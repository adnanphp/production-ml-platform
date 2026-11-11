"""Pydantic request/response models."""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    features: list[float] = Field(..., min_length=1, max_length=64)


class PredictResponse(BaseModel):
    prediction: float
    model: str            # "incumbent" | "candidate"
    model_hash: str
    latency_ms: float


class MetricsResponse(BaseModel):
    window_size: int
    incumbent_p50_ms: float | None
    incumbent_p95_ms: float | None
    incumbent_p99_ms: float | None
    candidate_p50_ms: float | None
    candidate_p95_ms: float | None
    candidate_p99_ms: float | None
    requests_incumbent: int
    requests_candidate: int
