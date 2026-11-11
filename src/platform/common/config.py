"""Config loading. Phase 1 only needs gate.yaml."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class GateConfig:
    recall_min: float
    ece_max: float
    p99_latency_ms_max: float
    margin_vs_incumbent_min: float
    ece_bins: int


def load_gate_config(path: str | Path = "configs/gate.yaml") -> GateConfig:
    data = yaml.safe_load(Path(path).read_text())
    return GateConfig(
        recall_min=float(data["recall_min"]),
        ece_max=float(data["ece_max"]),
        p99_latency_ms_max=float(data["p99_latency_ms_max"]),
        margin_vs_incumbent_min=float(data["margin_vs_incumbent_min"]),
        ece_bins=int(data["ece_bins"]),
    )
