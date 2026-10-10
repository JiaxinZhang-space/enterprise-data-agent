from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any


SCHEMA_SQL = """
CREATE TABLE dwd_breeding_event (
    event_id TEXT PRIMARY KEY,
    event_date TEXT NOT NULL,
    farm_id TEXT NOT NULL,
    sow_line_id TEXT NOT NULL,
    boar_line_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('valid', 'invalid')),
    is_rule_match INTEGER NOT NULL CHECK (is_rule_match IN (0, 1))
)
""".strip()


def initialize_demo_database(db_path: Path, seed_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    events = json.loads(seed_path.read_text(encoding="utf-8"))
    with closing(sqlite3.connect(db_path)) as connection:
        connection.execute("DROP TABLE IF EXISTS dwd_breeding_event")
        connection.execute(SCHEMA_SQL)
        connection.executemany(
            """
            INSERT INTO dwd_breeding_event (
                event_id, event_date, farm_id, sow_line_id, boar_line_id, status, is_rule_match
            ) VALUES (
                :event_id, :event_date, :farm_id, :sow_line_id, :boar_line_id, :status,
                :is_rule_match
            )
            """,
            events,
        )
        connection.commit()


def execute_read_only(db_path: Path, sql: str, parameters: list[Any]) -> list[dict[str, Any]]:
    uri = f"{db_path.resolve().as_uri()}?mode=ro"
    with closing(sqlite3.connect(uri, uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(sql, parameters).fetchall()
    return [dict(row) for row in rows]

