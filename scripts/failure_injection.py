"""
Failure injection: end-to-end scenario that produces the numbers quoted
in FAILURE_REPORT.md.

Run:  python scripts/failure_injection.py

What it does:
  1. Trains nothing. Uses ConstantModel as the incumbent (p=0.5).
  2. Uses ConstantModel as a "candidate" that we PROMOTE via the real gate.
  3. Serves a rolling window of NORMAL traffic through a Router — no drift.
  4. Injects SHIFTED traffic — drift detector fires.
  5. Triggers a rollback via the real trigger logic.
  6. Records the rollback in a real SQLite registry.
  7. Prints: latency p50/p95/p99, throughput, rollback duration, drift reason.

The point is not to be fast. The point is that the numbers come out of the
real machinery, not from a spreadsheet.
"""
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

import numpy as np

from src.platform.common.config import GateConfig
from src.platform.drift import DriftDetector
from src.platform.gate import evaluate_candidate
from src.platform.registry import RegistryStore, make_record
from src.platform.rollback import check_triggers, perform_rollback
from src.platform.serving.model_loader import ConstantModel, ModelSlot
from src.platform.serving.router import Router


def main() -> dict:
    rng = np.random.default_rng(42)
    cfg = GateConfig(
        recall_min=0.85, ece_max=0.05, p99_latency_ms_max=100.0,
        margin_vs_incumbent_min=0.02, ece_bins=10,
    )

    # ── Setup: incumbent + candidate ────────────────────────
    incumbent_metrics = {"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0}
    candidate_metrics = {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 40.0}

    candidate = {"model_hash": "candidate-A", "metrics": candidate_metrics}
    incumbent = {"model_hash": "incumbent-0", "metrics": incumbent_metrics}

    # ── 1. Gate ─────────────────────────────────────────────
    decision = evaluate_candidate(candidate, incumbent, cfg)
    print(f"[gate] candidate-A -> {decision.status} ({decision.reason or 'all rules passed'})")
    assert decision.status == "PROMOTE"

    # ── 2. Registry ─────────────────────────────────────────
    db_path = Path("registry.db")
    if db_path.exists():
        db_path.unlink()
    store = RegistryStore(db_path)
    store.insert(make_record(
        model_hash="candidate-A", decision=decision,
        candidate=candidate, config=cfg, rule_version="failure-injection",
    ))

    # ── 3. Serving: 500 requests, 90/10 split, measure p50/95/99
    incumbent_model = ConstantModel(0.5, "incumbent-0")
    candidate_model = ConstantModel(0.9, "candidate-A")
    slot_inc = ModelSlot("incumbent", incumbent_model)
    slot_cand = ModelSlot("candidate", candidate_model)
    router = Router(
        incumbent=slot_inc, candidate=slot_cand,
        incumbent_weight=0.90, latency_window=500,
    )

    n_requests = 500
    features_normal = rng.normal(0, 1, (n_requests, 4))
    t_start = time.perf_counter()
    for i in range(n_requests):
        router.predict(features_normal[i].tolist())
    elapsed_s = time.perf_counter() - t_start

    m = router.metrics()
    throughput_rps = n_requests / elapsed_s
    print(f"[serving] throughput = {throughput_rps:.0f} req/s")
    print(f"[serving] incumbent latency p50/p95/p99 = "
          f"{m['incumbent_p50_ms']:.3f} / "
          f"{m['incumbent_p95_ms']:.3f} / "
          f"{m['incumbent_p99_ms']:.3f} ms")
    print(f"[serving] candidate latency p50/p95/p99 = "
          f"{m['candidate_p50_ms']:.3f} / "
          f"{m['candidate_p95_ms']:.3f} / "
          f"{m['candidate_p99_ms']:.3f} ms")

    # ── 4. Drift: inject shifted traffic ────────────────────
    reference = rng.normal(0, 1, (500, 4))
    detector = DriftDetector(
        reference=reference,
        feature_names=["f0", "f1", "f2", "f3"],
        ks_alpha=0.01, ks_min_features=2, mean_shift_sigma_threshold=2.0,
    )
    shifted = rng.normal(2.5, 1, (200, 4))
    drift = detector.check(shifted)
    print(f"[drift] fires = {drift.fires}, reason = {drift.reason!r}")
    assert drift.fires

    # ── 5. Trigger ─────────────────────────────────────────
    trigger = check_triggers(
        p50_latency_ms=m["candidate_p50_ms"],
        error_rate=0.0,
        drift_fires=drift.fires,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    print(f"[trigger] fires = {trigger.fires}, reasons = {trigger.reasons}")
    assert trigger.fires

    # ── 6. Rollback ────────────────────────────────────────
    rollback = perform_rollback(
        slot=slot_cand,
        incumbent_model=incumbent_model,
        incumbent_metrics=incumbent_metrics,
        trigger=trigger,
        registry=store,
        rule_version="failure-injection",
    )
    print(f"[rollback] from={rollback.from_hash} to={rollback.to_hash} "
          f"duration={rollback.duration_ms:.3f} ms")
    assert rollback.performed
    assert slot_cand.get().model_hash == "incumbent-0"

    # ── 7. Audit ───────────────────────────────────────────
    rows = store.get_by_model_hash("candidate-A")
    print(f"[registry] candidate-A has {len(rows)} record(s):")
    for r in rows:
        print(f"  - {r['decision']}: {r['reason'] or '(all rules passed)'}")

    # ── Summary the report will quote ──────────────────────
    summary = {
        "throughput_rps": throughput_rps,
        "incumbent_p50_ms": m["incumbent_p50_ms"],
        "incumbent_p95_ms": m["incumbent_p95_ms"],
        "incumbent_p99_ms": m["incumbent_p99_ms"],
        "candidate_p50_ms": m["candidate_p50_ms"],
        "candidate_p95_ms": m["candidate_p95_ms"],
        "candidate_p99_ms": m["candidate_p99_ms"],
        "rollback_duration_ms": rollback.duration_ms,
        "drift_reason": drift.reason,
        "trigger_reasons": trigger.reasons,
        "registry_records_for_candidate_A": len(rows),
    }
    print("\n[summary json]")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    main()
