# SQL / ORM Query Perf Inspector

A runnable Python pet project for inspecting SQL queries, highlighting slow queries, and detecting likely ORM N+1 patterns through a web dashboard.

## Features

- FastAPI dashboard with query statistics
- SQLAlchemy engine instrumentation using engine events
- Slow-query alerts with configurable threshold
- Heuristic N+1 detector based on repeated normalized `SELECT` fingerprints
- Query history, query fingerprints, execution duration, and parameter preview
- Demo endpoints for healthy eager loading, intentional N+1, and a delay demo
- SQLite database seeded automatically
- JSON API and tests
- Dockerfile and Compose configuration

> N+1 detection is heuristic. Repeated queries can be legitimate; review findings in context. This is a development/profiling tool, not a production SQL proxy.

## Run on Windows PowerShell

Requires Python 3.11+.

```powershell
cd sql-orm-query-perf-inspector
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run without activating the environment:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open the dashboard at http://127.0.0.1:8000 and API docs at http://127.0.0.1:8000/docs.

## Try it

1. Click **Run healthy demo** to load authors and books using eager loading.
2. Click **Trigger N+1 demo** to issue one query for authors and one lazy query per author.
3. Review alerts and recent SQL history. The detector groups identical normalized SELECT statements in a short time window.
4. Click **Run slow demo** to test the demo endpoint. Note: it adds an application delay; SQL instrumentation measures SQL execution time, not the total route duration.

## Configuration

| Environment variable | Default | Meaning |
|---|---:|---|
| `DATABASE_URL` | `sqlite:///./inspector.db` | SQLAlchemy database URL |
| `SLOW_QUERY_MS` | `100` | SQL duration threshold in milliseconds |
| `N1_THRESHOLD` | `3` | Repeated SELECT count needed for a candidate |
| `QUERY_HISTORY_LIMIT` | `500` | In-memory event history limit |
| `N1_WINDOW_SECONDS` | `10` | Time window for N+1 heuristic |

## API

- `GET /health`
- `GET /api/summary`
- `GET /api/queries?limit=100`
- `GET /api/alerts`
- `POST /api/demo/healthy`
- `POST /api/demo/n-plus-one`
- `POST /api/demo/slow`
- `POST /api/clear`

## Architecture

```text
FastAPI routes / demo service
          |
          v
SQLAlchemy Engine events
(before_cursor_execute / after_cursor_execute)
          |
          v
QueryStore: duration + normalized fingerprint + parameters
          |
          +----> Slow-query alerts
          +----> N+1 heuristic
          |
          v
Web dashboard + JSON API
```

## Tests

```powershell
python -m pytest -q
```

## Next steps

1. Correlate queries with request IDs so repeated queries are grouped per HTTP request.
2. Add PostgreSQL integration and explain-plan capture.
3. Persist history instead of keeping it in memory.
4. Add a real ORM sample application and benchmark suite.
5. Add AI explanations after the core detector is validated.

## License

MIT. See `LICENSE`.
