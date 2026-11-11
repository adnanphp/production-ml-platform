"""Shared constructors for registry tests."""
from src.platform.common.config import GateConfig
from src.platform.gate import evaluate_candidate
from src.platform.registry import make_record


GATE_CFG = GateConfig(
    recall_min=0.85,
    ece_max=0.05,
    p99_latency_ms_max=100.0,
    margin_vs_incumbent_min=0.02,
    ece_bins=10,
)


def promote_record(model_hash="promo1", rule_version="abc123"):
    candidate = {
        "model_hash": model_hash,
        "metrics": {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 40.0},
    }
    incumbent = {
        "model_hash": "inc0",
        "metrics": {"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
    }
    decision = evaluate_candidate(candidate, incumbent, GATE_CFG)
    assert decision.status == "PROMOTE"
    return make_record(
        model_hash=model_hash,
        decision=decision,
        candidate=candidate,
        config=GATE_CFG,
        rule_version=rule_version,
    )


def reject_record(model_hash="rej1", rule_version="abc123"):
    candidate = {
        "model_hash": model_hash,
        "metrics": {"recall": 0.95, "ece": 0.20, "p99_latency_ms": 40.0},
    }
    incumbent = {
        "model_hash": "inc0",
        "metrics": {"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
    }
    decision = evaluate_candidate(candidate, incumbent, GATE_CFG)
    assert decision.status == "REJECT"
    return make_record(
        model_hash=model_hash,
        decision=decision,
        candidate=candidate,
        config=GATE_CFG,
        rule_version=rule_version,
    )
