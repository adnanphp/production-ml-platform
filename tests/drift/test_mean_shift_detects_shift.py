import numpy as np

from src.platform.drift import mean_shift


def test_no_shift_small_value():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 500)
    b = rng.normal(0.05, 1, 500)
    fires, v = mean_shift.mean_shift_fires(a, b, sigma=2.0)
    assert not fires
    assert abs(v) < 2.0


def test_shift_fires_at_2_sigma():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 500)
    b = rng.normal(2.5, 1, 500)
    fires, v = mean_shift.mean_shift_fires(a, b, sigma=2.0)
    assert fires
    assert abs(v) > 2.0


def test_constant_reference_and_same_mean_does_not_fire():
    a = np.zeros(200)
    b = np.zeros(200)
    fires, v = mean_shift.mean_shift_fires(a, b, sigma=2.0)
    assert not fires
    assert v == 0.0


def test_constant_reference_and_different_mean_fires():
    a = np.zeros(200)
    b = np.ones(200)
    fires, v = mean_shift.mean_shift_fires(a, b, sigma=2.0)
    assert fires
    assert v == float("inf")
