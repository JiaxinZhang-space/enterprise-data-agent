from __future__ import annotations

from pathlib import Path

from app.models import AgentResponse
from app.router import route_question
from app.tools import lookup_metric_definition, query_mismatch_rate


def answer_question(question: str, db_path: Path, knowledge_path: Path) -> AgentResponse:
    decision = route_question(question)

    if decision.route == "blocked":
        return AgentResponse(
            status="blocked",
            question=question,
            route=decision.route,
            route_reason=decision.reason,
            answer="请求已拒绝：演示系统只允许只读分析，不执行写入或结构变更。",
            warnings=["Day 1 使用意图级前置拦截；SQLGlot AST 和数据库只读角色尚未接入。"],
        )

    if decision.route == "clarify":
        return AgentResponse(
            status="needs_clarification",
            question=question,
            route=decision.route,
            route_reason=decision.reason,
            answer=decision.reason,
        )

    if decision.route == "knowledge":
        result = lookup_metric_definition(knowledge_path)
        return AgentResponse(
            status=result["status"],
            question=question,
            route=decision.route,
            route_reason=decision.reason,
            answer=result["answer"],
            citations=result["citations"],
            warnings=["当前是关键词章节检索基线，不是向量 RAG；Embedding/Chroma 在 Day 4 接入。"],
        )

    result = query_mismatch_rate(db_path=db_path, **decision.parameters)
    return AgentResponse(
        status=result["status"],
        question=question,
        route=decision.route,
        route_reason=decision.reason,
        answer=result["answer"],
        sql=result["sql"],
        sql_parameters=result["parameters"],
        data={key: value for key, value in result.items() if key not in {"status", "answer", "sql", "parameters"}},
        warnings=["当前 SQL 来自受控指标模板，不是 LLM 自由生成的 SQL。"],
    )

