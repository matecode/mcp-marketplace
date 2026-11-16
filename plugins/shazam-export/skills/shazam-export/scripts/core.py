"""Shazam snapshots, positional reconstruction and local export files."""
import csv
from collections import Counter
from datetime import datetime, timedelta, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import tempfile
from zoneinfo import ZoneInfo

PREFIX = 'com.shazam.android:id/'
FIELDS = ('title', 'artist', 'recognized_display')
CSV_FIELDS = ('position', 'timestamp', *FIELDS, 'section')
MONTHS = dict(zip(('Jan', 'Feb', 'März', 'Apr', 'Mai', 'Juni', 'Juli', 'Aug',
                   'Sept', 'Okt', 'Nov', 'Dez'), range(1, 13)))
MONTHS.update(dict(zip(('Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli',
                        'August', 'September', 'Oktober', 'November', 'Dezember'), range(1, 13))))


class Paused(RuntimeError):
    """A safe, content-free reason to retain a partial export."""


def atomic(path, data):
    path = Path(path)
    fd, temp = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def save_json(path, value):
    atomic(path, json.dumps(value, ensure_ascii=False, indent=2).encode())


def full(row):
    return all(row.get(f) for f in FIELDS)


def visible_list(nodes):
    if any(any(word in n.get('identifier', '').lower() for word in ('lockscreen', 'keyguard'))
           for n in nodes):
        raise Paused('device_locked')
    if not any(n.get('identifier') == 'android:id/list' for n in nodes):
        raise Paused('song_list_not_visible')
    if not any(n.get('identifier') == PREFIX + 'text_column' for n in nodes):
        raise Paused('unsupported_shazam_layout')


def slots(nodes):
    result, current, section = [], None, None
    for node in nodes:
        name = node.get('identifier', '').removeprefix(PREFIX)
        if name == 'label' and node.get('text'):
            section = node['text']
        if name == 'text_column':
            current = {'section': section}
            result.append(current)
        field = {'title': 'title', 'subtitle': 'artist', 'datetime': 'recognized_display'}.get(name)
        if current is not None and field and node.get('text'):
            current[field] = node['text']
    return result


def loading(nodes):
    groups, current = [], None
    for node in nodes:
        name = node.get('identifier', '').removeprefix(PREFIX)
        if name == 'text_column':
            current = {}
            groups.append(current)
        if current is not None and name in ('title', 'subtitle', 'datetime'):
            current[name] = node.get('text')
    return any(len(row) == 3 and not all(row.values()) for row in groups)


def merge(existing, batch):
    """Align positions using full rows, retaining incomplete slots and duplicates."""
    candidates = Counter()
    for j, row in enumerate(batch):
        if full(row):
            for i, old in enumerate(existing):
                if full(old) and all(old[f] == row[f] for f in FIELDS):
                    candidates[i - j] += 1
    valid = []
    for offset, score in candidates.items():
        if offset < 0 or offset > len(existing):
            continue
        if all(all(not old.get(f) or not row.get(f) or old[f] == row[f] for f in FIELDS)
               for j, row in enumerate(batch) if offset + j < len(existing)
               for old in [existing[offset + j]]):
            valid.append((score, offset))
    if not valid:
        raise Paused('no_positional_overlap')
    best_score = max(score for score, _ in valid)
    best = [offset for score, offset in valid if score == best_score]
    if len(best) != 1:
        raise Paused('ambiguous_positional_overlap')
    offset = best[0]
    for j, row in enumerate(batch):
        if offset + j == len(existing):
            existing.append(dict(row))
        else:
            existing[offset + j].update({f: value for f, value in row.items() if value})
    section = None
    for row in existing:
        section = row.get('section') or section
        row['section'] = section
    return offset


def expected_count(nodes):
    node = next((n for n in nodes if n.get('identifier') == PREFIX + 'list_subtitle'), None)
    if not node or not re.fullmatch(r'[\d.,\s]+\s+\S.*', node.get('text', '')):
        raise Paused('start_at_top_of_song_list')
    count = int(re.sub(r'\D', '', node['text']))
    if count <= 0:
        raise Paused('empty_or_unsupported_song_count')
    return count


def gesture(nodes, direction='up', fraction=0.55):
    """Use fresh list bounds, away from the expanding fast-scroll overlay."""
    visible_list(nodes)
    bounds = next(n['coordinates'] for n in nodes if n.get('identifier') == 'android:id/list')
    left, top, width, height = (bounds[k] for k in ('x', 'y', 'width', 'height'))
    overlay = next((n['coordinates']['x'] for n in nodes
                    if n.get('identifier') == PREFIX + 'fast_scroll_container'), left + width)
    available = min(left + width, overlay) - left
    if available < 80 or height < 200:
        raise Paused('no_safe_scroll_area')
    return {'direction': direction, 'x': int(left + min(width * 0.23, available / 2)),
            'y': int(top + height * (0.88 if direction == 'up' else 0.12)),
            'distance': max(40, int(height * fraction))}


def offset_zone(value):
    match = re.fullmatch(r'([+-])(\d{2}):(\d{2})', value or '')
    if not match:
        raise ValueError('Offset must use +HH:MM or -HH:MM')
    sign, hour, minute = match.groups()
    if int(hour) > 14 or int(minute) > 59 or (int(hour) == 14 and int(minute)):
        raise ValueError('Invalid timezone offset')
    delta = timedelta(hours=int(hour), minutes=int(minute))
    return timezone(delta if sign == '+' else -delta)


def timestamp(row, reference_date, offset=None, zone=None):
    if not row.get('recognized_display'):
        return None
    match = re.fullmatch(r'(\d{1,2}) ([A-Za-zäöüÄÖÜ]+)\.?, (\d{2}):(\d{2})', row['recognized_display'])
    if not match:
        raise ValueError('Unsupported recognition date format')
    day, month_name, hour, minute = match.groups()
    month = MONTHS[month_name]
    section = row.get('section') or ''
    absolute = re.fullmatch(r'([A-Za-zäöüÄÖÜ]+) (\d{4})', section)
    reference = datetime.fromisoformat(reference_date).date()
    if absolute:
        name, year = absolute.groups()
        if MONTHS[name] != month:
            raise ValueError('Recognition date and section disagree')
        year = int(year)
    else:
        year = reference.year - ((month, int(day)) > (reference.month, reference.day))
        date = datetime(year, month, int(day)).date()
        age = (reference - date).days
        allowed = {'Heute': (0, 0), 'Gestern': (1, 1), 'Diese Woche': (0, 7),
                   'Letzte Woche': (1, 14)}
        if section not in allowed or not allowed[section][0] <= age <= allowed[section][1]:
            raise ValueError('Cannot resolve relative date section')
    value = datetime(year, month, int(day), int(hour), int(minute))
    if offset:
        value = value.replace(tzinfo=offset_zone(offset))
    elif zone:
        tz = ZoneInfo(zone)
        candidates = set()
        for fold in (0, 1):
            aware = value.replace(tzinfo=tz, fold=fold)
            if aware.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None) == value:
                candidates.add(aware.isoformat(timespec='minutes'))
        if len(candidates) != 1:
            raise ValueError('Local time is ambiguous or absent during DST transition; specify a fixed offset')
        return candidates.pop()
    return value.isoformat(timespec='minutes')


def write_outputs(directory, records, metadata):
    rows = []
    for i, row in enumerate(records):
        try:
            value = timestamp(row, metadata['reference_date'], metadata.get('offset'), metadata.get('zone'))
        except (ValueError, KeyError):
            if metadata.get('complete'):
                raise
            value = None
        rows.append({**row, 'position': i + 1, 'timestamp': value})
    result = {**metadata, 'rows': rows, 'captured_count': sum(full(r) for r in records),
              'date_note': 'Minute precision; year inferred from sections and reference_date. '
                           'Timezone, if configured, is an explicit assumption. Original display retained.'}
    json_bytes = json.dumps(result, ensure_ascii=False, indent=2).encode()
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=CSV_FIELDS)
    writer.writeheader()
    writer.writerows({f: row.get(f) for f in CSV_FIELDS} for row in rows)
    csv_bytes = stream.getvalue().encode('utf-8-sig')
    # Build both outputs before replacing either one; verification detects interrupted pairs.
    atomic(directory / 'shazam-export.json', json_bytes)
    atomic(directory / 'shazam-export.csv', csv_bytes)
    save_json(directory / 'verification.json', {
        'complete': bool(metadata.get('complete')), 'rows': len(rows),
        'captured': sum(full(r) for r in records),
        'expected': metadata.get('expected_count'),
        'files': {name: hashlib.sha256(data).hexdigest() for name, data in
                  [('shazam-export.json', json_bytes), ('shazam-export.csv', csv_bytes)]},
    })


def verify(directory):
    proof = json.loads((directory / 'verification.json').read_text())
    if set(proof['files']) != {'shazam-export.json', 'shazam-export.csv'}:
        raise ValueError('Both output hashes are required')
    for name, digest in proof['files'].items():
        if name not in ('shazam-export.json', 'shazam-export.csv'):
            raise ValueError('Unsupported verification file')
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != digest:
            raise ValueError('Output hash mismatch')
    data = json.loads((directory / 'shazam-export.json').read_text())
    with (directory / 'shazam-export.csv').open(encoding='utf-8-sig', newline='') as handle:
        csv_rows = list(csv.DictReader(handle))
    rows = data['rows']
    if (proof['rows'] != len(rows) or proof['captured'] != sum(full(r) for r in rows)
            or proof['expected'] != data.get('expected_count')
            or proof['complete'] != bool(data.get('complete'))):
        raise ValueError('Verification metadata mismatch')
    if len(csv_rows) != len(rows) or [r['position'] for r in rows] != list(range(1, len(rows) + 1)):
        raise ValueError('Position or count mismatch')
    if not all(all(str(a.get(f) or '') == b.get(f, '') for f in CSV_FIELDS)
               for a, b in zip(rows, csv_rows)):
        raise ValueError('CSV/JSON mismatch')
    for row in rows:
        if row.get('timestamp') is not None:
            expected_time = timestamp(row, data['reference_date'], data.get('offset'), data.get('zone'))
            if row['timestamp'] != expected_time:
                raise ValueError('ISO timestamp disagrees with source date or time assumption')
    if data.get('complete') and not (all(full(r) and r.get('timestamp') for r in rows)
                                    and len(rows) == data['expected_count']):
        raise ValueError('Incomplete export marked complete')
    return {'complete': bool(data.get('complete')), 'captured': sum(full(r) for r in rows),
            'expected': data.get('expected_count'), 'csv_json_identical': True}
