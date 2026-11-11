"""
Triggers that decide when to roll back.

Three independent signals (DESIGN.md §3):
  - p50 latency over window > p50_latency_ms_max
  - error rate over window > error_rate_max
  - drift detector fires (from Phase 4)

Any one firing => roll back.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TriggerResult:
    fires: bool
    reasons: list[str] = field(default_factory=list)


def check_triggers(
    *,
    p50_latency_ms: float | None,
    error_rate: float,
    drift_fires: bool,
    p50_latency_ms_max: float,
    error_rate_max: float,
) -> TriggerResult:
    reasons: list[str] = []

    if p50_latency_ms is not None and p50_latency_ms > p50_latency_ms_max:
        reasons.append(
            f"p50 latency {p50_latency_ms:.1f}ms > {p50_latency_ms_max:.1f}ms"
        )
    if error_rate > error_rate_max:
        reasons.append(f"error rate {error_rate:.3f} > {error_rate_max:.3f}")
    if drift_fires:
        reasons.append("drift detector fired")

    return TriggerResult(fires=bool(reasons), reasons=reasons)
