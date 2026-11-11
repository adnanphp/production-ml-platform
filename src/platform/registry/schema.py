"""
DecisionRecord — the registry row.

Superset of gate.Decision plus the audit fields DESIGN.md §4 mandates:
model_hash, rule_version, timestamp, actor.

One record per gate evaluation. Never mutated, never deleted.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone


@dataclass(frozen=True)
class DecisionRecord:
    # Identity
    model_hash: str
    rule_version: str          # git SHA of the gate code, or "dev"
    # Decision
    decision: str              # "PROMOTE" | "REJECT"
    reason: str                # empty iff PROMOTE
    failed_rules: tuple[str, ...]
    # Metrics snapshot (what the gate saw)
    recall: float
    ece: float
    p99_latency_ms: float
    # Config snapshot (what thresholds were in force)
    thresholds_json: str       # JSON of GateConfig at evaluation time
    # Per-rule detail (serialized list of dicts)
    rule_results_json: str
    # Provenance
    cold_start: bool
    timestamp: str             # ISO-8601 UTC
    actor: str                 # "auto" | "human:<id>"


def make_record(
    *,
    model_hash: str,
    decision,                 # gate.Decision
    candidate: dict,
    config,                   # common.config.GateConfig
    rule_version: str = "dev",
    actor: str = "auto",
    now: datetime | None = None,
) -> DecisionRecord:
    ts = (now or datetime.now(timezone.utc)).isoformat()
    thresholds = {
        "recall_min": config.recall_min,
        "ece_max": config.ece_max,
        "p99_latency_ms_max": config.p99_latency_ms_max,
        "margin_vs_incumbent_min": config.margin_vs_incumbent_min,
        "ece_bins": config.ece_bins,
    }
    m = candidate["metrics"]
    return DecisionRecord(
        model_hash=model_hash,
        rule_version=rule_version,
        decision=decision.status,
        reason=decision.reason,
        failed_rules=tuple(decision.failed_rules),
        recall=float(m["recall"]),
        ece=float(m["ece"]),
        p99_latency_ms=float(m["p99_latency_ms"]),
        thresholds_json=json.dumps(thresholds, sort_keys=True),
        rule_results_json=json.dumps(decision.rule_results, sort_keys=True),
        cold_start=bool(decision.cold_start),
        timestamp=ts,
        actor=actor,
    )
