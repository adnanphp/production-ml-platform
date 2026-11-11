# Failure Report

> Run `make failure-injection` to produce the numbers below, then replace the
> `<PLACEHOLDER>` markers with the printed values. The rest of the prose is
> yours to edit — this skeleton structures it, it does not write it for you.

## Scenario

A candidate model (`candidate-A`) was promoted through the gate, served
alongside the incumbent at a 90/10 split, and then faced a deliberately
shifted input distribution. The drift detector fired; the trigger fired;
the rollback executed. This is what happened, with numbers.

## What broke

Traffic shifted +2.5σ on every feature. Not a subtle distributional creep —
a step change, the kind that would happen if an upstream data source
changed format or a feature pipeline broke.

## What the system did (measured)

| Metric | Value |
|---|---|
| Throughput (n=500) | `<PLACEHOLDER>` req/s |
| Incumbent latency p50 / p95 / p99 | `<PLACEHOLDER>` / `<PLACEHOLDER>` / `<PLACEHOLDER>` ms |
| Candidate latency p50 / p95 / p99 | `<PLACEHOLDER>` / `<PLACEHOLDER>` / `<PLACEHOLDER>` ms |
| Drift detector fired | yes |
| Drift reason | `<PLACEHOLDER>` |
| Trigger reasons | `<PLACEHOLDER>` |
| Rollback duration | `<PLACEHOLDER>` ms |
| Records in registry for candidate-A | `<PLACEHOLDER>` |

## What I would change

Edit this section in your own words. Some starting questions:

- The rollback fired on drift alone. Was that the right call? What if
  p50 latency had been healthy but drift had fired? Should the system have
  rolled back anyway?
- The threshold was 2σ mean-shift on any feature. Would you tighten to 2.5σ?
  Loosen to 1.5σ? What's the tradeoff — more safety vs. more false positives?
- If rollback failed (e.g. incumbent artifact was missing), what would
  happen? The current system would raise. Should it fall back to a
  "serve nothing but return 503" mode instead?

## What worked

Edit this too. Some candidates:

- The gate rejected a candidate model in an earlier run that passed recall
  but failed calibration. That's the negative-result story to quote.
- The registry recorded both the promotion and the rollback, so the full
  history of candidate-A is queryable.
- `test_no_false_positive_on_same_distribution` stayed green — the system
  did **not** roll back on healthy traffic during setup.

---

## Negative result to quote in interviews

"The gate rejected a candidate that scored 0.95 recall but had ECE 0.20.
Accuracy alone would have promoted it. The calibration gate caught it.
That's the whole point of the project."

The exact test that enforces this:
`tests/gate/test_calibration_rejection.py::test_high_recall_bad_calibration_is_rejected`
