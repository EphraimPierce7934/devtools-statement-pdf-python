import json

from statement_client import StatementClient


def test_retries_use_the_same_idempotency_key(monkeypatch):
    requests = []

    class Response:
        status = 200

        def read(self):
            return b'{"ok": true, "data": {"pdf_id": "pdf-1"}}'

    def opener(request, timeout):
        requests.append(json.loads(request.data))
        if len(requests) == 1:
            from urllib.error import URLError

            raise URLError("temporary failure")
        return Response()

    monkeypatch.setattr("statement_client.time.sleep", lambda _: None)
    result = StatementClient(api_key="test", opener=opener).generate("# Statement", "statement-acct-7-2026-08")

    assert result == {"pdf_id": "pdf-1"}
    assert [body["idempotency_key"] for body in requests] == ["statement-acct-7-2026-08"] * 2
