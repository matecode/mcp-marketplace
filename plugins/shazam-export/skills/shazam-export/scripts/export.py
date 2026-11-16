#!/usr/bin/env python3
"""Private Shazam export, resume, probe, verification and ISO conversion."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import time
from zoneinfo import ZoneInfo

from core import (PREFIX, FIELDS, Paused, expected_count, full, gesture, loading,
                  merge, offset_zone, save_json, slots, verify, visible_list, write_outputs)
from device import Android, Awake, fingerprint
from mobile import Mobile, launch_config


def progress(**value):
    print(json.dumps(value), flush=True)


class Lock:
    def __init__(self, directory):
        self.path = directory / 'run.lock'

    def __enter__(self):
        try:
            fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            # A dead process can leave a lock after SIGKILL. Do not remove a live lock.
            pid = int(self.path.read_text())
            if pid <= 0:
                raise Paused('invalid_run_lock')
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                self.path.unlink()
                return self.__enter__()
            raise Paused('export_already_running') from None
        with os.fdopen(fd, 'w') as handle:
            handle.write(str(os.getpid()))
        return self

    def __exit__(self, *args):
        self.path.unlink(missing_ok=True)


def private_directory(value):
    path = Path(value).expanduser().resolve()
    plugin = Path(__file__).resolve().parents[3]
    if path.is_relative_to(plugin):
        raise ValueError('Output must be outside the installed plugin')
    if any((parent / '.git').exists() for parent in (path, *path.parents)):
        raise ValueError('Output must be outside Git repositories')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def choose(devices, identifier):
    selected = [d for d in devices if d.get('id') == identifier and d.get('platform') == 'android']
    if len(selected) != 1:
        raise Paused('selected_android_device_unavailable')
    return selected[0]


def read_snapshot(mobile, device):
    for _ in range(6):
        nodes = mobile.snapshot(device)
        visible_list(nodes)
        if not loading(nodes):
            if not any(full(r) for r in slots(nodes)):
                raise Paused('no_complete_song_rows')
            return nodes
        time.sleep(1)
    raise Paused('song_rows_still_loading')


def collect(args, directory, mobile, android):
    state_path = directory / 'checkpoint.json'
    if args.action == 'resume':
        state = json.loads(state_path.read_text())
        if state['schema'] != 1 or state['device_sha256'] != fingerprint(args.device):
            raise Paused('checkpoint_device_or_schema_mismatch')
        if state['metadata']['complete']:
            return verify(directory)
        if state['metadata']['reference_date'] != android.reference_date():
            raise Paused('device_date_changed_since_checkpoint')
        if state['app_version'] != android.version():
            raise Paused('shazam_version_changed_since_checkpoint')
        records, metadata = state['rows'], state['metadata']
    else:
        if state_path.exists() or (directory / 'shazam-export.json').exists():
            raise Paused('output_already_exists_use_resume_or_new_directory')
        records = []
        metadata = {'source': 'Shazam Android via Mobile MCP', 'complete': False,
                    'exported_at': datetime.now(timezone.utc).isoformat(),
                    'reference_date': android.reference_date(), 'offset': args.offset,
                    'zone': args.zone, 'expected_count': None, 'snapshot_count': 0}
        state = {'schema': 1, 'device_sha256': fingerprint(args.device),
                 'app_version': android.version(), 'metadata': metadata, 'rows': records}
    captures = directory / 'snapshots'
    captures.mkdir(exist_ok=True, mode=0o700)
    awake = Awake(android, directory)

    def persist():
        metadata['captured_count'] = sum(full(row) for row in records)
        save_json(state_path, state)
        write_outputs(directory, records, metadata)

    unchanged, last, recoveries = 0, None, 0
    try:
        if not args.no_keep_awake:
            awake.enable()
        else:
            awake.restore()
        for page in range(args.max_pages):
            nodes = read_snapshot(mobile, args.device)
            batch = slots(nodes)
            if not records:
                metadata['expected_count'] = expected_count(nodes)
                records.extend(batch)
            else:
                top_count = next((n for n in nodes if n.get('identifier') == PREFIX + 'list_subtitle'), None)
                if top_count and expected_count(nodes) != metadata['expected_count']:
                    raise Paused('song_count_changed')
                try:
                    merge(records, batch)
                except Paused as error:
                    if str(error) != 'no_positional_overlap' or recoveries >= 8:
                        raise
                    recoveries += 1
                    # A bounded return toward already captured rows; no unaligned batch is saved.
                    mobile.call('mobile_swipe_on_screen', {'device': args.device,
                                **gesture(nodes, 'down', 0.15)})
                    time.sleep(0.7)
                    continue
            recoveries = 0
            expected = metadata['expected_count']
            if len(records) > expected:
                raise Paused('more_positions_than_reported_by_shazam')
            count = metadata['snapshot_count']
            safe = [n for n in nodes if n.get('identifier', '').startswith(PREFIX)]
            save_json(captures / f'{count:06d}.json', safe)
            metadata['snapshot_count'] += 1
            current = [tuple(r.get(f) for f in FIELDS) for r in batch]
            unchanged = unchanged + 1 if current == last else 0
            last = current
            captured = sum(full(row) for row in records)
            if unchanged >= 2:
                if captured != expected or len(records) != expected:
                    raise Paused('list_end_with_missing_positions')
                metadata['complete'] = True
                metadata.pop('pause_reason', None)
                persist()
                return verify(directory)
            if page % 5 == 0:
                persist()
                progress(captured=captured, expected=expected, complete=False)
            mobile.call('mobile_swipe_on_screen', {'device': args.device, **gesture(nodes)})
            time.sleep(0.7)
        raise Paused('page_limit_reached')
    except BaseException as error:
        metadata['complete'] = False
        metadata['pause_reason'] = str(error) if isinstance(error, Paused) else 'interrupted_or_invalid_data'
        persist()
        raise
    finally:
        awake.restore()


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['devices', 'probe', 'export', 'resume', 'verify', 'convert', 'restore-display'])
    parser.add_argument('--output', required=True, help='Private directory outside the plugin')
    parser.add_argument('--mcp-launch', help='Private JSON command/args/env/cwd for the original Mobile MCP')
    parser.add_argument('--device', help='Explicit identifier from the private device inventory')
    parser.add_argument('--adb', default=shutil.which('adb') or 'adb')
    parser.add_argument('--input', help='Existing Shazam export JSON, for convert')
    parser.add_argument('--reference-date', help='YYYY-MM-DD of the original displayed capture')
    tz = parser.add_mutually_exclusive_group()
    tz.add_argument('--offset', help='Explicit fixed offset, e.g. +02:00')
    tz.add_argument('--zone', help='Explicit IANA zone, e.g. Europe/Berlin')
    parser.add_argument('--no-keep-awake', action='store_true')
    parser.add_argument('--max-pages', type=int, default=2000)
    args = parser.parse_args()
    mobile = None
    try:
        if args.offset:
            offset_zone(args.offset)
        if args.zone:
            ZoneInfo(args.zone)
        if args.max_pages <= 0:
            raise ValueError('Invalid page limit')
        directory = private_directory(args.output)
        with Lock(directory):
            if args.action == 'verify':
                progress(**verify(directory))
                return 0
            if args.action == 'convert':
                if not args.input or (directory / 'shazam-export.json').exists():
                    raise ValueError('Conversion requires an input and a fresh output directory')
                data = json.loads(Path(args.input).read_text())
                rows = data.pop('rows')
                data['reference_date'] = args.reference_date or data.get('reference_date')
                if not data['reference_date']:
                    raise ValueError('Conversion requires the original device reference date')
                data['offset'], data['zone'] = args.offset, args.zone
                data.setdefault('expected_count', len(rows))
                data.setdefault('complete', False)
                write_outputs(directory, rows, data)
                progress(**verify(directory))
                return 0
            if args.action != 'devices' and not args.device:
                raise ValueError('An explicit device is required')
            if args.action == 'restore-display':
                Awake(Android(args.adb, args.device), directory).restore()
                progress(display_restored=True)
                return 0
            if not args.mcp_launch:
                raise ValueError('A private MCP launch configuration is required')
            mobile = Mobile(launch_config(args.mcp_launch), directory)
            devices = mobile.devices()
            if args.action == 'devices':
                save_json(directory / 'devices.json', devices)
                progress(android_devices=sum(d.get('platform') == 'android' for d in devices),
                         inventory_file='devices.json')
                return 0
            choose(devices, args.device)
            android = Android(args.adb, args.device)
            if args.action == 'probe':
                nodes = read_snapshot(mobile, args.device)
                save_json(directory / 'probe.json', [n for n in nodes if n.get('identifier', '').startswith(PREFIX)])
                progress(song_list_visible=True, complete_visible_rows=sum(full(r) for r in slots(nodes)),
                         shazam_version=android.version())
                return 0
            progress(**collect(args, directory, mobile, android))
            return 0
    except Paused as error:
        progress(complete=False, pause_reason=str(error))
        return 2
    except KeyboardInterrupt:
        progress(complete=False, pause_reason='interrupted')
        return 130
    except Exception:
        progress(complete=False, pause_reason='invalid_input_or_runtime')
        return 2
    finally:
        if mobile:
            mobile.close()


if __name__ == '__main__':
    raise SystemExit(main())
