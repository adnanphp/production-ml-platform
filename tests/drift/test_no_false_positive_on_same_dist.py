"""
The drift detector must NOT fire when incoming traffic looks like reference.
This is the most important drift test — it's what stops you from rolling
back healthy models.
"""
import numpy as np

from src.platform.drift import DriftDetector


def _reference(n=500, d=4, seed=0):
    rng = np.random.default_rng(seed)
    return rng.normal(0, 1, (n, d))


def test_no_drift_on_same_distribution():
    ref = _reference()
    det = DriftDetector(
        reference=ref,
        feature_names=["f0", "f1", "f2", "f3"],
        ks_alpha=0.01,
        ks_min_features=2,
        mean_shift_sigma_threshold=2.0,
    )
    rng = np.random.default_rng(1)
    new = rng.normal(0, 1, (200, 4))
    result = det.check(new)
    assert result.fires is False
    assert result.reason == ""


def test_fires_on_broad_shift():
    ref = _reference()
    det = DriftDetector(
        reference=ref,
        feature_names=["f0", "f1", "f2", "f3"],
        ks_alpha=0.01,
        ks_min_features=2,
        mean_shift_sigma_threshold=2.0,
    )
    rng = np.random.default_rng(1)
    new = rng.normal(2.5, 1, (200, 4))   # everything shifted +2.5 sigma
    result = det.check(new)
    assert result.fires is True
    assert result.ks_count >= 2 or result.mean_shift_count >= 1
    assert "KS fired" in result.reason or "mean-shift" in result.reason
