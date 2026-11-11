# Production ML Platform — Design

> Status: DRAFT — thresholds are placeholders. Edit every number below
> to your own judgment before Phase 1. The numbers are the learning.

## 0. One Sentence

Build the machinery that decides whether a newly trained model is safe to
replace the model currently serving traffic, and that automatically undoes
the swap if the new one misbehaves.

## 1. Model and Task

- Task: binary classification (reuse the stock-sentiment classifier from
  da_Stock-sentiment_analysis_NLP — no new data work)
- Input: text (news headline / reddit snippet) -> feature vector
- Output: probability in [0, 1]
- Validation set: held-out, fixed, versioned (hash recorded)
- Metrics computed on validation set:
  - recall
  - ECE (expected calibration error, 10 bins)
  - p99 inference latency (ms) on the serving container

## 2. Promotion Rule (THE core decision)

A candidate model is PROMOTED if and only if ALL hold:

  recall                       >= 0.85
  ECE                          <= 0.05
  p99 latency                  <= 100 ms
  recall improvement vs incumbent >= +2% (absolute)

Otherwise: REJECTED, with a human-readable reason recorded in the registry.

### The rule that matters most
A model that passes recall but fails ECE is REJECTED. This is the
negative result we will quote later. A test enforces it.

## 3. Rollback Triggers

Automatic rollback if, over a 5-minute sliding window:

  p50 latency       > 200 ms
  error rate        > 1%
  drift statistic   > 2 sigma from reference distribution

Manual rollback: always available via one command.
Rollback target: the last PROMOTED incumbent. Never a rejected model.

## 4. Audit / Logging (what proves each decision)

Every promotion / rejection / rollback writes a record:

  model_hash          sha256 of the model artifact
  metrics             {recall, ECE, p99_latency, ...}
  rule_version        git SHA of the gate code
  decision            PROMOTE | REJECT | ROLLBACK
  reason              human-readable string (empty only for PROMOTE)
  timestamp           UTC ISO-8601
  actor               "auto" | "human:<id>"

The registry must answer: "show me every rejected model and why."

## 5. Measured vs Estimated

MEASURED (reported as numbers, no rounding games):
  - p50 / p95 / p99 latency (ms)
  - throughput (req/s)
  - error rate (%)
  - drift statistic (sigma)
  - rollback duration (wall clock seconds)

ESTIMATED (labelled as such):
  - business impact of a rejected model (do not fake precision)

## 6. Non-Goals (guardrails — do not drift into these)

  - No new model, dataset, or domain
  - No LLM / RAG / agents in this repo
  - No Grafana dashboards until Phases 1-6 complete
  - No new cloud account — Docker Compose only
  - No feature store
  - Do not start a fresh repo — evolve mlops-pipeline

## 7. Phase Gates

  Phase 1 (gate)      -> tests/gate/test_calibration_rejection.py GREEN
  Phase 2 (registry)  -> 2 candidates recorded: 1 promoted, 1 rejected
  Phase 3 (serving)   -> two models serving; latency numbers recorded
  Phase 4 (drift)     -> shifted inputs fire drift; logged
  Phase 5 (rollback)  -> failure injection -> auto rollback; time recorded
  Phase 6 (docs)      -> README + FAILURE_REPORT.md with 3 numbers + 2 stories

## 8. Open Questions (fill in before Phase 1)

  - Q1: Exact validation set + hash?
  - Q2: ECE bin count (default 10) — justify or change
  - Q3: Drift statistic choice (PSI? KS? mean-shift?) — pick ONE
  - Q4: What "improvement vs incumbent" means if incumbent is absent
        (first-ever promotion)? Default: skip the margin rule.
