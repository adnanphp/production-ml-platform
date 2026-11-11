"""
Individual promotion rules. Each returns (passed: bool, reason: str).

reason is "" when passed, human-readable when failed.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RuleResult:
    name: str
    passed: bool
    reason: str
    value: float
    threshold: float


def rule_recall(candidate: dict, recall_min: float) -> RuleResult:
    v = float(candidate["metrics"]["recall"])
    ok = v >= recall_min
    return RuleResult(
        name="recall",
        passed=ok,
        reason="" if ok else f"recall {v:.3f} < threshold {recall_min:.3f}",
        value=v,
        threshold=recall_min,
    )


def rule_ece(candidate: dict, ece_max: float) -> RuleResult:
    v = float(candidate["metrics"]["ece"])
    ok = v <= ece_max
    return RuleResult(
        name="ece",
        passed=ok,
        reason="" if ok else f"ECE {v:.3f} > threshold {ece_max:.3f} (miscalibrated)",
        value=v,
        threshold=ece_max,
    )


def rule_latency(candidate: dict, p99_max: float) -> RuleResult:
    v = float(candidate["metrics"]["p99_latency_ms"])
    ok = v <= p99_max
    return RuleResult(
        name="p99_latency_ms",
        passed=ok,
        reason="" if ok else f"p99 latency {v:.1f}ms > threshold {p99_max:.1f}ms",
        value=v,
        threshold=p99_max,
    )


def rule_margin(candidate: dict, incumbent: dict, margin_min: float) -> RuleResult:
    """
    Candidate must improve on incumbent recall by at least margin_min (absolute).
    Only applied when incumbent exists (Q4: cold-start skips this rule).
    """
    c = float(candidate["metrics"]["recall"])
    i = float(incumbent["metrics"]["recall"])
    delta = c - i
    ok = delta >= margin_min
    return RuleResult(
        name="margin_vs_incumbent",
        passed=ok,
        reason="" if ok else (
            f"recall improvement {delta:+.3f} < required +{margin_min:.3f} "
            f"(candidate {c:.3f} vs incumbent {i:.3f})"
        ),
        value=delta,
        threshold=margin_min,
    )
