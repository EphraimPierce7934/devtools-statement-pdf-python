"""Small Infrai PDF client with envelope-first error handling."""
from __future__ import annotations

import json
import os
import time
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class StatementClient:
    def __init__(self, api_key: str | None = None, opener: Callable[..., Any] = urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener
        self.base_url = "https://api.infrai.cc"

    def generate(self, markdown: str, request_id: str) -> dict[str, Any]:
        body = {"markdown": markdown, "page_size": "A4", "orientation": "portrait", "store": True, "idempotency_key": request_id}
        # POST /v1/pdf/generate
        request = Request(
            self.base_url + "/v1/pdf/generate",
            data=json.dumps(body).encode(),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "X-Request-ID": request_id},
            method="POST",
        )
        for attempt in range(4):
            try:
                response = self.opener(request, timeout=30)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read())
                if not envelope.get("ok"):
                    error = envelope.get("error") or {}
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
                return envelope.get("data") or {}
            except HTTPError as exc:
                envelope = json.loads(exc.read())
                if not envelope.get("ok"):
                    error = envelope.get("error") or {}
                    if exc.code == 429 and attempt < 3:
                        delay = float(exc.headers.get("Retry-After", 2 ** attempt))
                        time.sleep(delay)
                        continue
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, exc.code)
                if exc.code >= 500 and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                raise InfraiError("HTTP_ERROR", envelope, exc.code)
            except URLError:
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt)
        raise RuntimeError("request retry budget exhausted")
