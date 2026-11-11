"""
Mean-shift guard.

Fires when |mean(new) - mean(reference)| > sigma * std(reference).
This catches cases where the distribution's shape is similar but it has
slipped (e.g. small uniform shift that KS doesn't flag).
"""
from __future__ import annotations

import numpy as np


def mean_shift_sigma(reference: np.ndarray, new: np.ndarray) -> float:
    """Signed shift in reference-sigma units. Returns inf if reference std == 0."""
    ref = np.asarray(reference, dtype=float).ravel()
    cur = np.asarray(new, dtype=float).ravel()
    if ref.size == 0 or cur.size == 0:
        raise ValueError("both samples must be non-empty")
    sd = float(ref.std(ddof=0))
    if sd == 0.0:
        return 0.0 if float(ref.mean()) == float(cur.mean()) else float("inf")
    return float((cur.mean() - ref.mean()) / sd)


def mean_shift_fires(reference: np.ndarray, new: np.ndarray, sigma: float) -> tuple[bool, float]:
    v = mean_shift_sigma(reference, new)
    return (abs(v) > sigma, v)
