from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.database import initialize_demo_database  # noqa: E402
from app.service import answer_question  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Day 1 vertical-slice demo.")
    parser.add_argument("question", help="Natural-language business question")
    parser.add_argument("--reset", action="store_true", help="Rebuild the generated demo database")
    args = parser.parse_args()

    db_path = PROJECT_ROOT / "data" / "runtime" / "demo.db"
    seed_path = PROJECT_ROOT / "data" / "synthetic" / "breeding_events.json"
    knowledge_path = PROJECT_ROOT / "data" / "knowledge" / "metrics.md"
    if args.reset or not db_path.exists():
        initialize_demo_database(db_path, seed_path)

    response = answer_question(args.question, db_path, knowledge_path)
    print(json.dumps(response.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

