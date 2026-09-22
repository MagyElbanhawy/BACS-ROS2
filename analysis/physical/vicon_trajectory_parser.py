from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List


def read_vicon_csv(path: str | Path) -> List[Dict[str, float | int]]:
    records: List[Dict[str, float | int]] = []
    with open(path, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            record = {key: (int(value) if key == 'timestamp_ns' else float(value)) for key, value in row.items()}
            records.append(record)
    return records


def pose_series(path: str | Path) -> List[tuple[int, float, float, float, float]]:
    series: List[tuple[int, float, float, float, float]] = []
    for row in read_vicon_csv(path):
        timestamp_ns = int(row['timestamp_ns'])
        x = float(row['x'])
        y = float(row['y'])
        z = float(row['z'])
        yaw = float(row['yaw_rad'])
        series.append((timestamp_ns, x, y, z, yaw))
    return series
