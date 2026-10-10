from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class RouteDecision:
    route: str
    reason: str
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    status: str
    question: str
    route: str
    route_reason: str
    answer: str
    sql: str | None = None
    sql_parameters: list[Any] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    citations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

