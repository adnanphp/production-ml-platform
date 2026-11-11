from src.platform.gate import evaluate_candidate


def test_happy_path_promotes(good_candidate, good_incumbent):
    d = evaluate_candidate(good_candidate, good_incumbent)
    assert d.status == "PROMOTE"
    assert d.reason == ""
    assert d.failed_rules == []
