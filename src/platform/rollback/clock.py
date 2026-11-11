"""Wall-clock measurement helper for rollback duration."""
from __future__ import annotations

import time
from contextlib import contextmanager


@contextmanager
def measure_ms():
    """Yields a callable; after the block, calling it returns elapsed ms."""
    t0 = time.perf_counter()
    holder = {"ms": 0.0}

    def elapsed() -> float:
        return (time.perf_counter() - t0) * 1000.0

    yield elapsed
    holder["ms"] = elapsed()
