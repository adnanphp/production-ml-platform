import numpy as np

from src.platform.drift import RollingWindow


def test_window_drops_oldest_when_full():
    w = RollingWindow(size=5)
    for i in range(10):
        w.add([float(i)])
    arr = w.as_array()
    assert arr.shape == (5, 1)
    assert arr[:, 0].tolist() == [5.0, 6.0, 7.0, 8.0, 9.0]


def test_window_not_full_tracks_len():
    w = RollingWindow(size=10)
    for _ in range(3):
        w.add([0.0])
    assert len(w) == 3
    assert not w.full


def test_window_empty_as_array():
    w = RollingWindow(size=10)
    assert w.as_array().shape == (0, 0)
