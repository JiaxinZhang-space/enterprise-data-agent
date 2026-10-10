from __future__ import annotations

import re

from app.models import RouteDecision


_UNSAFE_PATTERN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|attach|pragma)\b"
    r"|删除|删表|写入|修改数据|清空",
    re.IGNORECASE,
)
_YEAR_MONTH_PATTERN = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月")
_COMPARE_MONTH_PATTERN = re.compile(r"比\s*(\d{1,2})\s*月")
_FARM_PATTERN = re.compile(r"([A-Za-z0-9]+)\s*场")


def route_question(question: str) -> RouteDecision:
    normalized = question.strip()
    if not normalized:
        return RouteDecision("clarify", "问题为空，需要补充查询目标。")

    if _UNSAFE_PATTERN.search(normalized):
        return RouteDecision("blocked", "检测到写操作或危险 SQL 意图；当前系统只允许只读分析。")

    if "错配率" in normalized and any(token in normalized for token in ("定义", "口径", "怎么计算", "如何计算")):
        return RouteDecision("knowledge", "问题询问业务定义，应优先检索指标口径文档。")

    if "错配率" in normalized:
        date_match = _YEAR_MONTH_PATTERN.search(normalized)
        farm_match = _FARM_PATTERN.search(normalized)
        if not date_match or not farm_match:
            return RouteDecision(
                "clarify",
                "指标已识别，但缺少明确的年月或场区，不能擅自补全口径。",
            )

        target_year = int(date_match.group(1))
        target_month = int(date_match.group(2))
        compare_match = _COMPARE_MONTH_PATTERN.search(normalized)
        compare_month = int(compare_match.group(1)) if compare_match else None
        compare_year = target_year
        if compare_month is not None and compare_month > target_month:
            compare_year -= 1

        return RouteDecision(
            "metrics",
            "识别到受控指标、场区和时间范围，使用确定性 Metrics SQL。",
            {
                "farm_id": farm_match.group(1).upper(),
                "target_month": f"{target_year:04d}-{target_month:02d}",
                "compare_month": (
                    f"{compare_year:04d}-{compare_month:02d}" if compare_month is not None else None
                ),
            },
        )

    return RouteDecision(
        "clarify",
        "Day 1 基线尚未覆盖该意图，需要说明指标、场区和时间范围。",
    )

