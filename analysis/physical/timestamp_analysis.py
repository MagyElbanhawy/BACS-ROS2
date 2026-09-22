from __future__ import annotations

from typing import Iterable


def ns_to_seconds(value_ns: int | float) -> float:
    return float(value_ns) / 1e9


def duration_seconds(start_ns: int | float, end_ns: int | float) -> float:
    return ns_to_seconds(end_ns - start_ns)


def is_monotonic(values: Iterable[int | float]) -> bool:
    prev = None
    for value in values:
        if prev is not None and value < prev:
            return False
        prev = value
    return True
