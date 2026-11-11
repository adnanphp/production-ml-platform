from src.platform.gate import evaluate_candidate


def test_low_recall_is_rejected(good_incumbent):
    candidate = {
        "model_hash": "x",
        "metrics": {"recall": 0.70, "ece": 0.02, "p99_latency_ms": 40.0},
    }
    d = evaluate_candidate(candidate, good_incumbent)
    assert d.status == "REJECT"
    assert "recall" in d.failed_rules
