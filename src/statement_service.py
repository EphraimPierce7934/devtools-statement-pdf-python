from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from statement_client import StatementClient


@dataclass(frozen=True)
class BuildEvent:
    name: str
    status: str
    occurred_on: date


@dataclass(frozen=True)
class ReleaseOperation:
    version: str
    environment: str
    status: str


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    message: str


@dataclass(frozen=True)
class StatementRequest:
    account_id: str
    period: str
    builds: tuple[BuildEvent, ...] = ()
    releases: tuple[ReleaseOperation, ...] = ()
    diagnostics: tuple[Diagnostic, ...] = ()


def render_markdown(statement: StatementRequest) -> str:
    lines = [f"# Account statement: {statement.account_id}", f"Period: {statement.period}", "", "## Build events"]
    lines += [f"- {e.occurred_on.isoformat()} | {e.name} | {e.status}" for e in statement.builds] or ["- None"]
    lines += ["", "## Release operations"]
    lines += [f"- {r.version} | {r.environment} | {r.status}" for r in statement.releases] or ["- None"]
    lines += ["", "## Developer diagnostics"]
    lines += [f"- {d.severity}: {d.message}" for d in statement.diagnostics] or ["- None"]
    return "\n".join(lines)


def export_statement(statement: StatementRequest, client: StatementClient | Any, request_id: str) -> dict[str, Any]:
    if not statement.account_id.strip() or not statement.period.strip():
        raise ValueError("account_id and period are required")
    return client.generate(render_markdown(statement), request_id)
