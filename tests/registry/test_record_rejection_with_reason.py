from src.platform.registry import RegistryStore
from tests.registry._helpers import reject_record


def test_rejection_reason_is_persisted(tmp_path):
    db = tmp_path / "reg.db"
    rec = reject_record(model_hash="m-bad-ece")

    # reason produced by the gate must be non-empty
    assert rec.reason
    assert "ece" in rec.reason.lower()

    with RegistryStore(db) as store:
        store.insert(rec)
        rows = store.get_by_model_hash("m-bad-ece")

    assert rows[0]["decision"] == "REJECT"
    assert "ece" in rows[0]["reason"].lower()
    assert rows[0]["reason"] == rec.reason


def test_failed_rules_persisted_as_json(tmp_path):
    import json
    db = tmp_path / "reg.db"
    with RegistryStore(db) as store:
        store.insert(reject_record(model_hash="m-bad"))
        rows = store.get_by_model_hash("m-bad")

    failed = json.loads(rows[0]["failed_rules"])
    assert "ece" in failed
