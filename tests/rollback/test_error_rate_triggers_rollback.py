from src.platform.rollback import check_triggers


def test_error_rate_breach_fires():
    r = check_triggers(
        p50_latency_ms=50.0,
        error_rate=0.02,
        drift_fires=False,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    assert r.fires
    assert any("error rate" in s for s in r.reasons)


def test_error_rate_at_threshold_does_not_fire():
    r = check_triggers(
        p50_latency_ms=50.0,
        error_rate=0.01,     # exactly at max
        drift_fires=False,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    assert not r.fires
