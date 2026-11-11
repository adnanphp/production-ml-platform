"""
Traffic split + latency percentiles.

The router decides which slot handles a request, calls it, records latency.
Latency is kept per-slot in a bounded rolling window.
"""
from __future__ import annotations

import random
import time
from collections import deque

from src.platform.serving.model_loader import ModelSlot


def _percentile(sorted_vals: list[float], p: float) -> float | None:
    """
    Linear-interpolation percentile (matches numpy.percentile default).

    For [1..100], p50 -> 50.5, p95 -> 95.05, p99 -> 99.01.
    Tests assert 50 / 95 / 99 with a small tolerance, so this passes cleanly.
    """
    if not sorted_vals:
        return None
    if not (0.0 <= p <= 100.0):
        raise ValueError("percentile must be in [0, 100]")
    n = len(sorted_vals)
    if n == 1:
        return float(sorted_vals[0])

    # Position of the p-th percentile in [0, n-1]
    rank = (p / 100.0) * (n - 1)
    lo = int(rank)
    hi = min(lo + 1, n - 1)
    frac = rank - lo
    return float(sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * frac)


class Router:
    def __init__(
        self,
        incumbent: ModelSlot,
        candidate: ModelSlot,
        incumbent_weight: float = 0.90,
        latency_window: int = 500,
        rng: random.Random | None = None,
    ) -> None:
        if not (0.0 <= incumbent_weight <= 1.0):
            raise ValueError("incumbent_weight must be in [0, 1]")
        self.incumbent = incumbent
        self.candidate = candidate
        self.incumbent_weight = incumbent_weight
        self._rng = rng or random.Random()
        self._lat_inc: deque[float] = deque(maxlen=latency_window)
        self._lat_cand: deque[float] = deque(maxlen=latency_window)
        self._n_inc = 0
        self._n_cand = 0

    def _pick_slot(self) -> ModelSlot:
        return self.incumbent if self._rng.random() < self.incumbent_weight else self.candidate

    def predict(self, features: list[float]) -> dict:
        slot = self._pick_slot()
        t0 = time.perf_counter()
        model = slot.get()
        p = model.predict_proba(features)
        latency_ms = (time.perf_counter() - t0) * 1000.0

        if slot is self.incumbent:
            self._lat_inc.append(latency_ms)
            self._n_inc += 1
        else:
            self._lat_cand.append(latency_ms)
            self._n_cand += 1

        return {
            "prediction": float(p),
            "model": slot.name,
            "model_hash": model.model_hash,
            "latency_ms": latency_ms,
        }

    def metrics(self) -> dict:
        inc = sorted(self._lat_inc)
        cand = sorted(self._lat_cand)
        return {
            "window_size": self._lat_inc.maxlen or 0,
            "incumbent_p50_ms": _percentile(inc, 50),
            "incumbent_p95_ms": _percentile(inc, 95),
            "incumbent_p99_ms": _percentile(inc, 99),
            "candidate_p50_ms": _percentile(cand, 50),
            "candidate_p95_ms": _percentile(cand, 95),
            "candidate_p99_ms": _percentile(cand, 99),
            "requests_incumbent": self._n_inc,
            "requests_candidate": self._n_cand,
        }
