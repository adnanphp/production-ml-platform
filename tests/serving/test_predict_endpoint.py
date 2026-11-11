from fastapi.testclient import TestClient

from src.platform.serving.app import create_app


def _client():
    # config with no real models -> uses ConstantModel for both slots
    return TestClient(create_app("configs/serving.yaml"))


def test_predict_returns_200_with_model_fields():
    c = _client()
    r = c.post("/predict", json={"features": [0.1, 0.2, 0.3]})
    assert r.status_code == 200
    body = r.json()
    assert set(body) == {"prediction", "model", "model_hash", "latency_ms"}
    assert body["model"] in {"incumbent", "candidate"}
    assert 0.0 <= body["prediction"] <= 1.0
    assert body["latency_ms"] >= 0.0


def test_predict_rejects_empty_features():
    c = _client()
    r = c.post("/predict", json={"features": []})
    assert r.status_code == 422   # pydantic validation
