"""
THE test. If this passes, the project has delivered its core lesson:
accuracy alone must not promote a model.
"""
from src.platform.gate import evaluate_candidate


def test_high_recall_bad_calibration_is_rejected():
    candidate = {
        "model_hash": "deadbeef",
        "metrics": {"recall": 0.95, "ece": 0.20, "p99_latency_ms": 40.0},
    }
    incumbent = {
        "model_hash": "cafe1234",
        "metrics": {"recall": 0.86, "ece": 0.04, "p99_latency_ms": 38.0},
    }

    decision = evaluate_candidate(candidate, incumbent)

    assert decision.status == "REJECT"
    assert "ece" in decision.reason.lower()
    assert "ece" in decision.failed_rules
