"""
FastAPI app: /predict, /health, /metrics.

By default uses ConstantModel for both slots so the app is runnable without
model artifacts. Real models are loaded from configs/serving.yaml when
present.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException

from src.platform.serving.model_loader import ConstantModel, ModelSlot, SklearnModel
from src.platform.serving.router import Router
from src.platform.serving.schemas import MetricsResponse, PredictRequest, PredictResponse


def _build_router(config_path: str | Path = "configs/serving.yaml") -> Router:
    cfg: dict = {}
    p = Path(config_path)
    if p.exists():
        cfg = yaml.safe_load(p.read_text())

    incumbent_weight = float(cfg.get("incumbent_weight", 0.90))
    window = int(cfg.get("latency_window", 500))
    model_dir = Path(cfg.get("model_dir", "models"))

    # Incumbent: try real pkl, else constant
    inc_pkl = model_dir / "incumbent" / "model.pkl"
    if inc_pkl.exists():
        incumbent_model = SklearnModel(inc_pkl, model_hash="incumbent-pkl")
    else:
        incumbent_model = ConstantModel(0.5, model_hash="incumbent-constant")

    # Candidate: try real pkl, else constant
    cand_pkl = model_dir / "candidates" / "current" / "model.pkl"
    if cand_pkl.exists():
        candidate_model = SklearnModel(cand_pkl, model_hash="candidate-pkl")
    else:
        candidate_model = ConstantModel(0.6, model_hash="candidate-constant")

    return Router(
        incumbent=ModelSlot("incumbent", incumbent_model),
        candidate=ModelSlot("candidate", candidate_model),
        incumbent_weight=incumbent_weight,
        latency_window=window,
    )


def create_app(config_path: str | Path = "configs/serving.yaml") -> FastAPI:
    app = FastAPI(title="Production ML Platform — Serving", version="0.1.0")
    app.state.router = _build_router(config_path)

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/predict", response_model=PredictResponse)
    def predict(req: PredictRequest) -> PredictResponse:
        try:
            out = app.state.router.predict(req.features)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"inference failed: {e}")
        return PredictResponse(**out)

    @app.get("/metrics", response_model=MetricsResponse)
    def metrics() -> MetricsResponse:
        return MetricsResponse(**app.state.router.metrics())

    return app


app = create_app()
