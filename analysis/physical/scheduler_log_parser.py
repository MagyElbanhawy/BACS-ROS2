from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


def read_scheduler_log(path: str | Path) -> List[Dict[str, str]]:
    records: List[Dict[str, str]] = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))
    return records


def summarize_policy_events(path: str | Path) -> Dict[str, float | int]:
    rows = read_scheduler_log(path)
    if not rows:
        return {'n_events': 0, 'mean_deferral_ns': 0.0}
    deferrals = [int(r['deferral_ns']) for r in rows]
    return {
        'n_events': len(rows),
        'mean_deferral_ns': sum(deferrals) / len(deferrals),
        'median_deferral_ns': sorted(deferrals)[len(deferrals) // 2],
        'max_deferral_ns': max(deferrals),
    }
