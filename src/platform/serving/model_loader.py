"""
Model loading.

A "model" here is any callable: features -> probability.
Two concrete backends ship:
  - SklearnModel  wraps a .pkl file with a predict_proba method
  - ConstantModel  returns a fixed probability (used in tests)

The loader can hot-swap the incumbent (Phase 5 will exercise this).
"""
from __future__ import annotations

import pickle
import threading
from pathlib import Path
from typing import Protocol


class Model(Protocol):
    model_hash: str
    def predict_proba(self, features: list[float]) -> float: ...


class SklearnModel:
    def __init__(self, path: Path, model_hash: str) -> None:
        with path.open("rb") as f:
            self._inner = pickle.load(f)
        self.model_hash = model_hash

    def predict_proba(self, features: list[float]) -> float:
        # sklearn's predict_proba returns shape (n, 2); take P(class=1)
        import numpy as np
        arr = np.asarray([features], dtype=float)
        proba = self._inner.predict_proba(arr)
        return float(proba[0, 1])


class ConstantModel:
    """Deterministic model for tests and for the app's health check."""
    def __init__(self, p: float, model_hash: str = "constant") -> None:
        self.p = p
        self.model_hash = model_hash

    def predict_proba(self, features: list[float]) -> float:
        return self.p


class ModelSlot:
    """
    Holds the currently-active model for one role (incumbent or candidate).
    Thread-safe hot-swap.
    """
    def __init__(self, name: str, model: Model) -> None:
        self.name = name
        self._model = model
        self._lock = threading.RLock()

    def get(self) -> Model:
        with self._lock:
            return self._model

    def swap(self, new_model: Model) -> str:
        """Return the model_hash that was previously active."""
        with self._lock:
            old_hash = self._model.model_hash
            self._model = new_model
            return old_hash
