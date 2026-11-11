"""
SQLite store for DecisionRecords.

Append-only. No UPDATE, no DELETE. If a decision was wrong, record a new
decision — the audit trail stays intact.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.platform.registry.schema import DecisionRecord


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS decisions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    model_hash      TEXT NOT NULL,
    rule_version    TEXT NOT NULL,
    decision        TEXT NOT NULL CHECK (decision IN ('PROMOTE', 'REJECT')),
    reason          TEXT NOT NULL,
    failed_rules    TEXT NOT NULL,   -- JSON list
    recall          REAL NOT NULL,
    ece             REAL NOT NULL,
    p99_latency_ms  REAL NOT NULL,
    thresholds_json TEXT NOT NULL,
    rule_results_json TEXT NOT NULL,
    cold_start      INTEGER NOT NULL,
    timestamp       TEXT NOT NULL,
    actor           TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_decisions_model_hash ON decisions(model_hash);
CREATE INDEX IF NOT EXISTS idx_decisions_decision   ON decisions(decision);
CREATE INDEX IF NOT EXISTS idx_decisions_ts         ON decisions(timestamp);
"""


class RegistryStore:
    def __init__(self, path: str | Path = "registry.db") -> None:
        self.path = Path(path)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA_SQL)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "RegistryStore":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def insert(self, rec: DecisionRecord) -> int:
        import json
        cur = self._conn.execute(
            """
            INSERT INTO decisions (
                model_hash, rule_version, decision, reason, failed_rules,
                recall, ece, p99_latency_ms, thresholds_json, rule_results_json,
                cold_start, timestamp, actor
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                rec.model_hash,
                rec.rule_version,
                rec.decision,
                rec.reason,
                json.dumps(list(rec.failed_rules)),
                rec.recall,
                rec.ece,
                rec.p99_latency_ms,
                rec.thresholds_json,
                rec.rule_results_json,
                int(rec.cold_start),
                rec.timestamp,
                rec.actor,
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    def get_by_model_hash(self, model_hash: str) -> list[dict]:
        rows = self._conn.execute(
            "SELECT * FROM decisions WHERE model_hash = ? ORDER BY id ASC",
            (model_hash,),
        ).fetchall()
        return [dict(r) for r in rows]

    def get_incumbent(self) -> dict | None:
        """The most recent PROMOTE. This is the model currently serving."""
        row = self._conn.execute(
            "SELECT * FROM decisions WHERE decision = 'PROMOTE' "
            "ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return dict(row) if row else None
