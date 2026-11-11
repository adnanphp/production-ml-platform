"""
Drift detector.

Combines per-feature KS tests and mean-shift guards.

Fire rule (Q3):
    fires = (number of features whose KS p < alpha >= ks_min_features)
         OR (any feature's |mean_shift_sigma| > mean_shift_sigma)
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from src.platform.drift import ks, mean_shift


@dataclass
class FeatureDrift:
    name: str
    ks_p: float
    ks_stat: float
    ks_fires: bool
    mean_shift_sigma: float
    mean_shift_fires: bool


@dataclass
class DriftResult:
    fires: bool
    reason: str
    ks_count: int
    mean_shift_count: int
    features: list[FeatureDrift] = field(default_factory=list)


class DriftDetector:
    def __init__(
        self,
        reference: np.ndarray,
        feature_names: list[str],
        ks_alpha: float = 0.01,
        ks_min_features: int = 2,
        mean_shift_sigma_threshold: float = 2.0,
    ) -> None:
        reference = np.asarray(reference, dtype=float)
        if reference.ndim != 2:
            raise ValueError("reference must be 2-D (N, D)")
        if reference.shape[1] != len(feature_names):
            raise ValueError(
                f"reference has {reference.shape[1]} cols but "
                f"{len(feature_names)} feature names given"
            )
        self.reference = reference
        self.feature_names = list(feature_names)
        self.ks_alpha = ks_alpha
        self.ks_min_features = ks_min_features
        self.mean_shift_sigma_threshold = mean_shift_sigma_threshold

    def check(self, new: np.ndarray) -> DriftResult:
        new = np.asarray(new, dtype=float)
        if new.ndim != 2 or new.shape[1] != self.reference.shape[1]:
            raise ValueError("new window shape mismatch with reference")

        per_feature: list[FeatureDrift] = []
        ks_hits = 0
        ms_hits = 0
        for j, name in enumerate(self.feature_names):
            ref_col = self.reference[:, j]
            new_col = new[:, j]
            fires_ks, stat, p = ks.ks_fires(ref_col, new_col, self.ks_alpha)
            fires_ms, shift = mean_shift.mean_shift_fires(
                ref_col, new_col, self.mean_shift_sigma_threshold
            )
            if fires_ks:
                ks_hits += 1
            if fires_ms:
                ms_hits += 1
            per_feature.append(
                FeatureDrift(
                    name=name,
                    ks_p=p,
                    ks_stat=stat,
                    ks_fires=fires_ks,
                    mean_shift_sigma=shift,
                    mean_shift_fires=fires_ms,
                )
            )

        ks_trigger = ks_hits >= self.ks_min_features
        ms_trigger = ms_hits >= 1
        fires = ks_trigger or ms_trigger

        reasons = []
        if ks_trigger:
            reasons.append(f"KS fired on {ks_hits} feature(s) (>= {self.ks_min_features})")
        if ms_trigger:
            reasons.append(f"mean-shift exceeded {self.mean_shift_sigma_threshold}σ on {ms_hits} feature(s)")
        reason = "; ".join(reasons) if reasons else ""

        return DriftResult(
            fires=fires,
            reason=reason,
            ks_count=ks_hits,
            mean_shift_count=ms_hits,
            features=per_feature,
        )
