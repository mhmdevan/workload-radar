# Workload Radar – Production-Style Flask Backend (Resume Project)

This repository is a **resume-focused backend project** that simulates a realistic production service:

- Python 3 + Flask 3.x
- PostgreSQL (external DB) + Pony ORM + analytical SQL (CTE, aggregation)
- Celery + RabbitMQ for background processing
- Docker / Docker Compose + Nginx + gunicorn
- SQL-based migrations
- pytest test suite running in Docker (SQLite in-memory)
- Centralized logging, error handling, and a health check

It is built to answer typical senior-level interview questions:

> *What problem were you solving?  
> What options did you consider?  
> Why did you choose this stack?  
> What metrics did you track?  
> What went wrong and how did you fix it?*

This README is written so you can comfortably walk through those topics in an interview.

---

## 1. Problem Statement (What this service does)

**Business story (simplified):**

A small team works on several projects. They need:

- A way to manage **users**, **projects**, and **tasks** via a clean REST API.
- A lightweight event log of **task changes** (for future audit/tracking).
- A way to generate **analytical reports** (e.g. task status breakdown, average lead time) without blocking the main API.
- A deployment model that looks like real life: external PostgreSQL, Dockerized app, message queue, worker.

So the service answers questions like:

- How many tasks are `todo`, `in_progress`, `done` per project?
- What is the **average lead time** (from creation to completion) for tasks done in the last 30 days?
- Can we generate such reports asynchronously and fetch them later?

**Core features:**

- REST API for:
  - user registration & login
  - creating/listing projects
  - creating/listing/updating tasks
  - requesting reports and fetching their results
- Celery worker that:
  - executes heavy analytical queries
  - stores results into a `reports` table
- Health check & logging for basic observability.

This is intentionally small but realistically structured for a senior backend developer.

---

## 2. Tech Choices & Alternatives (Why this stack)

### Web framework

- **Chosen:** Flask 3.x  
  - Lightweight and unopinionated.
  - Easy to show **manual architecture decisions** (blueprints, services, repositories) instead of relying on framework magic.
  - Very common in existing codebases; good for “I can work with legacy Flask apps” narrative.
- **Considered:** FastAPI
  - Pro: async-first, OpenAPI out-of-the-box.
  - Reason *not* used here: this project focuses on *architecture & infrastructure*, not async HTTP benchmarks. Sticking with Flask keeps the code accessible and highlights structure, not framework capabilities.

### ORM & database

- **Chosen:** Pony ORM + PostgreSQL
  - Postgres is the primary external DB in Docker and production-like environments.
  - Pony ORM gives a different flavor than SQLAlchemy, showing that:
    - I’m comfortable with **different ORMs**,
    - and I know when to drop down to **raw SQL** (for complex analytics).
  - Entities: `User`, `Project`, `Task`, `TaskEvent`, `Report`.
- **Considered:** SQLAlchemy
  - SQLAlchemy is more standard and powerful.
  - Reason *not* used here: I deliberately chose Pony to show adaptation to less common tools. In many real teams you inherit stacks that are not what you’d choose today.

### Async & messaging

- **Chosen:** Celery + RabbitMQ
  - Classic combo, widely used in production.
  - Clean separation:
    - Flask app produces jobs (report requests).
    - Celery worker consumes jobs, runs heavy SQL, writes results.
  - RabbitMQ runs as a Docker service, configured via env.
- **Considered:** Redis as broker / task queue
  - Redis is simpler to run.
  - Reason *not* used here: RabbitMQ highlights experience with **dedicated message brokers** beyond simple caching layers.

### Deployment & infrastructure

- **Chosen:**
  - Docker / Docker Compose
  - gunicorn as WSGI server
  - Nginx as reverse proxy
  - External PostgreSQL (not in the same compose file)
- Why:
  - Mirrors a realistic setup where the DB is managed separately (cloud RDS, managed PostgreSQL, etc.).
  - Compose orchestrates app, worker, RabbitMQ, Nginx — but **not** the database.
  - Shows understanding of reverse proxying, health checks, and layering.

### Testing & CI

- **Chosen:**
  - pytest for backend tests
  - SQLite in-memory DB for tests (fast, isolated)
  - GitHub Actions for basic CI.

- Why:
  - Tests should not depend on the external PostgreSQL instance.
  - In-memory DB keeps test feedback fast and stable.
  - CI only needs a Python environment; no DB container, no migrations needed.

---

## 3. Architecture (How the service is structured)

### High-level layout

```text
src/
├─ app/
│  ├─ __init__.py            # app factory
│  ├─ config.py              # environment-based settings
│  ├─ logging_config.py      # logging setup
│  ├─ errors.py              # global error handlers
│  ├─ exceptions.py          # custom API/domain exceptions
│  ├─ models.py              # Pony ORM entities
│  ├─ extensions.py          # DB + Celery initialization
│  ├─ celery_app.py          # Celery entrypoint (worker)
│  ├─ pagination.py          # pagination helper
│  ├─ blueprints/            # HTTP controllers
│  ├─ services/              # business logic
│  ├─ repositories/          # data access layer
│  └─ tasks/                 # Celery tasks
├─ scripts/
│  ├─ entrypoint.py          # dev vs prod launcher
│  ├─ run_dev.py             # dev server (Flask)
│  ├─ run_prod.py            # gunicorn launcher
│  └─ apply_migrations.py    # SQL migration runner
├─ migrations/               # SQL files for schema evolution
├─ tests/                    # pytest suite (SQLite-based)
├─ docker/                   # Dockerfiles for app & worker
├─ nginx/                    # Nginx config
└─ .github/workflows/        # CI configuration
```

### Layering & responsibilities

- **Blueprints (`app/blueprints/*.py`)**
  - Thin HTTP controllers.
  - Parse input, call services, return JSON.
  - Do not contain business logic or persistence details.

- **Services (`app/services/*.py`)**
  - Contain business rules and validation.
  - Coordinate repositories and Celery tasks.
  - Example: `ReportService` creates a `Report` record then enqueues a Celery job.

- **Repositories (`app/repositories/*.py`)**
  - Wrap Pony ORM queries and raw SQL where appropriate.
  - Encapsulate data access, not business logic.

- **Tasks (`app/tasks/*.py`)**
  - Long-running / heavy operations.
  - `generate_project_summary` computes per-project metrics and updates `Report.result`.

- **Scripts (`scripts/*.py`)**
  - Runner for development server, production server, and migration application.
  - Keep container entrypoints and local commands clean and explicit.

This approach demonstrates:

- **SRP / SOLID**: each layer has a single responsibility.
- **DRY**: shared concerns (pagination, error format, logging) are centralized.
- **KISS / YAGNI**: no premature microservices, but still easily extensible.

---

## 4. Data Model & Metrics (What is measured)

### Entities

- `User`
  - `id`, `email`, `name`, `password_hash`, `created_at`
- `Project`
  - `id`, `name`, `owner`, `created_at`
- `Task`
  - `id`, `project`, `title`, `description`, `status`, `priority`, `assignee`, `created_at`, `done_at`
- `TaskEvent`
  - `id`, `task`, `type`, `payload`, `created_at`
- `Report`
  - `id`, `project`, `type`, `params`, `status`, `result`, `created_at`, `finished_at`

### Business metrics (computed in reports)

The `daily_summary` report uses both ORM and raw SQL to compute:

- `status_counts` → number of tasks per status (`todo`, `in_progress`, `done`) for the project.
- `avg_lead_time_days_last_30_days` → average time (in days) between `created_at` and `done_at` for tasks completed in the last 30 days.

The average lead time is computed via a **CTE** in `app/tasks/report_tasks.py`:

- `WITH done_tasks AS (...)`
- `EXTRACT(EPOCH FROM (done_at - created_at)) / 86400.0` to get days
- `AVG(lead_time_days)` over that CTE.

This shows:

- Ability to write analytical SQL where ORMs become awkward.
- Comfort with PostgreSQL functions and time-based analytics.

---

## 5. Migrations & External PostgreSQL (How schema is managed)

### External database, not in Compose

The service is designed to work with an **external PostgreSQL** instance (e.g. cloud RDS or another managed DB).  

Environment variables in `.env` describe that DB:

```env
DB_PROVIDER=postgres
DB_HOST=your-external-host
DB_PORT=5432
DB_USER=radar_user
DB_PASSWORD=strong_password
DB_NAME=radar_db
```

No `postgres` service appears in `docker-compose.yml`.  
This mirrors a real setup where app and DB lifecycles are decoupled.

### Migrations

- SQL migrations live under `migrations/` (e.g. `001_init.sql`).
- `scripts/apply_migrations.py`:
  - connects to PostgreSQL using configuration from `Config`,
  - ensures `schema_migrations` table exists,
  - applies all pending `.sql` files in order,
  - records applied versions.

Usage (from host, using the `web` container):

```bash
docker compose run --rm web python -m scripts.apply_migrations
```

Interview angle:

- You can talk about why you chose **plain SQL migrations** instead of a heavy migration framework.
- You can explain how you keep app and DB schemas in sync, especially with an external DB.

---

## 6. Async Processing (Celery + RabbitMQ)

### Flow

1. Client calls:

   ```http
   POST /reports/project/<project_id>/daily-summary
   ```

2. Service:
   - creates a `Report` entity with `status="pending"`.
   - enqueues a Celery task: `reports.generate_project_summary(report_id)`.

3. Celery worker:
   - loads the `Report` and its `Project`.
   - queries `Task` data (via ORM and raw SQL).
   - computes metrics:
     - counts per status,
     - average lead time.
   - writes metrics to `Report.result`,
   - sets `status="ready"` and `finished_at`.

4. Client later calls:

   ```http
   GET /reports/<report_id>
   ```

   to retrieve the final result.

### Why this matters (interview answer)

- Demonstrates how to **keep HTTP requests fast** while doing heavier analytics in the background.
- Shows understanding of:
  - idempotent tasks (re-running a report is safe),
  - decoupling app and worker,
  - configuring Celery with Flask app context.

---

## 7. Error Handling, Logging & Health Check

### Logging

- Centralized in `app/logging_config.py`.
- Structured log format:
  - timestamp
  - log level
  - logger name
  - message
- Logs go to stdout (Docker-friendly, ready for aggregation tools like ELK, Loki, etc.).

### Error handling

- Domain/API errors:
  - `APIError`, `ValidationError`, `NotFoundError` in `app/exceptions.py`.
  - Unified JSON responses via `app/errors.py`.
- Unexpected exceptions:
  - logged with full stack trace
  - return `{ "error": { "type": "InternalServerError", ... } }` with HTTP 500.

### Health check

- `GET /healthz`:
  - runs a simple DB connectivity check with Pony.
  - returns JSON with overall status and a `database` sub-check.
- Can be used by:
  - Docker healthcheck
  - Nginx / LB
  - Kubernetes liveness/readiness probes.

---

## 8. Running the Stack

### Prerequisites

- Docker & Docker Compose.
- An external PostgreSQL database reachable from the Docker host.

### 8.1. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env`:

- Set `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` to your external DB.
- Keep `CELERY_BROKER_URL` pointing to RabbitMQ in Docker (default works).
- Optionally set `APP_ENV=production` and `ENABLE_NGINX=true` for a more production-like run.

### 8.2. Apply migrations

```bash
docker compose run --rm web python -m scripts.apply_migrations
```

### 8.3. Start services

```bash
docker compose up --build
```

You get:

- API (via Nginx): `http://localhost/`
- Direct Flask port (if exposed): `http://localhost:8000/`
- RabbitMQ management UI: `http://localhost:15672/` (default user/pass from compose env)

Quick manual checks:

```bash
# Health
curl http://localhost/healthz

# Register user
curl -X POST http://localhost/auth/register \
  -H "Content-Type: application/json" \
  -d '{
        "email": "test@example.com",
        "name": "Test User",
        "password": "secret123"
      }'
```

---

## 9. Testing Strategy (and Python version note)

### Python version

- **Supported / tested:** Python 3.12 (inside Docker).
- **Note about Python 3.13:**  
  Pony ORM currently has issues decompiling certain generator comprehensions on Python 3.13, which can manifest as internal `IndexError` in Pony’s `decompiling.py`.  
  To keep things stable and realistic, the canonical runtime for this project is Python 3.12 (as configured in the Dockerfiles).

### Tests

Tests live under `src/tests/` and use:

- Flask test client.
- In-memory SQLite database:
  - `DB_PROVIDER = "sqlite"`
  - `DB_NAME = ":memory:"`
- A dedicated `TestConfig` in `tests/conftest.py`.

They cover:

- user registration & login.
- project creation and listing.
- task creation, listing, and status update.

### Running tests (recommended)

Inside Docker (canonical):

```bash
docker compose run --rm web pytest
```

This:

- builds/uses the same image as the app container,
- runs tests with Python 3.12,
- uses SQLite in-memory (does **not** touch the external PostgreSQL DB).

Optional (local, if you use Python 3.12 and set PYTHONPATH):

```bash
export PYTHONPATH=src
pytest
```

---

## 10. Issues Encountered & How They Were Fixed

This section is deliberately resume-oriented: it highlights real problems that came up while building and wiring this stack, and how they were solved.

### 10.1. Pony ORM rebinding error during tests

**Symptom:**

- `BindingError: Database object was already bound to SQLite provider` during pytest.

**Root cause:**

- Pony’s `Database` instance is global.
- `create_app()` was called multiple times in tests.
- Each call attempted to `db.bind(...)` again.

**Fix:**

- Made DB binding **idempotent** in `app/extensions.py`:

  ```python
  if db.provider is not None:
      return
  ```

- Later, aligned the test fixture to use `scope="session"` for the Flask app to avoid unnecessary repeated initialization.

**Takeaway for interview:**

> When using global ORM objects (Pony, SQLAlchemy engines, etc.), you must consider how many times they’re initialized in test runners and app factories. Making initialization idempotent is a simple but important robustness measure.

---

### 10.2. ORM compatibility with Python 3.13

**Symptom (local dev):**

- `IndexError: tuple index out of range` inside Pony’s `decompiling.py` when running `select(...)` queries on Python 3.13.

**Root cause:**

- Pony ORM’s bytecode decompiler is not yet fully compatible with Python 3.13’s new bytecode format and AST changes.

**Fix:**

- Standardized the project on **Python 3.12** in Docker.
- Documented this clearly in the README.
- Kept local dev on 3.12 for stable behavior.

**Takeaway for interview:**

> For production or serious projects, you should pin language and library versions to combinations you know are stable, especially when using tools doing bytecode introspection or expression decompilation.

---

### 10.3. Keeping tests independent from external PostgreSQL

**Goal:**

- Tests should not depend on:
  - external network,
  - cloud DB,
  - migrations being applied.

**Decision:**

- Test config uses in-memory SQLite and calls `db.generate_mapping(create_tables=True)` to create tables on the fly.

**Benefit:**

- `pytest` runs fast and deterministically.
- CI can run in a simple Python container without Postgres or migrations.

**Takeaway for interview:**

> Test environments should be cheap, isolated, and deterministic. External dependencies (network DBs, queues, etc.) should be avoided or mocked for basic test suites.

---

## 11. How to Present This Project in an Interview

When talking about this repo, you can structure your story like this:

1. **Problem**  
   - “I wanted a small but realistic backend that manages tasks and projects, and computes reports asynchronously so HTTP stays fast.”

2. **Tech choices**  
   - Flask (to control architecture), PostgreSQL + Pony (to show flexibility and raw SQL skills), Celery + RabbitMQ (classic async stack), external DB (production-like), pytest + Docker (reliable tests).

3. **Metrics**  
   - “The app computes business metrics (status counts, average lead time) via a combination of ORM and raw SQL (CTE). I also care about test status (3 integration tests), service health (`/healthz`), and error logs produced by the global error handler.”

4. **Challenges & fixes**  
   - Pony rebinding error → idempotent DB binding.
   - Pony + Python 3.13 decompilation issues → pinning to Python 3.12 and documenting it.
   - Keeping tests independent from external DB → SQLite in-memory config.

5. **What this says about your level**  
   - You think about:
     - clean layering and domain modeling,
     - externalized configuration and environments,
     - async workloads & queues,
     - DB migrations and versioning,
     - test strategy and CI.

---

If you are reviewing this as a recruiter or lead, the best places to look are:

- `app/blueprints/*.py` – REST API style and controllers.
- `app/services/*.py` – business logic and error handling.
- `app/repositories/*.py` – DB access patterns.
- `app/tasks/report_tasks.py` – analytical SQL and Celery usage.
- `migrations/*.sql` – DB schema design.
- `docker/*`, `nginx/*`, `compose.yml` – deployment model.
- `tests/*` and `.github/workflows/` – testing and CI strategy.

## 12. License

```text
MIT License

Copyright (c) 2025 Mohammad Eslamnia
```
