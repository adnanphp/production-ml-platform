"""
The gate. Evaluates a candidate model against the promotion rule.

Q4 decision: cold-start (incumbent is None) applies absolute thresholds only;
the margin rule applies only when an incumbent exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from src.platform.common.config import GateConfig, load_gate_config
from src.platform.gate import rules


@dataclass
class Decision:
    status: str                 # "PROMOTE" | "REJECT"
    reason: str = ""            # empty iff PROMOTE
    failed_rules: list[str] = field(default_factory=list)
    rule_results: list[dict] = field(default_factory=list)
    cold_start: bool = False


def evaluate_candidate(
    candidate: dict,
    incumbent: dict | None,
    config: GateConfig | None = None,
) -> Decision:
    """
    candidate / incumbent: dicts with keys:
        model_hash: str
        metrics: {recall: float, ece: float, p99_latency_ms: float}
    """
    cfg = config or load_gate_config()
    cold_start = incumbent is None

    results = [
        rules.rule_recall(candidate, cfg.recall_min),
        rules.rule_ece(candidate, cfg.ece_max),
        rules.rule_latency(candidate, cfg.p99_latency_ms_max),
    ]
    if not cold_start:
        results.append(rules.rule_margin(candidate, incumbent, cfg.margin_vs_incumbent_min))

    failed = [r for r in results if not r.passed]
    rule_results_serialized = [
        {
            "name": r.name,
            "passed": r.passed,
            "value": r.value,
            "threshold": r.threshold,
            "reason": r.reason,
        }
        for r in results
    ]

    if not failed:
        return Decision(
            status="PROMOTE",
            reason="",
            failed_rules=[],
            rule_results=rule_results_serialized,
            cold_start=cold_start,
        )

    return Decision(
        status="REJECT",
        reason="; ".join(r.reason for r in failed),
        failed_rules=[r.name for r in failed],
        rule_results=rule_results_serialized,
        cold_start=cold_start,
    )
