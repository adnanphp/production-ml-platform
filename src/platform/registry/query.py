"""
The two questions the registry must answer (DESIGN.md §4):
  - "show me every rejected model and why"
  - "what is the history of this model hash"
"""
from __future__ import annotations

import json
from src.platform.registry.store import RegistryStore


def list_rejected(store: RegistryStore) -> list[dict]:
    rows = store._conn.execute(
        "SELECT model_hash, reason, failed_rules, timestamp "
        "FROM decisions WHERE decision = 'REJECT' ORDER BY id ASC"
    ).fetchall()
    return [
        {
            "model_hash": r["model_hash"],
            "reason": r["reason"],
            "failed_rules": json.loads(r["failed_rules"]),
            "timestamp": r["timestamp"],
        }
        for r in rows
    ]


def history(store: RegistryStore, model_hash: str) -> list[dict]:
    """Full row history for one model hash, oldest first."""
    return store.get_by_model_hash(model_hash)
