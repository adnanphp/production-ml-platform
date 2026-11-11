"""
Rollback executor.

The contract:
  - Swap the candidate slot back to the last-known-good model.
  - Record the rollback decision in the registry (via registry.store.insert).
  - Return a RollbackResult with wall-clock duration.

If there is no incumbent (cold-start), rollback is a no-op with a reason.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone

from src.platform.registry import DecisionRecord, RegistryStore
from src.platform.rollback.clock import measure_ms
from src.platform.rollback.triggers import TriggerResult
from src.platform.serving.model_loader import Model, ModelSlot


@dataclass
class RollbackResult:
    performed: bool
    reason: str
    from_hash: str | None
    to_hash: str | None
    duration_ms: float
    trigger_reasons: list[str]


def perform_rollback(
    *,
    slot: ModelSlot,
    incumbent_model: Model,
    incumbent_metrics: dict,      # {recall, ece, p99_latency_ms} — used for the record
    trigger: TriggerResult,
    registry: RegistryStore | None = None,
    rule_version: str = "dev",
    now: datetime | None = None,
) -> RollbackResult:
    """
    Roll back the given slot to `incumbent_model`. If registry is provided,
    write an audit record.
    """
    if not trigger.fires:
        return RollbackResult(
            performed=False,
            reason="no trigger fired",
            from_hash=None,
            to_hash=None,
            duration_ms=0.0,
            trigger_reasons=[],
        )

    with measure_ms() as elapsed:
        old_hash = slot.swap(incumbent_model)

        if registry is not None:
            thresholds = {
                "trigger_reasons": trigger.reasons,
                "note": "rollback uses default thresholds in this record",
            }
            rec = DecisionRecord(
                model_hash=old_hash,
                rule_version=rule_version,
                decision="REJECT",           # rollback = reject the model that was serving
                reason="; ".join(trigger.reasons),
                failed_rules=tuple(),
                recall=float(incumbent_metrics.get("recall", 0.0)),
                ece=float(incumbent_metrics.get("ece", 0.0)),
                p99_latency_ms=float(incumbent_metrics.get("p99_latency_ms", 0.0)),
                thresholds_json=json.dumps(thresholds, sort_keys=True),
                rule_results_json=json.dumps([]),
                cold_start=False,
                timestamp=(now or datetime.now(timezone.utc)).isoformat(),
                actor="auto",
            )
            registry.insert(rec)

    return RollbackResult(
        performed=True,
        reason="; ".join(trigger.reasons),
        from_hash=old_hash,
        to_hash=incumbent_model.model_hash,
        duration_ms=elapsed(),
        trigger_reasons=trigger.reasons,
    )
