from fastapi.testclient import TestClient

from src.platform.serving.app import create_app


def test_health():
    c = TestClient(create_app("configs/serving.yaml"))
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_metrics_shape_before_any_traffic():
    c = TestClient(create_app("configs/serving.yaml"))
    r = c.get("/metrics")
    assert r.status_code == 200
    body = r.json()
    assert body["requests_incumbent"] == 0
    assert body["requests_candidate"] == 0
    assert body["incumbent_p50_ms"] is None


def test_metrics_after_traffic():
    c = TestClient(create_app("configs/serving.yaml"))
    for _ in range(20):
        c.post("/predict", json={"features": [0.1, 0.2]})
    body = c.get("/metrics").json()
    total = body["requests_incumbent"] + body["requests_candidate"]
    assert total == 20
    # at least one slot received traffic
    assert body["requests_incumbent"] > 0 or body["requests_candidate"] > 0
