from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

import numpy as np


def compute_map_alignment_rmse(est_points: Sequence[Sequence[float]], ref_points: Sequence[Sequence[float]]) -> float:
    if len(est_points) != len(ref_points) or len(est_points) == 0:
        raise ValueError('estimated and reference point sets must have equal length and be non-empty')
    est = np.asarray(est_points, dtype=float)
    ref = np.asarray(ref_points, dtype=float)
    est_center = est.mean(axis=0)
    ref_center = ref.mean(axis=0)
    est_c = est - est_center
    ref_c = ref - ref_center
    h = est_c.T @ ref_c
    u, _, vt = np.linalg.svd(h)
    r = vt.T @ u.T
    if np.linalg.det(r) < 0:
        vt[-1, :] *= -1
        r = vt.T @ u.T
    aligned = est_c @ r + ref_center
    errors = np.linalg.norm(aligned - ref, axis=1)
    return float(np.sqrt(np.mean(errors ** 2)))
