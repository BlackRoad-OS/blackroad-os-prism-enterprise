# Prism Console Compliance Engine

The compliance engine exposes a FastAPI application that evaluates onboarding
requests against concrete policy rules and persists decisions to SQLite. It is
an end-to-end slice of functionality that turns marketing copy into a running
service.

## Running the API

```bash
uvicorn services.compliance_engine.app:create_app --factory --reload
```

By default the service stores decisions in `data/compliance/events.sqlite`. Set
`PRISM_COMPLIANCE_DB` to point at a different location when starting the app:

```bash
PRISM_COMPLIANCE_DB=/tmp/events.sqlite \
uvicorn services.compliance_engine.app:create_app --factory --reload
```

## Endpoints

### `POST /v1/compliance/account-opening`

Evaluates an account opening request. On success it returns the persisted
record, including the status and any violations. When the payload fails a
policy check the response contains `status="rejected"` with descriptive
violations.

### `GET /v1/compliance/events/{client_id}`

Returns the stored compliance history for a client. Responds with HTTP 404 if
no events exist.

### `GET /v1/compliance/disclosures`

Lists the disclosures enforced by the policy module so that UIs can surface the
requirements alongside onboarding forms.

## Tests

Execute the targeted unit tests with:

```bash
pytest tests/unit/test_compliance_engine.py
```

The suite uses FastAPI's `TestClient` to exercise the API and confirms that
results are persisted.
