"""Q4: with no incumbent, margin rule is skipped; absolute thresholds decide."""
from src.platform.gate import evaluate_candidate


def test_cold_start_promotes_on_absolute_thresholds():
    candidate = {
        "model_hash": "first",
        "metrics": {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 40.0},
    }
    d = evaluate_candidate(candidate, incumbent=None)
    assert d.status == "PROMOTE"
    assert d.cold_start is True
    # margin rule must not appear in evaluated rules
    names = [r["name"] for r in d.rule_results]
    assert "margin_vs_incumbent" not in names


def test_cold_start_still_rejects_bad_calibration():
    candidate = {
        "model_hash": "first",
        "metrics": {"recall": 0.90, "ece": 0.30, "p99_latency_ms": 40.0},
    }
    d = evaluate_candidate(candidate, incumbent=None)
    assert d.status == "REJECT"
    assert "ece" in d.failed_rules
