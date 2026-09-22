from __future__ import annotations

import math
from typing import Sequence


def compute_pose_rmse(estimated: Sequence[float], reference: Sequence[float]) -> float:
    if len(estimated) != len(reference):
        raise ValueError('estimated and reference sequences must have the same length')
    if len(estimated) == 0:
        return 0.0
    squared = 0.0
    for e, r in zip(estimated, reference):
        squared += (e - r) ** 2
    return math.sqrt(squared / len(estimated))
