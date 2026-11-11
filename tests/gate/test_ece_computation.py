import numpy as np

from src.platform.gate import expected_calibration_error


def test_perfectly_calibrated_binary_low_ece():
    # Predict 0.5 always, half the labels are 1 -> calibrated at 0.5
    y_true = np.array([1, 0, 1, 0, 1, 0, 1, 0])
    y_prob = np.full(8, 0.5)
    ece = expected_calibration_error(y_true, y_prob, n_bins=10)
    assert ece < 0.01


def test_confidently_wrong_has_high_ece():
    # Predict 0.95, all labels 0 -> badly miscalibrated
    y_true = np.zeros(100)
    y_prob = np.full(100, 0.95)
    ece = expected_calibration_error(y_true, y_prob, n_bins=10)
    assert ece > 0.9


def test_input_validation():
    import pytest
    with pytest.raises(ValueError):
        expected_calibration_error(np.array([]), np.array([]))
    with pytest.raises(ValueError):
        expected_calibration_error(np.array([0, 1]), np.array([1.5, 0.2]))
    with pytest.raises(ValueError):
        expected_calibration_error(np.array([0, 1]), np.array([0.5]))
