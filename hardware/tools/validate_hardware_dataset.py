#!/usr/bin/env python3
"""Validate the raw BACS hardware evidence without modifying it."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = ROOT / 'hardware' / 'raw' / 'BACS_v10_raw'
METADATA_CSV = RAW_ROOT / 'experiment_results' / 'metadata' / 'session_manifest.csv'
FILE_INDEX = RAW_ROOT / 'derived' / 'raw_file_index.csv'
EXPECTED_TOPICS = [
    '/vicon/limo01/pose',
    '/vicon/limo02/pose',
    '/odom/limo01',
    '/odom/limo02',
    '/scan/limo01',
    '/scan/limo02',
    '/tf',
    '/bacs/scheduler',
]
EXPECTED_VICON_HEADER = ['timestamp_ns', 'x', 'y', 'z', 'roll_rad', 'pitch_rad', 'yaw_rad', 'vx', 'vy', 'vz']
EXPECTED_SCHEDULER_HEADER = ['session', 'run', 'seq', 'policy', 'robot', 't_gen_ns', 't_selected_ns', 't_tx_ns', 't_rx_ns', 'deferral_ns', 'channel', 'rssi_dbm', 'snr_db', 'payload_hex']


@dataclass
class CheckResult:
    passed: bool
    details: List[str]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def read_csv_rows(path: Path) -> List[Dict[str, str]]:
    with open(path, 'r', newline='') as f:
        return list(csv.DictReader(f))


def validate_hash_index() -> CheckResult:
    result = CheckResult(passed=True, details=[])
    if not FILE_INDEX.exists():
        result.passed = False
        result.details.append('Missing derived/raw_file_index.csv')
        return result
    expected: Dict[str, str] = {}
    with open(FILE_INDEX, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            expected[row['relative_path']] = row['sha256']
    for path in sorted(RAW_ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(RAW_ROOT).as_posix()
        if rel == 'derived/raw_file_index.csv':
            continue
        if rel.startswith('logs/') or rel.startswith('derived/'):
            continue
        actual = sha256_file(path)
        if rel in expected and actual != expected[rel]:
            result.passed = False
            result.details.append(f'Checksum mismatch for {rel}: expected {expected[rel]} got {actual}')
        if rel not in expected:
            result.details.append(f'File {rel} present but missing from raw_file_index.csv')
            result.passed = False
    return result


def validate_session_manifest() -> Tuple[CheckResult, List[Dict[str, str]]]:
    result = CheckResult(passed=True, details=[])
    rows: List[Dict[str, str]] = []
    if not METADATA_CSV.exists():
        result.passed = False
        result.details.append('Missing metadata/session_manifest.csv')
        return result, rows
    with open(METADATA_CSV, 'r', newline='') as f:
        rows = list(csv.DictReader(f))
    required = {'session_id', 'policy', 'ros_acquisition_start_utc', 'ros_acquisition_end_utc', 'duration_sec', 'n_runs', 'robots'}
    if not required.issubset(rows[0].keys()):
        result.passed = False
        result.details.append('session_manifest.csv is missing required columns')
        return result, rows
    seen = set()
    for row in rows:
        sid = row['session_id']
        if sid in seen:
            result.passed = False
            result.details.append(f'Duplicate session entry in manifest: {sid}')
        seen.add(sid)
        expected_files = [
            f'experiment_results/vicon_logs/vicon_ground_truth_{sid}_limo01_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}.csv',
            f'experiment_results/vicon_logs/vicon_ground_truth_{sid}_limo02_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}.csv',
            f'experiment_results/bacs_logs/bacs_scheduler_log_{sid}_{row["policy"]}_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}.csv',
        ]
        # session names already map to bag directories; only check basic existence and semantics.
        for p in expected_files:
            full = RAW_ROOT / p
            if not full.exists():
                result.passed = False
                result.details.append(f'Missing expected file: {p}')
    return result, rows


def validate_vicon_csv(path: Path, sid: str, robot: str) -> CheckResult:
    result = CheckResult(passed=True, details=[])
    if not path.exists():
        result.passed = False
        result.details.append(f'Missing Vicon CSV: {path}')
        return result
    with open(path, 'r', newline='') as f:
        rows = list(csv.reader(f))
    if len(rows) < 2:
        result.passed = False
        result.details.append(f'Vicon file has no data rows: {path.name}')
        return result
    header = rows[0]
    if header != EXPECTED_VICON_HEADER:
        result.passed = False
        result.details.append(f'Unexpected Vicon header in {path.name}: {header}')
    try:
        timestamps = [int(r[0]) for r in rows[1:] if len(r) >= 10]
    except ValueError:
        result.passed = False
        result.details.append(f'Non-numeric timestamps in Vicon CSV: {path.name}')
        return result
    if len(timestamps) == 0:
        result.passed = False
        result.details.append(f'No numeric timestamps in Vicon CSV: {path.name}')
        return result
    if not all(b >= a for a, b in zip(timestamps, timestamps[1:])):
        result.passed = False
        result.details.append(f'Non-monotonic Vicon timestamps: {path.name}')
    if sid not in path.name:
        result.passed = False
        result.details.append(f'Session mismatch in Vicon filename: {path.name}')
    if robot not in path.name:
        result.passed = False
        result.details.append(f'Robot mismatch in Vicon filename: {path.name}')
    return result


def validate_scheduler_csv(path: Path) -> CheckResult:
    result = CheckResult(passed=True, details=[])
    if not path.exists():
        result.passed = False
        result.details.append(f'Missing scheduler CSV: {path}')
        return result
    with open(path, 'r', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    if len(rows) < 2:
        result.passed = False
        result.details.append(f'No scheduler data in {path.name}')
        return result
    header = rows[0]
    if header != EXPECTED_SCHEDULER_HEADER:
        result.passed = False
        result.details.append(f'Unexpected scheduler header in {path.name}: {header}')
    data_rows = rows[1:]
    if not data_rows:
        result.passed = False
        result.details.append(f'No scheduler events in {path.name}')
    for i, row in enumerate(data_rows[:3], start=1):
        if len(row) != len(EXPECTED_SCHEDULER_HEADER):
            result.passed = False
            result.details.append(f'Bad row length in {path.name} at line {i+1}: {len(row)} != {len(EXPECTED_SCHEDULER_HEADER)}')
            break
    if len(data_rows) > 0:
        generation_times = [int(r[5]) for r in data_rows if len(r) >= 6]
        if generation_times and not all(b >= a for a, b in zip(generation_times, generation_times[1:])):
            result.passed = False
            result.details.append(f'Non-monotonic generation timestamps in {path.name}')
    return result


def validate_bag_db3(path: Path) -> CheckResult:
    result = CheckResult(passed=True, details=[])
    if not path.exists():
        result.passed = False
        result.details.append(f'Missing bag DB3: {path}')
        return result
    try:
        con = sqlite3.connect(str(path))
    except sqlite3.DatabaseError as exc:
        result.passed = False
        result.details.append(f'Unable to open DB3: {path}: {exc}')
        return result
    with con:
        tables = con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
        table_names = {r[0] for r in tables}
        required_tables = {'messages', 'topics', 'metadata', 'schema'}
        missing = required_tables - table_names
        if missing:
            result.passed = False
            result.details.append(f'Missing DB3 tables in {path.name}: {sorted(missing)}')
        topics = con.execute('SELECT name, type FROM topics ORDER BY id').fetchall()
        topic_names = [r[0] for r in topics]
        for name in EXPECTED_TOPICS:
            if name not in topic_names:
                result.passed = False
                result.details.append(f'Missing topic in {path.name}: {name}')
        msg_count = con.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
        if msg_count != 238320:
            result.passed = False
            result.details.append(f'Unexpected DB3 message count in {path.name}: {msg_count}')
        ts = con.execute('SELECT MIN(timestamp), MAX(timestamp), COUNT(*) FROM messages').fetchone()
        min_ts, max_ts, count = ts
        if count != 238320:
            result.passed = False
            result.details.append(f'Count mismatch in DB3 {path.name}: {count}')
        timestamps = [int(r[0]) for r in con.execute('SELECT timestamp FROM messages ORDER BY timestamp')]
        if timestamps and any(b < a for a, b in zip(timestamps, timestamps[1:])):
            result.passed = False
            result.details.append(f'Non-monotonic message timestamps in {path.name}')
        topic_count = con.execute('SELECT topic_id, COUNT(*) FROM messages GROUP BY topic_id ORDER BY topic_id').fetchall()
        expected_counts = {
            1: 72000,
            2: 72000,
            3: 36000,
            4: 36000,
            5: 3600,
            6: 3600,
            7: 14400,
            8: 720,
        }
        for topic_id, count in topic_count:
            if topic_id in expected_counts and count != expected_counts[topic_id]:
                result.passed = False
                result.details.append(f'Unexpected count for DB3 topic {topic_id} in {path.name}: {count}')
    con.close()
    return result


def validate_duplicate_payload_streams() -> CheckResult:
    result = CheckResult(passed=True, details=[])
    payload_hashes: Dict[str, str] = {}
    for path in sorted((RAW_ROOT / 'experiment_results' / 'bacs_logs').glob('*.csv')):
        rows = read_csv_rows(path)
        payload_sequence = ''.join(r['payload_hex'] for r in rows)
        stream_hash = hashlib.sha256(payload_sequence.encode('utf-8')).hexdigest()
        payload_hashes[path.name] = stream_hash
    seen: Dict[str, str] = {}
    for name, h in payload_hashes.items():
        if h in seen:
            result.passed = False
            result.details.append(f'Duplicate scheduler payload stream detected: {seen[h]} and {name}')
        seen[h] = name
    return result


def validate_manifest_files() -> CheckResult:
    result = CheckResult(passed=True, details=[])
    manifest_rows = read_csv_rows(METADATA_CSV)
    for row in manifest_rows:
        sid = row['session_id']
        bag_db3 = RAW_ROOT / 'experiment_results' / 'rosbags' / f'{sid}_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}_db3' / f'{sid}_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}_db3.db3'
        if not bag_db3.exists():
            result.passed = False
            result.details.append(f'Manifest references missing bag DB3: {bag_db3}')
        bag_mcap = RAW_ROOT / 'experiment_results' / 'rosbags' / f'{sid}_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}_mcap' / f'{sid}_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}_mcap.mcap'
        if not bag_mcap.exists():
            result.passed = False
            result.details.append(f'Manifest references missing bag MCAP: {bag_mcap}')
        scheduler = RAW_ROOT / 'experiment_results' / 'bacs_logs' / f'bacs_scheduler_log_{sid}_{row["policy"]}_{row["ros_acquisition_start_utc"][0:10].replace("-", "")}_{row["ros_acquisition_start_utc"][11:19].replace(":", "")}.csv'
        if not scheduler.exists():
            result.passed = False
            result.details.append(f'Manifest references missing scheduler CSV: {scheduler}')
    return result


def generate_json_report() -> Dict[str, Any]:
    generated = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    report: Dict[str, Any] = {
        'generated_at_utc': generated,
        'source_root': str(RAW_ROOT),
        'status': 'pass',
        'issues': [],
        'checks': {},
    }

    checks = [
        ('sha256_index', validate_hash_index()),
        ('session_manifest', validate_session_manifest()[0]),
        ('manifest_files', validate_manifest_files()),
        ('duplicate_payload_streams', validate_duplicate_payload_streams()),
    ]
    for name, check in checks:
        report['checks'][name] = {'passed': check.passed, 'details': check.details}
        report['issues'].extend([f'[{name}] {d}' for d in check.details])
    for bag in sorted((RAW_ROOT / 'experiment_results' / 'rosbags').glob('*_db3/*.db3')):
        result = validate_bag_db3(bag)
        report['checks'][f'bag::{bag.name}'] = {'passed': result.passed, 'details': result.details}
        report['issues'].extend([f'[bag::{bag.name}] {d}' for d in result.details])
    for file_path in sorted((RAW_ROOT / 'experiment_results' / 'vicon_logs').glob('*.csv')):
        sid = file_path.name.split('_')[3] if len(file_path.name.split('_')) >= 4 else 'UNKNOWN'
        robot = 'limo01' if 'limo01' in file_path.name else 'limo02'
        result = validate_vicon_csv(file_path, sid, robot)
        report['checks'][f'vicon::{file_path.name}'] = {'passed': result.passed, 'details': result.details}
        report['issues'].extend([f'[vicon::{file_path.name}] {d}' for d in result.details])
    for file_path in sorted((RAW_ROOT / 'experiment_results' / 'bacs_logs').glob('*.csv')):
        result = validate_scheduler_csv(file_path)
        report['checks'][f'scheduler::{file_path.name}'] = {'passed': result.passed, 'details': result.details}
        report['issues'].extend([f'[scheduler::{file_path.name}] {d}' for d in result.details])

    report['status'] = 'fail' if report['issues'] else 'pass'
    return report


def format_markdown(report: Dict[str, Any]) -> str:
    lines = [
        '# Hardware validation report',
        '',
        f'- generated_at_utc: {report["generated_at_utc"]}',
        f'- overall_status: {report["status"]}',
        '',
        '## Checks',
        '',
    ]
    for key, value in report['checks'].items():
        status = 'PASS' if value['passed'] else 'FAIL'
        lines.append(f'### {key}: {status}')
        for detail in value['details']:
            lines.append(f'- {detail}')
        lines.append('')
    if report['issues']:
        lines.append('## Issues')
        lines.append('')
        for issue in report['issues']:
            lines.append(f'- {issue}')
    else:
        lines.append('## Issues')
        lines.append('')
        lines.append('No issues detected.')
    return '\n'.join(lines) + '\n'


def main() -> int:
    report = generate_json_report()
    out_json = ROOT / 'hardware' / 'validation_report.json'
    out_md = ROOT / 'hardware' / 'validation_report.md'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    with open(out_md, 'w', encoding='utf-8') as f:
        f.write(format_markdown(report))
    print(json.dumps({'status': report['status'], 'issues': len(report['issues'])}, indent=2))
    return 0 if report['status'] == 'pass' else 1


if __name__ == '__main__':
    raise SystemExit(main())
