# RightsAI Nigeria — Backend

AI-powered legal **information** platform that helps Nigerian citizens understand
potential rights issues, relevant laws, evidence to preserve, agencies to
contact, and recommended next actions.

> ⚖️ **Legal notice:** This system provides **legal information only — not legal
> advice.** It uses cautious language ("may constitute", "could indicate",
> "potentially involves") and includes a disclaimer in every response. It does
> not create a lawyer–client relationship.

## Features

- `POST /api/analyze` — turns a free-text complaint into structured legal
  information (category, facts, possible rights, relevant laws, evidence,
  recommended actions, agencies, risk level, disclaimer).
- `POST /api/letter` — generates a formal, cautious complaint letter for
  Nigerian institutions from a complaint + its analysis.
- `GET /health` — health/readiness probe.
- Rule-based **legal mapper** with 20+ starter mappings that enriches every
  analysis with baseline rights, constitutional sections, laws, and agencies.
- **Async-first** OpenAI integration with JSON-output enforcement and graceful
  error handling.
- **Offline mode:** with no `OPENAI_API_KEY`, the service falls back to
  deterministic, rule-based output so you can develop and test without a key.
- **RAG-ready** abstractions (`Retriever`, `VectorStore`) with TODOs for future
  PostgreSQL + pgvector integration.

## Tech stack

- Python 3.12+
- FastAPI + Pydantic v2 + pydantic-settings
- OpenAI SDK (async)
- PostgreSQL / pgvector-ready architecture (placeholders only for now)

## Project structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app: CORS, health, OpenAPI, lifespan
│   ├── api/
│   │   ├── analyze.py           # POST /api/analyze
│   │   └── letter.py            # POST /api/letter
│   ├── services/
│   │   ├── llm_service.py       # async OpenAI + offline fallback
│   │   ├── legal_mapper.py      # 20+ rule-based mappings
│   │   └── prompt_engine.py     # load + cache prompt templates
│   ├── rag/
│   │   ├── vector_store.py      # VectorStore interface (placeholder)
│   │   └── retriever.py         # Retriever interface (placeholder)
│   ├── prompts/
│   │   ├── analyze.txt
│   │   └── letter.txt
│   ├── schemas/
│   │   └── incident.py          # Pydantic request/response models
│   └── core/
│       ├── config.py            # env-based settings
│       └── logging_config.py    # structured JSON logging
├── tests/
│   └── test_api.py
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## Setup

All commands are run from the `backend/` directory.

```bash
cd backend

# 1. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# (optional) edit .env and add your OPENAI_API_KEY
```

## Running

```bash
uvicorn app.main:app --reload
```

Then open:

- Swagger UI: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/health

### Example: analyze

```bash
curl -s -X POST http://127.0.0.1:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"complaint":"Police officers arrested me and detained me for two days without telling me why."}'
```

### Example: letter

Pass the analysis you got back from `/api/analyze`:

```bash
curl -s -X POST http://127.0.0.1:8000/api/letter \
  -H "Content-Type: application/json" \
  -d '{"complaint":"Police officers arrested me and detained me for two days without telling me why.","analysis": { ... }}'
```

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | _(empty)_ | OpenAI key. If empty, runs in offline mode. |
| `OPENAI_MODEL` | `gpt-4o-mini` | Chat model used for analysis/letters. |
| `OPENAI_TIMEOUT_SECONDS` | `30` | Per-request timeout. |
| `OPENAI_MAX_RETRIES` | `2` | SDK retry count. |
| `CORS_ORIGINS` | `*` | Comma-separated allowed origins. |
| `LOG_LEVEL` | `INFO` | Logging level. |
| `DATABASE_URL` | _(empty)_ | Reserved for future pgvector RAG. |

## Testing & quality

```bash
cd backend
pytest                 # tests (run fully offline)
ruff check .           # lint
mypy app               # type check
```

## Roadmap (RAG)

`app/rag/` ships with clean interfaces only. Future work (see `TODO(pgvector)`
comments):

- Implement a pgvector-backed `VectorStore`.
- Embed and index Nigerian legal corpora.
- Inject retrieved context into the analyze/letter prompts for grounded output.
