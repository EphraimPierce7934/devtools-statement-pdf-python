import argparse
import json
from datetime import date

from statement_client import StatementClient
from statement_service import BuildEvent, Diagnostic, ReleaseOperation, StatementRequest, export_statement


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a developer-tools account statement as PDF")
    parser.add_argument("account_id")
    parser.add_argument("period", help="For example 2026-08")
    args = parser.parse_args()
    statement = StatementRequest(
        account_id=args.account_id,
        period=args.period,
        builds=(BuildEvent("linux-release", "passed", date.today()),),
        releases=(ReleaseOperation("v2.4.0", "production", "completed"),),
        diagnostics=(Diagnostic("info", "artifact retention is within policy"),),
    )
    print(json.dumps(export_statement(statement, StatementClient(), f"statement-{args.account_id}-{args.period}"), indent=2))


if __name__ == "__main__":
    main()
