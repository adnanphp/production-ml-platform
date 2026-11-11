from src.platform.serving.model_loader import ConstantModel, ModelSlot
from src.platform.serving.router import Router, _percentile


def test_percentile_function_basics():
    vals = [float(i) for i in range(1, 101)]     # 1..100
    # Linear-interpolation percentiles:
    assert abs(_percentile(vals, 50) - 50.5) < 1e-9
    assert abs(_percentile(vals, 95) - 95.05) < 1e-9
    assert abs(_percentile(vals, 99) - 99.01) < 1e-9
    assert _percentile([], 50) is None
    assert _percentile([42.0], 50) == 42.0


def test_router_records_latency_per_slot():
    inc = ModelSlot("incumbent", ConstantModel(0.1, "inc"))
    cand = ModelSlot("candidate", ConstantModel(0.9, "cand"))
    r = Router(incumbent=inc, candidate=cand, incumbent_weight=1.0, latency_window=100)

    for _ in range(50):
        r.predict([0.0])

    m = r.metrics()
    assert m["requests_incumbent"] == 50
    assert m["requests_candidate"] == 0
    assert m["incumbent_p50_ms"] is not None
    assert m["incumbent_p95_ms"] is not None
    assert m["incumbent_p99_ms"] is not None
    assert m["candidate_p50_ms"] is None


def test_window_bounds_memory():
    inc = ModelSlot("incumbent", ConstantModel(0.1, "inc"))
    cand = ModelSlot("candidate", ConstantModel(0.9, "cand"))
    r = Router(incumbent=inc, candidate=cand, incumbent_weight=1.0, latency_window=10)
    for _ in range(100):
        r.predict([0.0])
    assert r.metrics()["requests_incumbent"] == 100
    assert len(r._lat_inc) == 10
