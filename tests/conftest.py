import pytest


@pytest.fixture
def good_candidate():
    return {
        "model_hash": "aaa111",
        "metrics": {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 40.0},
    }


@pytest.fixture
def good_incumbent():
    return {
        "model_hash": "bbb222",
        "metrics": {"recall": 0.86, "ece": 0.03, "p99_latency_ms": 38.0},
    }
