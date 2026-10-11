# SQL / ORM Query Performance Inspector

A Python web application for monitoring SQL query execution, identifying slow queries, and detecting potential ORM **N+1 query problems**.

Built as a portfolio project to demonstrate Python backend development, SQLAlchemy instrumentation, automated testing, and API design.

## Overview

Repeated database queries and inefficient ORM loading strategies can significantly affect application performance. This tool collects SQL execution events, normalizes query fingerprints, tracks execution duration, and raises alerts for suspicious patterns.

The project includes a web dashboard and demo endpoints that make it possible to reproduce and inspect common query-performance issues locally.

## Features

* **SQL query instrumentation** using SQLAlchemy engine events.
* **Slow-query detection** with a configurable execution-time threshold.
* **Heuristic N+1 detection** based on repeated normalized `SELECT` fingerprints.
* **Query history** with execution duration, fingerprints, and parameter previews.
* **Web dashboard** with query statistics and alerts.
* **REST API** for retrieving query information and triggering demos.
* **Demo scenarios** for healthy loading, N+1 behavior, and delayed execution.
* **Automated tests** using pytest.
* **Continuous integration** with GitHub Actions.
* **SQLite database** initialized automatically.
* **Docker and Docker Compose** configuration.

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* SQLite
* pytest
* GitHub Actions
* Docker

## Architecture

```text
                 Web Dashboard
                       |
                 FastAPI Routes
                       |
                SQLAlchemy Engine
                       |
                Engine Event Hooks
                       |
                Query Instrumentation
                       |
          +------------+------------+
          |                         |
     Query History             Alert Detection
          |                  +------+------+
          |                  |             |
    JSON REST API        Slow Queries   N+1 Candidates
```

## Getting Started

### Requirements

* Python 3.11 or newer
* Git

### Run on Windows

Clone the repository and enter the project directory:

```powershell
git clone https://github.com/xdmolodoi/sql-orm-query-perf-inspector.git
cd sql-orm-query-perf-inspector
```

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install pytest httpx
```

Start the application:

```powershell
python -m uvicorn app.main:app --reload
```

Open the following URLs:

* **Dashboard:** http://127.0.0.1:8000/
* **API documentation:** http://127.0.0.1:8000/docs
* **Health check:** http://127.0.0.1:8000/health
* **Query summary:** http://127.0.0.1:8000/api/summary

## Demo Scenarios

Use the dashboard or API documentation to explore the available scenarios.

### Healthy Query Loading

```http
POST /api/demo/healthy
```

Runs a demo using eager loading to avoid issuing a separate lazy-load query for each author.

### N+1 Query Pattern

```http
POST /api/demo/n-plus-one
```

Triggers repeated queries so that the detector can identify a potential N+1 pattern.

### Slow Demo

```http
POST /api/demo/slow
```

Runs a demo endpoint with an application-level delay. SQL instrumentation measures database statement execution time, not total HTTP request duration.

### Inspect Alerts and History

Review the dashboard or call:

```http
GET /api/alerts
GET /api/queries?limit=100
GET /api/summary
```

## API Endpoints

| Method | Endpoint                 | Purpose                 |
| ------ | ------------------------ | ----------------------- |
| GET    | `/health`                | Health check            |
| GET    | `/api/summary`           | Query statistics        |
| GET    | `/api/queries?limit=100` | Recent query history    |
| GET    | `/api/alerts`            | Detected alerts         |
| POST   | `/api/demo/healthy`      | Healthy loading demo    |
| POST   | `/api/demo/n-plus-one`   | N+1 demo                |
| POST   | `/api/demo/slow`         | Slow demo               |
| POST   | `/api/clear`             | Clear collected history |

Interactive API documentation is available at `/docs`.

## Configuration

The application supports the following environment variables:

| Variable              | Default                    | Description                          |
| --------------------- | -------------------------- | ------------------------------------ |
| `DATABASE_URL`        | `sqlite:///./inspector.db` | SQLAlchemy database URL              |
| `SLOW_QUERY_MS`       | `100`                      | Slow-query threshold in milliseconds |
| `N1_THRESHOLD`        | `3`                        | Repeated SELECT threshold            |
| `QUERY_HISTORY_LIMIT` | `500`                      | Maximum in-memory event history      |
| `N1_WINDOW_SECONDS`   | `10`                       | N+1 detection time window            |

## Running Tests

Install the test dependencies if needed:

```powershell
python -m pip install pytest httpx
```

Run the test suite:

```powershell
python -m pytest -v
```

GitHub Actions runs the tests automatically on pushes to `main` and pull requests targeting `main`.

## Limitations

* N+1 detection is heuristic; repeated SQL statements are not always a performance problem.
* Query history is stored in memory and is cleared when the application restarts.
* This is a local development and profiling tool, not a production database proxy.
* SQL execution timing does not represent the full HTTP request duration.

## Potential Improvements

* Correlate SQL statements with HTTP request IDs.
* Add PostgreSQL integration tests.
* Capture and analyze database execution plans.
* Persist query history.
* Add benchmarking and performance regression thresholds.
* Explore AI-assisted explanations of detected query patterns.

## License

MIT. See [LICENSE](LICENSE).
