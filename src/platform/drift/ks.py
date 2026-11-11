"""
Two-sample Kolmogorov-Smirnov test, implemented without scipy so the module
has no external deps beyond numpy.

KS statistic = max |F_ref(x) - F_new(x)| over the sorted union of samples.
Asymptotic p-value via the Kolmogorov distribution, which is accurate enough
for n >= 30 on each side and avoids the scipy dependency.
"""
from __future__ import annotations

import math
import numpy as np


def ks_statistic(reference: np.ndarray, new: np.ndarray) -> float:
    """Max absolute gap between the two empirical CDFs."""
    ref = np.sort(np.asarray(reference, dtype=float).ravel())
    cur = np.sort(np.asarray(new, dtype=float).ravel())
    if ref.size == 0 or cur.size == 0:
        raise ValueError("both samples must be non-empty")

    # All points where the empirical CDFs can differ
    grid = np.concatenate([ref, cur])
    cdf_ref = np.searchsorted(ref, grid, side="right") / ref.size
    cdf_cur = np.searchsorted(cur, grid, side="right") / cur.size
    return float(np.max(np.abs(cdf_ref - cdf_cur)))


def ks_pvalue(d_stat: float, n_ref: int, n_cur: int) -> float:
    """
    Asymptotic p-value for the two-sample KS test (Kolmogorov distribution).

    Q_KS(lambda) = 2 * sum_{k=1..inf} (-1)^(k-1) exp(-2 k^2 lambda^2)
    where lambda = (sqrt(n_eff) + 0.12 + 0.11/sqrt(n_eff)) * D
    and n_eff = n_ref * n_cur / (n_ref + n_cur).
    """
    if d_stat <= 0:
        return 1.0
    if n_ref <= 0 or n_cur <= 0:
        raise ValueError("sample sizes must be positive")
    n_eff = (n_ref * n_cur) / (n_ref + n_cur)
    sqrt_n = math.sqrt(n_eff)
    lam = (sqrt_n + 0.12 + 0.11 / sqrt_n) * d_stat
    # Sum the Kolmogorov series until convergence
    total = 0.0
    for k in range(1, 100):
        term = 2.0 * ((-1) ** (k - 1)) * math.exp(-2.0 * (k ** 2) * (lam ** 2))
        total += term
        if abs(term) < 1e-12:
            break
    return max(0.0, min(1.0, total))


def ks_fires(reference: np.ndarray, new: np.ndarray, alpha: float) -> tuple[bool, float, float]:
    """Return (fires, statistic, pvalue). fires == (pvalue < alpha)."""
    d = ks_statistic(reference, new)
    p = ks_pvalue(d, len(reference), len(new))
    return (p < alpha, d, p)
