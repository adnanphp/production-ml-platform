"""
THE test. If this passes, the project has already delivered its core lesson:
accuracy alone must not promote a model.

A model with high recall but bad calibration (high ECE) MUST be rejected.
"""
from src.platform.gate import evaluate_candidate


def test_high_recall_bad_calibration_is_rejected():
    candidate = {
        "model_hash": "deadbeef",
        "metrics": {
            "recall": 0.95,          # well above 0.85 threshold
            "ece": 0.20,             # well above 0.05 threshold
            "p99_latency_ms": 40.0,  # under 100 ms
        },
    }
    incumbent = {
        "model_hash": "cafe1234",
        "metrics": {"recall": 0.86, "ece": 0.04, "p99_latency_ms": 38.0},
    }

    decision = evaluate_candidate(candidate, incumbent)

    assert decision.status == "REJECT"
    assert "ece" in decision.reason.lower()
