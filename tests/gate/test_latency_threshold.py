from src.platform.gate import evaluate_candidate


def test_slow_model_is_rejected(good_incumbent):
    candidate = {
        "model_hash": "x",
        "metrics": {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 250.0},
    }
    d = evaluate_candidate(candidate, good_incumbent)
    assert d.status == "REJECT"
    assert "p99_latency_ms" in d.failed_rules
