from src.platform.gate import evaluate_candidate


def test_insufficient_margin_is_rejected(good_incumbent):
    # recall 0.87 vs incumbent 0.86 -> +0.01, below the +0.02 requirement
    candidate = {
        "model_hash": "x",
        "metrics": {"recall": 0.87, "ece": 0.02, "p99_latency_ms": 40.0},
    }
    d = evaluate_candidate(candidate, good_incumbent)
    assert d.status == "REJECT"
    assert "margin_vs_incumbent" in d.failed_rules
