from src.platform.rollback import check_triggers


def test_drift_alone_fires():
    r = check_triggers(
        p50_latency_ms=50.0,
        error_rate=0.0,
        drift_fires=True,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    assert r.fires
    assert any("drift" in s for s in r.reasons)


def test_no_triggers_all_quiet():
    r = check_triggers(
        p50_latency_ms=50.0,
        error_rate=0.0,
        drift_fires=False,
        p50_latency_ms_max=200.0,
        error_rate_max=0.01,
    )
    assert not r.fires
    assert r.reasons == []
