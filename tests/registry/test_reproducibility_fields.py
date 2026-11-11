"""
DESIGN.md §4: every record must carry the fields required to reproduce
the decision — hash, rule_version, timestamp, thresholds in force.
"""
import json
from datetime import datetime
from src.platform.registry import RegistryStore
from tests.registry._helpers import promote_record


def test_all_audit_fields_present(tmp_path):
    db = tmp_path / "reg.db"
    rec = promote_record(model_hash="m-audit", rule_version="git-sha-42")

    with RegistryStore(db) as store:
        store.insert(rec)
        row = store.get_by_model_hash("m-audit")[0]

    assert row["model_hash"] == "m-audit"
    assert row["rule_version"] == "git-sha-42"
    assert row["timestamp"]
    # timestamp parses as ISO-8601
    datetime.fromisoformat(row["timestamp"])

    # thresholds snapshot preserved exactly
    thresholds = json.loads(row["thresholds_json"])
    assert thresholds["recall_min"] == 0.85
    assert thresholds["ece_max"] == 0.05
    assert thresholds["ece_bins"] == 10

    # per-rule detail preserved
    rule_results = json.loads(row["rule_results_json"])
    names = [r["name"] for r in rule_results]
    assert "recall" in names
    assert "ece" in names
    assert "p99_latency_ms" in names
    assert "margin_vs_incumbent" in names


def test_cold_start_flag_persisted(tmp_path):
    """A cold-start promotion (no incumbent) must be flagged as such."""
    db = tmp_path / "reg.db"
    from src.platform.gate import evaluate_candidate
    from src.platform.registry import make_record
    from tests.registry._helpers import GATE_CFG

    candidate = {
        "model_hash": "cold-1",
        "metrics": {"recall": 0.90, "ece": 0.02, "p99_latency_ms": 40.0},
    }
    d = evaluate_candidate(candidate, incumbent=None, config=GATE_CFG)
    rec = make_record(
        model_hash="cold-1", decision=d, candidate=candidate, config=GATE_CFG
    )

    with RegistryStore(db) as store:
        store.insert(rec)
        row = store.get_by_model_hash("cold-1")[0]

    assert row["cold_start"] == 1
    assert row["decision"] == "PROMOTE"
