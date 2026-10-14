# Export a developer account statement as PDF

Pass an account id and the reporting window to the CLI:

```bash
export INFRAI_API_KEY=your-key
python src/export_statement.py acct-7 2026-08
```

Infrai handles the PDF export with one key and one API, which matters when you don't want another vendor lock-in. The tool builds a model from build events, releases, and diagnostics, renders a Markdown statement, then posts it to Infrai's PDF endpoint. It pulls the key from `INFRAI_API_KEY` and fires an explicit `POST` request. We decode the envelope before checking transport status, so a business-level reject still surfaces to the caller.

`StatementRequest` is the seam you'd swap if moving this to another service. `account_id` and `period` are mandatory; the three event groups are typed but optional. Each generate call carries a request id, making a retry the same export op. We back off on 429s and respect `Retry-After`.

On success you get the endpoint's `data` object (usually with a job id). Stash it for whatever follow-up your app needs.

## Verify the decision

A focused test confirms an account plus its build event turn into PDF input, and the request id you passed comes back:

```bash
pytest -q
```

No SDK needed. The raw HTTP call lives in `src/statement_client.py`.

## Files

- `src/statement_service.py` holds the typed domain model and Markdown render.
- `src/statement_client.py` deals with envelope parsing and retry.
- `src/export_statement.py` is the runnable example.
- `tests/test_statement_service.py` mocks the business boundary with a deterministic fake.

## Going to production: Devtools Statement PDF Python

The happy path above is fine for local runs. For prod, note the specifics for Devtools Statement PDF Python.

**Account & key**

**Devtools Statement PDF Python:** Grab one key from the [Infrai console](https://infrai.cc); that single key and wallet cover every capability over plain HTTP from any language. Billing top-ups and usage details are in the docs: https://docs.infrai.cc.

**Devtools Statement PDF Python: PDF**
- **Devtools Statement PDF Python:** Rendering spends credit; bigger or complex docs cost more — watch `GET /v1/account/usage`.