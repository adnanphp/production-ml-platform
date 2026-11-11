"""
End-to-end: promote a candidate, serve it, detect drift, roll back,
record the decision in the registry.

If this test passes, the project has exercised every phase in one flow.
"""
import numpy as np

from src.platform.common.config import GateConfig
from src.platform.drift import DriftDetector
from src.platform.gate import evaluate_candidate
from src.platform.registry import RegistryStore, make_record
from src.platform.rollback import check_triggers, perform_rollback
from src.platform.serving.model_loader import ConstantModel, ModelSlot


def test_full_lifecycle(tmp_path):
    # ── 1. Gate: candidate promoted ────────────────────────────
    cfg = GateConfig(
        recall_min=0.85, ece_max=0.05, p99_latency_ms_max=100.0,
        margin_vs_incumbent_min=0.02, ece_bins=10,
    )
    candidate = {
        "model_hash": "cand-A",
        "metrics": {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 40.0},
    }
    incumbent = {
        "model_hash": "inc-0",
        "metrics": {"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
    }
    decision = evaluate_candidate(candidate, incumbent, cfg)
    assert decision.status == "PROMOTE"

    # ── 2. Registry: record the promotion ──────────────────────
    db = tmp_path / "reg.db"
    with RegistryStore(db) as store:
        store.insert(make_record(
            model_hash="cand-A", decision=decision,
            candidate=candidate, config=cfg,
            rule_version="sha-test",
        ))
        assert store.get_incumbent()["model_hash"] == "cand-A"

        # ── 3. Serving: candidate is now live ──────────────────
        slot = ModelSlot("live", ConstantModel(0.9, "cand-A"))
        assert slot.get().model_hash == "cand-A"

        # ── 4. Drift: incoming traffic shifted ─────────────────
        rng = np.random.default_rng(0)
        reference = rng.normal(0, 1, (500, 4))
        detector = DriftDetector(
            reference=reference,
            feature_names=["f0", "f1", "f2", "f3"],
            ks_alpha=0.01, ks_min_features=2, mean_shift_sigma_threshold=2.0,
        )
        shifted = rng.normal(2.5, 1, (200, 4))
        drift = detector.check(shifted)
        assert drift.fires is True
        assert drift.reason

        # ── 5. Triggers: drift alone is enough ─────────────────
        trigger = check_triggers(
            p50_latency_ms=50.0,
            error_rate=0.0,
            drift_fires=drift.fires,
            p50_latency_ms_max=200.0,
            error_rate_max=0.01,
        )
        assert trigger.fires
        assert any("drift" in s for s in trigger.reasons)

        # ── 6. Rollback: swap to incumbent ─────────────────────
        incumbent_model = ConstantModel(0.5, "inc-0")
        result = perform_rollback(
            slot=slot,
            incumbent_model=incumbent_model,
            incumbent_metrics=incumbent["metrics"],
            trigger=trigger,
            registry=store,
            rule_version="sha-test",
        )
        assert result.performed
        assert result.from_hash == "cand-A"
        assert result.to_hash == "inc-0"
        assert slot.get().model_hash == "inc-0"

        # ── 7. Registry: rollback recorded as REJECT ───────────
        rows = store.get_by_model_hash("cand-A")
        # row 1 = original promotion, row 2 = rollback rejection
        assert len(rows) == 2
        assert rows[0]["decision"] == "PROMOTE"
        assert rows[1]["decision"] == "REJECT"
        assert "drift" in rows[1]["reason"].lower()
