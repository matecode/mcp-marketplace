"""Synthetic behavior tests; never include real songs or device identifiers."""
import copy
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import subprocess
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / 'skills/shazam-export/scripts'
sys.path.insert(0, str(SCRIPTS))
import core
from device import Awake
from mobile import Mobile
spec = importlib.util.spec_from_file_location('export_cli', SCRIPTS / 'export.py')
cli = importlib.util.module_from_spec(spec)
sys.modules['export_cli'] = cli
spec.loader.exec_module(cli)


def row(name, date='16 Nov., 10:00', section='Heute'):
    return {'title': name, 'artist': 'Synthetic Artist', 'recognized_display': date, 'section': section}


def snapshot(rows, count=None, overlay=700):
    nodes = [{'identifier': 'android:id/list', 'coordinates': {'x': 0, 'y': 100, 'width': 1000, 'height': 1600}},
             {'identifier': core.PREFIX + 'fast_scroll_container', 'coordinates': {'x': overlay, 'y': 100, 'width': 1000-overlay, 'height': 1600}}]
    if count is not None:
        nodes.append({'identifier': core.PREFIX+'list_subtitle', 'text': f'{count} Songs'})
    for record in rows:
        if record.get('section'):
            nodes.append({'identifier': core.PREFIX+'label', 'text': record['section']})
        nodes.append({'identifier': core.PREFIX+'text_column'})
        for source, target in [('title', 'title'), ('artist', 'subtitle'), ('recognized_display', 'datetime')]:
            nodes.append({'identifier': core.PREFIX+target, 'text': record.get(source, '')})
    return nodes


class FakeAndroid:
    device = 'synthetic-device'
    def __init__(self): self.setting = '0'
    def reference_date(self): return '2026-11-16'
    def version(self): return 'synthetic-1'
    def shell(self, *args):
        if args[:2] == ('settings', 'get'): return self.setting
        if args[:2] == ('settings', 'put'): self.setting = args[-1]
        if args[:2] == ('settings', 'delete'): self.setting = 'null'
        if args[:2] == ('svc', 'power'): self.setting = '2'
        return ''


class FakeMobile:
    def __init__(self, frames): self.frames, self.calls = iter(frames), []
    def snapshot(self, device):
        item = next(self.frames)
        if isinstance(item, BaseException): raise item
        return copy.deepcopy(item)
    def call(self, name, args): self.calls.append((name, args)); return {}


def args(action='export'):
    return type('Args', (), {'action': action, 'device': 'synthetic-device',
        'offset': '+02:00', 'zone': None, 'max_pages': 30, 'no_keep_awake': False})()


class Reconstruction(unittest.TestCase):
    def test_loading_placeholder_is_a_position_and_can_be_filled(self):
        records = core.slots(snapshot([row('A'), {}, row('C')]))
        self.assertEqual(len(records), 3)
        self.assertTrue(core.loading(snapshot([row('A'), {}, row('C')])))
        core.merge(records, [row('A'), row('B'), row('C')])
        self.assertEqual([r['title'] for r in records], ['A', 'B', 'C'])

    def test_repeated_recognitions_are_not_deduplicated(self):
        records = [row('A'), row('B')]
        core.merge(records, [row('B'), row('B'), row('C')])
        self.assertEqual([r['title'] for r in records], ['A', 'B', 'B', 'C'])

    def test_missing_overlap_cannot_mutate_records(self):
        records = [row('A')]
        with self.assertRaises(core.Paused): core.merge(records, [row('X')])
        self.assertEqual(records, [row('A')])

    def test_ambiguous_duplicate_overlap_stops(self):
        with self.assertRaisesRegex(core.Paused, 'ambiguous'):
            core.merge([row('A'), row('A')], [row('A')])

    def test_clipped_row_fields_merge_into_existing_position(self):
        records = [row('A'), {'title': 'B', 'artist': 'Synthetic Artist'}]
        core.merge(records, [row('A'), row('B'), row('C')])
        self.assertEqual(len(records), 3)
        self.assertTrue(all(core.full(r) for r in records))

    def test_gesture_avoids_expanding_scroll_overlay(self):
        for overlay in (850, 400, 120):
            value = core.gesture(snapshot([row('A')], overlay=overlay))
            self.assertLess(value['x'], overlay)
            self.assertGreater(value['y']-value['distance'], 100)

    def test_lock_screen_wins_over_background_shazam_list(self):
        nodes = snapshot([row('A')])+[{'identifier': 'element:lockscreen'}]
        with self.assertRaisesRegex(core.Paused, 'locked'): core.visible_list(nodes)


class Dates(unittest.TestCase):
    def test_relative_year_boundary(self):
        value = core.timestamp(row('A', '31 Dez., 12:20', 'Letzte Woche'), '2026-01-05', '+02:00')
        self.assertEqual(value, '2025-12-31T12:20+02:00')

    def test_absolute_year_and_local_time_preserved(self):
        self.assertEqual(core.timestamp(row('A', '15 Sept., 07:57', 'September 2016'), '2026-11-16'),
                         '2016-09-15T07:57')

    def test_named_berlin_zone_observes_seasons(self):
        self.assertTrue(core.timestamp(row('A', '3 Feb., 12:30', 'Februar 2026'), '2026-11-16', zone='Europe/Berlin').endswith('+01:00'))
        self.assertTrue(core.timestamp(row('A', '3 Juli, 12:30', 'Juli 2026'), '2026-11-16', zone='Europe/Berlin').endswith('+02:00'))

    def test_dst_ambiguous_and_missing_times_require_offset(self):
        for date, section in [('25 Okt., 02:30', 'Oktober 2026'), ('29 März, 02:30', 'März 2026')]:
            with self.assertRaises(ValueError): core.timestamp(row('A', date, section), '2026-11-16', zone='Europe/Berlin')
            self.assertTrue(core.timestamp(row('A', date, section), '2026-11-16', '+02:00').endswith('+02:00'))

    def test_section_mismatch_and_unknown_year_do_not_guess(self):
        for section in ('Januar 2026', 'Unknown'):
            with self.assertRaises(ValueError): core.timestamp(row('A', section=section), '2026-11-16')


class Lifecycle(unittest.TestCase):
    @patch('export_cli.time.sleep', return_value=None)
    def test_complete_export_restores_display_and_matches_outputs(self, _):
        first = snapshot([row('A'), row('B')], 4)
        last = snapshot([row('B'), row('B'), row('C')])
        android = FakeAndroid(); mobile = FakeMobile([first, last, last, last])
        with tempfile.TemporaryDirectory() as folder:
            result = cli.collect(args(), Path(folder), mobile, android)
            self.assertTrue(result['complete'])
            self.assertEqual(result['captured'], 4)
            self.assertTrue(core.verify(Path(folder))['csv_json_identical'])
            self.assertEqual(android.setting, '0')
            self.assertTrue(json.loads((Path(folder)/'screen-state.json').read_text())['restored'])

    @patch('export_cli.time.sleep', return_value=None)
    def test_interrupt_and_resume_keep_original_reference_and_duplicates(self, _):
        android = FakeAndroid()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            with self.assertRaises(KeyboardInterrupt):
                cli.collect(args(), path, FakeMobile([snapshot([row('A'), row('B')], 3), KeyboardInterrupt()]), android)
            self.assertEqual(android.setting, '0')
            before = json.loads((path/'checkpoint.json').read_text())['metadata']['exported_at']
            last = snapshot([row('B'), row('B')])
            result = cli.collect(args('resume'), path, FakeMobile([last, last, last]), android)
            self.assertTrue(result['complete'])
            after = json.loads((path/'checkpoint.json').read_text())['metadata']['exported_at']
            self.assertEqual(before, after)

    @patch('export_cli.time.sleep', return_value=None)
    def test_list_end_with_gap_stays_partial(self, _):
        android = FakeAndroid(); frame = snapshot([row('A')], 2)
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(core.Paused, 'missing_positions'):
                cli.collect(args(), Path(folder), FakeMobile([frame, frame, frame]), android)
            self.assertFalse(core.verify(Path(folder))['complete'])
            self.assertEqual(android.setting, '0')

    def test_crashed_display_journal_recovers_without_overwriting_independent_change(self):
        android = FakeAndroid()
        with tempfile.TemporaryDirectory() as folder:
            guard = Awake(android, Path(folder)); guard.enable()
            android.setting = '3'
            with self.assertRaisesRegex(core.Paused, 'independently'): guard.restore()
            self.assertEqual(android.setting, '3')
            android.setting = '2'; Awake(android, Path(folder)).restore()
            self.assertEqual(android.setting, '0')

    def test_mismatching_resume_device_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            core.save_json(path/'checkpoint.json', {'schema': 1, 'device_sha256': 'wrong'})
            with self.assertRaisesRegex(core.Paused, 'mismatch'):
                cli.collect(args('resume'), path, FakeMobile([]), FakeAndroid())

    def test_output_tampering_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            core.write_outputs(path, [row('A, "quoted"')], {'reference_date': '2026-11-16', 'expected_count': 1, 'complete': True})
            self.assertTrue(core.verify(path)['complete'])
            (path/'shazam-export.csv').write_text('changed')
            with self.assertRaisesRegex(ValueError, 'hash'): core.verify(path)

    def test_invalid_iso_rejected_even_when_both_files_and_hashes_agree(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            core.write_outputs(path, [row('A')], {'reference_date': '2026-11-16', 'expected_count': 1, 'complete': True})
            for name in ('shazam-export.csv', 'shazam-export.json'):
                file = path / name
                file.write_bytes(file.read_bytes().replace(b'2026-11-16T10:00', b'invalid-timestamp'))
            proof = json.loads((path/'verification.json').read_text())
            proof['files'] = {name: hashlib.sha256((path/name).read_bytes()).hexdigest() for name in proof['files']}
            core.save_json(path/'verification.json', proof)
            with self.assertRaisesRegex(ValueError, 'timestamp'): core.verify(path)

    def test_conversion_requires_reference_date_and_keeps_source(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder); source = path/'source.json'
            core.save_json(source, {'rows': [row('A')], 'complete': True, 'expected_count': 1})
            before = source.read_bytes()
            command = [sys.executable, str(SCRIPTS/'export.py'), 'convert', '--input', str(source),
                       '--output', str(path/'converted'), '--offset', '+02:00']
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((path/'converted/shazam-export.json').exists())
            result = subprocess.run(command+['--reference-date', '2026-11-16'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertTrue(core.verify(path/'converted')['complete'])
            self.assertEqual(source.read_bytes(), before)


class Stdio(unittest.TestCase):
    def test_real_subprocess_transport_and_tool_error(self):
        server = '''import json, os, sys
for line in sys.stdin:
    request = json.loads(line)
    if 'id' not in request: continue
    if request['method'] == 'initialize':
        result = {'serverInfo': {'name': 'synthetic', 'version': '1'}, 'capabilities': {}}
    elif request['params']['name'] == 'mobile_list_available_devices':
        assert os.environ['MOBILEMCP_DISABLE_TELEMETRY'] == '1'
        assert os.environ['MOBILEWRIGHT_DISABLE_TELEMETRY'] == '1'
        result = {'content': [{'type': 'text', 'text': json.dumps({'devices': [{'id': 'synthetic', 'platform': 'android'}]})}]}
    elif request['params']['name'] == 'mobile_list_elements_on_screen':
        result = {'content': [{'type': 'text', 'text': 'Screen elements: []'}]}
    else: result = {'isError': True, 'content': [{'type': 'text', 'text': 'PRIVATE-SYNTHETIC-ERROR'}]}
    print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
'''
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder); script = path/'server.py'; script.write_text(server)
            mobile = Mobile({'command': sys.executable, 'args': [str(script)],
                             'env': {'MOBILEMCP_DISABLE_TELEMETRY': '0'}}, path)
            try:
                self.assertEqual(mobile.devices()[0]['id'], 'synthetic')
                self.assertEqual(mobile.snapshot('synthetic'), [])
                with self.assertRaisesRegex(core.Paused, '^mobile_tool_failed$'):
                    mobile.call('synthetic_error', {})
            finally:
                mobile.close()
            self.assertIsNotNone(mobile.proc.poll())


if __name__ == '__main__': unittest.main()
