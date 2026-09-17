# Adaptive API

A schema-agnostic FastAPI service that fetches paginated JSON from arbitrary external sources and aggregates records by configurable primary keys without hardcoding what shape the source data takes.

Built with a flat Clean Architecture layout: fetch a source once, and the same `/aggregate` endpoint can summarize orders by customer, betting results by player, or any other tabular JSON by whatever keys you pass in at request time.

## About the Developer

Built by Dynitia Mofokeng, a full-stack developer working across .NET, Python,
and Java. This project demonstrates adaptive API design and Clean Architecture principles applied to a schema-agnostic integration problem.

- 🔗 [LinkedIn](https://za.linkedin.com/in/dynitia-khumalo-mofokeng-57b883b5)
- 💻 [GitHub](https://github.com/Kat-Dante)
- ✉️ dynitia95@gmail.com

## Why this exists

Most integrations with external JSON APIs hardcode assumptions about response shape, pagination style, and what fields matter. This project separates those concerns:

- **Pagination** is handled generically, with adapters that detect whether a source returns a flat array or an enveloped `{"items": [...], "has_more": bool}` response.
- **Aggregation keys are runtime configuration**, not code  group by `customer_id` today, `region` tomorrow, without a redeploy.
- **Business logic never touches HTTP or pagination details**  the domain layer only knows about `Record` objects and grouping rules.

## Features

- 🔌 **Adapter-based pagination**  automatically detects flat-array vs. enveloped JSON responses
- 🛡️ **Safety guardrails**  a `max_pages` ceiling prevents runaway loops against misbehaving sources
- ⚙️ **Configurable aggregation**  group by any combination of fields, sum any numeric fields, all via query parameters
- 🚦 **Clear failure semantics**  upstream failures surface as `502 Bad Gateway` with a descriptive message, not a raw `500`
- 📄 **Raw passthrough endpoint**  fetch and return all paginated data unfiltered when you don't need aggregation
- ✅ **Fully tested**  unit tests per layer, integration tests against a mocked HTTP boundary

## Architecture

This project follows Clean Architecture principles with a flat package layout (no wrapping root package):

```
adaptive-api/
├── domain/                    # Business logic  no framework dependencies
│   ├── record.py              # Record wrapper + aggregate() grouping logic
│   └── source_adapter.py      # SourceAdapter protocol (interface)
├── application/                # Orchestrates domain + infrastructure
│   └── fetch.py                # fetch_and_aggregate() use case
├── infrastructure/              # External concerns  HTTP, pagination
│   ├── pagination.py            # fetch_all_pages()  the pagination loop
│   └── adapters.py               # EnvelopeAdapter, FlatListAdapter, detect_adapter()
├── api/                          # HTTP boundary
│   ├── main.py                    # FastAPI app + router registration
│   └── router/
│       └── data.py                 # /aggregate and /data endpoints
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   └── infrastructure/
│   ├── integration/
│   └── conftest.py
├── pytest.ini
└── requirements.txt
```

### Dependency direction

```
api/  →  application/  →  domain/
              ↓
      infrastructure/  →  domain/
```

- **`domain/`** has zero dependencies on FastAPI, httpx, or any other framework. It only knows about `Record` objects and aggregation rules.
- **`application/`** orchestrates a use case (fetch, then aggregate) by depending on `infrastructure/` and `domain/`.
- **`infrastructure/`** implements the actual HTTP fetching and pagination, translating raw JSON into `Record` objects.
- **`api/`** is the thinnest layer  it parses query parameters and calls into `application/`.

Because this is a flat layout, internal imports reference each top-level folder directly (e.g. `from domain.record import Record`), rather than through a wrapping package name.

## Getting started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone <your-repo-url>
cd adaptive-api
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### `requirements.txt`

```
fastapi
uvicorn
httpx
pytest
pytest-asyncio
respx
```

### Running the server

```bash
uvicorn api.main:app --reload
```

The API is now available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

### Running tests

```bash
pytest -v
```

Run a specific layer:
```bash
pytest tests/unit -v          # fast, no network calls
pytest tests/integration -v   # full request/response cycle, HTTP mocked
```

## API reference

### `GET /aggregate`

Fetches all paginated data from `source_url`, then groups and sums it by the given keys.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `source_url` | string | ✅ | External JSON endpoint to pull from |
| `primary_keys` | array\<string\> | ❌ | Fields to group by. Omit to skip aggregation and receive raw data. |
| `sum_fields` | array\<string\> | ❌ | Numeric fields to sum per group. Omit to skip aggregation and receive raw data. |

If either `primary_keys` or `sum_fields` is omitted, the endpoint returns all fetched records unaggregated (equivalent to `/data`), with `"aggregated": false` in the response.

**Example  aggregated:**
```
GET /aggregate?source_url=https://api.example.com/orders&primary_keys=customer_id&sum_fields=total_amount
```
```json
{
  "count": 2,
  "aggregated": true,
  "results": [
    {"customer_id": "A", "total_amount": 80},
    {"customer_id": "B", "total_amount": 20}
  ]
}
```

**Example  keys omitted (raw passthrough):**
```
GET /aggregate?source_url=https://api.example.com/orders
```
```json
{
  "count": 3,
  "aggregated": false,
  "results": [
    {"customer_id": "A", "total_amount": 50},
    {"customer_id": "A", "total_amount": 30},
    {"customer_id": "B", "total_amount": 20}
  ]
}
```

### `GET /data`

Fetches all paginated data from `source_url` and returns it unfiltered  no grouping, no summing.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `source_url` | string | ✅ | External JSON endpoint to pull from |

**Example:**
```
GET /data?source_url=https://jsonplaceholder.typicode.com/posts
```

### `GET /hello`

Basic health check  returns `{"message": "Developed by : Dynitia"}`. Useful for confirming the server is running.

## Supported source shapes

The pagination layer auto-detects which shape a source uses on its first response, via `infrastructure/adapters.py`:

**Enveloped (paginated):**
```json
{
  "items": [ { ... }, { ... } ],
  "has_more": true
}
```
The client follows `page`/`page_size` query parameters, incrementing `page` until `has_more` is `false`.

**Flat array (single page, no pagination metadata):**
```json
[ { ... }, { ... } ]
```
Treated as a complete, single-page result.

### Adding support for a new source shape

Implement the `SourceAdapter` protocol in `domain/source_adapter.py`:

```python
class MyCursorAdapter:
    def extract_items(self, payload): ...
    def has_more(self, payload): ...
    def next_page_params(self, current_params, payload): ...
```

Then wire it into `detect_adapter()` in `infrastructure/adapters.py`. No changes to `fetch_all_pages()` or any other layer are needed this is the seam that keeps source-specific logic isolated.

## Error handling

Failures reaching or parsing an external source surface as `502 Bad Gateway` (not a generic `500`), with a message describing what went wrong:

| Failure | Response |
|---|---|
| Source unreachable (DNS/connection failure) | `502`  "Could not reach source_url: ..." |
| Source returns non-2xx status | `502`  "Source returned {status}: ..." |
| Source returns invalid JSON | `502`  "Source did not return valid JSON: ..." |
| Source never terminates pagination | `502`  "Source exceeded max_pages ({n}) without terminating: ..." |

The `max_pages` guard (default: 1000) protects against a misconfigured or misbehaving source that always reports `has_more: true`.

## Known limitations

This is an early-stage implementation. The following are not yet handled and are worth knowing about before pointing this at a production source:

- **No cursor-based or offset-based pagination**  only numeric `page`/`page_size` and flat-array sources are supported today.
- **No retry/backoff logic**  a transient failure on any page fails the whole request rather than retrying.
- **No authentication support**  `source_url` is fetched with no headers or credentials; sources requiring auth aren't yet supported.
- **No persistent source configuration**  sources are specified per-request via `source_url`, with no registry, secrets management, or startup validation.
- **No observability**  no metrics, structured logging, or per-source counters currently exist.
- **Duplicate key handling is sum-only**  there's no support for first-wins/latest-wins/merge conflict resolution when the same primary key appears with conflicting non-numeric fields.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/cursor-pagination`)
3. Add tests for new behavior under the matching layer in `tests/`
4. Ensure `pytest -v` passes
5. Open a pull request

## License

 MIT, Apache 2.0, GPL v3
