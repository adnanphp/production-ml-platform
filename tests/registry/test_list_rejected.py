from src.platform.registry import RegistryStore, list_rejected
from tests.registry._helpers import promote_record, reject_record


def test_list_rejected_returns_only_rejections(tmp_path):
    db = tmp_path / "reg.db"
    with RegistryStore(db) as store:
        store.insert(promote_record(model_hash="p1"))
        store.insert(reject_record(model_hash="r1"))
        store.insert(promote_record(model_hash="p2"))
        store.insert(reject_record(model_hash="r2"))
        rejected = list_rejected(store)

    hashes = [r["model_hash"] for r in rejected]
    assert hashes == ["r1", "r2"]
    for r in rejected:
        assert r["reason"]           # never empty
        assert "ece" in r["failed_rules"]


def test_list_rejected_empty_when_none(tmp_path):
    db = tmp_path / "reg.db"
    with RegistryStore(db) as store:
        store.insert(promote_record(model_hash="p1"))
        assert list_rejected(store) == []
