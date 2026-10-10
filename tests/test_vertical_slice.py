from __future__ import annotations

import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from app.database import initialize_demo_database
from app.service import answer_question


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class VerticalSliceTest(unittest.TestCase):
    def setUp(self) -> None:
        test_runtime = PROJECT_ROOT / "data" / "runtime" / "tests"
        test_runtime.mkdir(parents=True, exist_ok=True)
        self.temp_dir = tempfile.TemporaryDirectory(dir=test_runtime)
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "demo.db"
        self.seed_path = PROJECT_ROOT / "data" / "synthetic" / "breeding_events.json"
        self.knowledge_path = PROJECT_ROOT / "data" / "knowledge" / "metrics.md"
        initialize_demo_database(self.db_path, self.seed_path)

    def test_month_over_month_metric_uses_valid_events_only(self) -> None:
        response = answer_question(
            "2026年9月A场的错配率是多少，比8月提高了多少个百分点？",
            self.db_path,
            self.knowledge_path,
        )

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.route, "metrics")
        self.assertEqual(response.data["target"]["valid_count"], 5)
        self.assertEqual(response.data["target"]["mismatch_count"], 2)
        self.assertEqual(response.data["target"]["mismatch_rate_pct"], 40.0)
        self.assertEqual(response.data["compare"]["mismatch_rate_pct"], 25.0)
        self.assertEqual(response.data["change_percentage_points"], 15.0)

    def test_definition_returns_traceable_source(self) -> None:
        response = answer_question("错配率是怎么计算的？", self.db_path, self.knowledge_path)

        self.assertEqual(response.status, "ok")
        self.assertEqual(response.route, "knowledge")
        self.assertIn("分母为 0 时返回 NULL", response.answer)
        self.assertEqual(len(response.citations), 1)

    def test_write_intent_is_blocked_without_changing_data(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as connection:
            before = connection.execute("SELECT COUNT(*) FROM dwd_breeding_event").fetchone()[0]

        response = answer_question(
            "DELETE FROM dwd_breeding_event",
            self.db_path,
            self.knowledge_path,
        )

        with closing(sqlite3.connect(self.db_path)) as connection:
            after = connection.execute("SELECT COUNT(*) FROM dwd_breeding_event").fetchone()[0]

        self.assertEqual(response.status, "blocked")
        self.assertEqual(response.route, "blocked")
        self.assertEqual(before, after)

    def test_ambiguous_question_requests_clarification(self) -> None:
        response = answer_question("上个月的达成率？", self.db_path, self.knowledge_path)

        self.assertEqual(response.status, "needs_clarification")
        self.assertEqual(response.route, "clarify")


if __name__ == "__main__":
    unittest.main()

