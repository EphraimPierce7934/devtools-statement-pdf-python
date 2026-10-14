from datetime import date

from statement_service import BuildEvent, StatementRequest, export_statement


class RecordingClient:
    def __init__(self):
        self.markdown = ""

    def generate(self, markdown, request_id):
        self.markdown = markdown
        return {"job_id": request_id}


def test_statement_contains_events_and_uses_request_id():
    client = RecordingClient()
    result = export_statement(
        StatementRequest("acct-7", "2026-08", builds=(BuildEvent("unit", "passed", date(2026, 8, 3)),)),
        client,
        "statement-acct-7-2026-08",
    )
    assert result == {"job_id": "statement-acct-7-2026-08"}
    assert "acct-7" in client.markdown
    assert "2026-08-03 | unit | passed" in client.markdown
