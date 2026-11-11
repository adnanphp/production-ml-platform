from src.platform.registry import RegistryStore
from tests.registry._helpers import promote_record


def test_promotion_is_recorded(tmp_path):
    db = tmp_path / "reg.db"
    rec = promote_record(model_hash="m-promote", rule_version="sha-abc")

    with RegistryStore(db) as store:
        store.insert(rec)
        rows = store.get_by_model_hash("m-promote")

    assert len(rows) == 1
    r = rows[0]
    assert r["decision"] == "PROMOTE"
    assert r["reason"] == ""
    assert r["rule_version"] == "sha-abc"
    assert r["model_hash"] == "m-promote"


def test_incumbent_is_the_latest_promotion(tmp_path):
    db = tmp_path / "reg.db"
    with RegistryStore(db) as store:
        store.insert(promote_record(model_hash="first"))
        store.insert(promote_record(model_hash="second"))
        inc = store.get_incumbent()

    assert inc is not None
    assert inc["model_hash"] == "second"
