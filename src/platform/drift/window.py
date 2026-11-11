"""
Rolling window of incoming feature vectors.

Features are stored as an (N, D) numpy array, dropping oldest when at cap.
Caller is responsible for column meaning (feature_names in configs/drift.yaml).
"""
from __future__ import annotations

from collections import deque
import numpy as np


class RollingWindow:
    def __init__(self, size: int) -> None:
        if size <= 0:
            raise ValueError("window size must be positive")
        self.size = size
        self._rows: deque[list[float]] = deque(maxlen=size)

    def add(self, features: list[float]) -> None:
        self._rows.append(list(features))

    def as_array(self) -> np.ndarray:
        if not self._rows:
            return np.empty((0, 0), dtype=float)
        return np.asarray(self._rows, dtype=float)

    def __len__(self) -> int:
        return len(self._rows)

    @property
    def full(self) -> bool:
        return len(self._rows) == self.size
