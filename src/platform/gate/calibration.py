"""
Expected Calibration Error (ECE).

Bins predictions by confidence, compares mean predicted probability against
empirical accuracy per bin, weights each bin by its share of samples.

Q2 decision: 10 bins. With N=2000 -> ~200 samples/bin, stable estimate.
"""
from __future__ import annotations

import numpy as np


def expected_calibration_error(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    n_bins: int = 10,
) -> float:
    """
    y_true: 1-D array of 0/1 labels
    y_prob: 1-D array of probabilities in [0, 1]
    returns: ECE in [0, 1], lower is better calibrated
    """
    y_true = np.asarray(y_true, dtype=float).ravel()
    y_prob = np.asarray(y_prob, dtype=float).ravel()
    if y_true.shape != y_prob.shape:
        raise ValueError("y_true and y_prob must have same shape")
    if y_prob.size == 0:
        raise ValueError("empty input")
    if np.any(y_prob < 0) or np.any(y_prob > 1):
        raise ValueError("y_prob must be in [0, 1]")

    # Bin boundaries on [0, 1]. Use linspace; include rightmost edge in last bin.
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    # bin index: searchsorted with right=... to make [edge_i, edge_i+1)
    bin_idx = np.digitize(y_prob, edges[1:-1], right=False)

    n = y_prob.size
    ece = 0.0
    for b in range(n_bins):
        mask = bin_idx == b
        count = int(mask.sum())
        if count == 0:
            continue
        avg_conf = float(y_prob[mask].mean())
        avg_acc = float(y_true[mask].mean())
        ece += (count / n) * abs(avg_conf - avg_acc)
    return float(ece)
