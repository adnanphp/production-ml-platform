
Changelog
[0.1.0] — Phase 6
Added
Phase 1 — Evaluation gate: recall, ECE (calibration), latency, margin rules.
Cold-start promotes on absolute thresholds only. Decision.rule_results
carries per-rule value/threshold/passed/reason for audit.

Phase 2 — SQLite model registry. Append-only. Records every decision with
model_hash, rule_version, thresholds_json, rule_results_json,
cold_start, timestamp, actor.

Phase 3 — Side-by-side serving. Weighted router (default 90/10), rolling
latency window per slot, /predict, /health, /metrics.

Phase 4 — Drift detection. Two-sample KS test + 2σ mean-shift guard.
Config: configs/drift.yaml.

Phase 5 — Automated rollback. Three triggers (latency, error rate, drift).
Uses ModelSlot.swap() for hot swap; writes the rollback to the registry
as a REJECT record with the trigger reason as reason.

Phase 6 — Docs. README.md, DESIGN.md, FAILURE_REPORT.md,
scripts/failure_injection.py, Makefile.

Tests
51 passing: 10 gate, 8 registry, 11 serving, 12 drift, 9 rollback,
1 integration.

Design decisions
Validation set is a frozen parquet with sha256 hash (Q1).

ECE uses 10 bins (Q2).

Drift fires on KS p < 0.01 for ≥2 features OR mean-shift > 2σ on any
feature (Q3).

Cold-start (no incumbent) skips the margin rule (Q4).

Known limitations
Not deployed to a public URL. Serving runs locally via make serve.

Registry is SQLite; multi-process concurrency not handled (single-writer).

p99_latency_ms on the gate is measured on the serving container in
Phases 3/5, but the gate accepts it as an input — no live measurement
in the gate itself.
