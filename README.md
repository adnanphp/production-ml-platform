# Production ML Platform

Machinery to **safely promote, serve, monitor, and roll back** ML models.

A model is not production-ready because it scores well on a test set.
It's production-ready because the system around it can answer four
questions:

1. **Is this candidate good enough to replace the running model?**
   → *evaluation gate*, with recall, calibration (ECE), and latency rules.

2. **What did we decide, and can we reproduce it?**
   → *SQLite model registry*, recording every decision, thresholds in force,
   per-rule reasons, and a `rule_version` for reproducibility.

3. **Is the running model still valid?**
   → *drift detection*: KS test per feature + mean-shift guard at 2σ.

4. **How fast can we undo a bad promotion?**
   → *automatic rollback*, triggered by latency, error rate, or drift;
   measured in wall-clock milliseconds.

## Architecture
candidate model ──► ┌───────────────┐
│ EVAL GATE │ ←── configs/gate.yaml
│ recall, ECE, │
│ latency, │
│ margin │
└───────┬───────┘
│ PROMOTE | REJECT
▼
┌───────────────┐
│ REGISTRY │ ←── SQLite (registry.db)
│ hash, metrics,│
│ thresholds, │
│ rule_version │
└───────┬───────┘
│
▼
incoming ──► ┌───────────────┐ ┌───────────────┐
traffic │ ROUTER │ 90/10 │ CANDIDATE │
│ (weighted) ├───────►│ slot │
│ ├──┐ └───────┬───────┘
└───────┬───────┘ │ │
│ │ ▼
│ │ ┌───────────────┐
│ │ │ DRIFT DETECT │
│ │ │ KS + 2σ mean │
│ │ └───────┬───────┘
│ │ │ fires?
│ │ ▼
│ │ ┌───────────────┐
│ └────►│ ROLLBACK │
│ │ swap + record │
│ └───────────────┘
▼
┌───────────────┐
│ INCUMBENT │
│ slot (live) │
└───────────────┘

text

## Numbers this system produces

Run `make failure-injection` to reproduce. Fill in after your first run:

| Metric | Value |
|---|---|
| Throughput | `<fill from script output>` |
| Incumbent p50/p95/p99 | `<fill>` |
| Candidate p50/p95/p99 | `<fill>` |
| Rollback duration | `<fill>` |

## Tests

51 tests across 6 phases:
make test

text

## Quick start

```bash
pip install -e .

# run the gate on a candidate (see DESIGN.md for the rule)
make test-gate

# serve locally
make serve
curl -X POST localhost:8000/predict \
  -H 'content-type: application/json' -d '{"features":[0.1,0.2]}'

# end-to-end: promote, serve, inject drift, roll back, audit
make failure-injection
Design notes
See DESIGN.md for the promotion rule, rollback triggers, and
the four design decisions (validation-set hash, ECE bins, drift statistic,
cold-start behavior).

See FAILURE_REPORT.md for one run's numbers and the
negative result.

Status
v0.1.0 — all 6 phases complete, 51 tests passing.

Not (yet) deployed to a public URL. That's the next milestone outside the
scope of this repo.
