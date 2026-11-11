import numpy as np

from src.platform.drift import ks


def test_ks_no_shift_returns_high_pvalue():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 500)
    b = rng.normal(0, 1, 500)
    fires, stat, p = ks.ks_fires(a, b, alpha=0.01)
    assert not fires
    assert p > 0.01


def test_ks_detects_mean_shift():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 500)
    b = rng.normal(1.5, 1, 500)      # large shift
    fires, stat, p = ks.ks_fires(a, b, alpha=0.01)
    assert fires
    assert p < 0.01
    assert stat > 0.3


def test_ks_detects_variance_change():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 500)
    b = rng.normal(0, 5, 500)        # same mean, much wider
    fires, stat, p = ks.ks_fires(a, b, alpha=0.01)
    assert fires
