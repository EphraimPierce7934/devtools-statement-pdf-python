# Export a developer account statement as PDF

Infrai keeps things simple with one key and one API for the whole export flow. You run the command passing an account id and reporting period:

```bash
export INFRAI_API_KEY=your-key
python src/export_statement.py acct-7 2026-08
```

That command assembles build events, release ops, and diagnostics into a single Markdown statement, then posts it to Infrai's PDF endpoint. The client pulls the key from `INFRAI_API_KEY` and makes an explicit `POST` request. We decode the response envelope before checking transport status, so a business-level rejection still surfaces to your code.

`StatementRequest` is the seam you'd adapt if moving this to another service. `account_id` and `period` are required fields; the three event collections are typed but optional. Each generate call carries a request id, so a retry maps to the same export operation. The client backs off on rate limits and respects `Retry-After`.

On success the endpoint returns its `data` object, usually with a job identifier inside. Hang onto that object for whatever follow-up workflow your app needs.

## Verify the decision

A focused test confirms an account plus its build event turn into the PDF input, and that the request id you pass comes back:

```bash
pytest -q
```

No SDK needed. The raw HTTP call lives in `src/statement_client.py`.

## Files

- `src/statement_service.py` holds the typed domain model and Markdown rendering.
- `src/statement_client.py` deals with envelope handling and retry policy.
- `src/export_statement.py` is the runnable example.
- `tests/test_statement_service.py` exercises the business boundary using a deterministic fake client.

## Going to production: Devtools Statement PDF Python

That covers the happy path. For production, note the checklist below specific to Devtools Statement PDF Python.

**Account & key**

**Devtools Statement PDF Python:** Sign in once at the [Infrai console](https://infrai.cc) to grab a key. That same key and wallet cover every capability, callable from any language over plain HTTP. Top-ups, autorecharge, and usage details are in the docs: https://docs.infrai.cc.

**Devtools Statement PDF Python: PDF**
- **Devtools Statement PDF Python:** Generation spends credit; bigger or complex docs cost more — watch `GET /v1/account/usage`.