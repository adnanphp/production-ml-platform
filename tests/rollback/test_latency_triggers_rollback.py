from src.platform.rollback import check_triggers


def test_latency_breach_fires():
    r = check_triggers(
        p50_latency_ms=250.0,
        error_rate=0.0,
        drift_fires=False,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    assert r.fires
    assert any("latency" in s for s in r.reasons)


def test_latency_within_threshold_does_not_fire():
    r = check_triggers(
        p50_latency_ms=150.0,
        error_rate=0.0,
        drift_fires=False,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    assert not r.fires
