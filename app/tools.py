from __future__ import annotations

from pathlib import Path
from typing import Any

from app.database import execute_read_only


MISMATCH_RATE_SQL = """
SELECT
    substr(event_date, 1, 7) AS month,
    SUM(CASE WHEN status = 'valid' THEN 1 ELSE 0 END) AS valid_count,
    SUM(
        CASE WHEN status = 'valid' AND is_rule_match = 0 THEN 1 ELSE 0 END
    ) AS mismatch_count,
    ROUND(
        100.0 * SUM(
            CASE WHEN status = 'valid' AND is_rule_match = 0 THEN 1 ELSE 0 END
        ) / NULLIF(SUM(CASE WHEN status = 'valid' THEN 1 ELSE 0 END), 0),
        2
    ) AS mismatch_rate_pct
FROM dwd_breeding_event
WHERE farm_id = ?
  AND substr(event_date, 1, 7) IN (?, ?)
GROUP BY substr(event_date, 1, 7)
ORDER BY month
""".strip()


def query_mismatch_rate(
    db_path: Path,
    farm_id: str,
    target_month: str,
    compare_month: str | None,
) -> dict[str, Any]:
    baseline_month = compare_month or target_month
    parameters = [farm_id, baseline_month, target_month]
    rows = execute_read_only(db_path, MISMATCH_RATE_SQL, parameters)
    by_month = {row["month"]: row for row in rows}
    target = by_month.get(target_month)

    if target is None:
        return {
            "status": "not_found",
            "answer": f"未找到 {target_month} 的 {farm_id} 场有效配种数据。",
            "rows": rows,
            "sql": MISMATCH_RATE_SQL,
            "parameters": parameters,
        }

    target_rate = target["mismatch_rate_pct"]
    answer = (
        f"{target_month} 的 {farm_id} 场错配率为 {target_rate:.2f}%"
        f"（错配 {target['mismatch_count']} 次 / 有效配种 {target['valid_count']} 次）"
    )
    result: dict[str, Any] = {
        "status": "ok",
        "target": target,
        "rows": rows,
        "sql": MISMATCH_RATE_SQL,
        "parameters": parameters,
    }

    if compare_month is not None:
        baseline = by_month.get(compare_month)
        if baseline is None or baseline["mismatch_rate_pct"] is None:
            result["status"] = "partial"
            answer += f"；但 {compare_month} 缺少可比较数据。"
        else:
            change = round(target_rate - baseline["mismatch_rate_pct"], 2)
            direction = "提高" if change >= 0 else "下降"
            answer += f"，比 {compare_month} {direction} {abs(change):.2f} 个百分点。"
            result["compare"] = baseline
            result["change_percentage_points"] = change

    result["answer"] = answer
    return result


def lookup_metric_definition(knowledge_path: Path, heading: str = "错配率") -> dict[str, Any]:
    lines = knowledge_path.read_text(encoding="utf-8").splitlines()
    marker = f"## {heading}"
    try:
        start = lines.index(marker)
    except ValueError:
        return {"status": "not_found", "answer": "未检索到对应指标定义。", "citations": []}

    section: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        if line.strip():
            section.append(line.strip().lstrip("- "))

    return {
        "status": "ok",
        "answer": "；".join(section),
        "citations": [f"{knowledge_path.as_posix()}#{heading}"],
    }

