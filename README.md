# TTC Data Pipeline

A data pipeline over two City of Toronto open datasets — **TTC Routes & Schedules**
(a GTFS feed) and **TTC Bus Delay Data** — built with **Postgres + Python** in a
**medallion (bronze → silver → gold)** architecture. It ingests the raw data,
cleans and types it, reconciles routes across the two datasets, and answers three
questions:

1. Average number of stops per route
2. The most frequently scheduled route
3. Average delay across all routes

## Brief overview of the pipeline (see the write-up for more details)

- **Ingestion** resolves the *current* download URLs from Toronto's CKAN API at
  runtime (URLs change when the TTC republishes), downloads the files, and lands
  them in `data/raw/`.
- **Postgres** (in Docker) stores everything, with the medallion layers as schemas:
  - `bronze` — raw landed data, every column `TEXT`, no casting
  - `silver` — typed, cleaned, plus the cross-dataset route reconciliation (not used in gold)
  - `gold` — the analysis result tables
- It's **ELT**: Python orchestrates; the transformations are SQL (`sql/`).

## Prerequisites

- **Docker Desktop** (running) — provides Postgres and, optionally, runs the pipeline
- **Python 3.11** — only needed for the "host" run option below

## Setup

```bash
# 1. copy the env template (holds the DB name/user/password and load scope)
cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
```

That's all that's required for the Docker option.

## Running the pipeline

### Option A — Docker 

```bash
docker compose up -d db                     # start Postgres
docker compose run --rm --build pipeline    # run the whole pipeline
```

Run a single stage instead of the whole thing:

```bash
docker compose run --rm pipeline python run.py --stage ingest
docker compose run --rm pipeline python run.py --stage bronze
# ...silver, gold
```

Load the full dataset (all delay years 2014–2025 instead of just the 2024 sample):

```bash
docker compose run --rm -e FULL_LOAD=true pipeline python run.py
```

### Option B — host Python 

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1                 # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d db                      # DB in Docker; pipeline on the host
python run.py                                # full pipeline
python run.py --stage silver                 # a single stage
```

### CLI reference

| Command | What it does |
| --- | --- |
| `python run.py` | Run the full pipeline (ddl → ingest → bronze → silver → gold) |
| `python run.py --stage <name>` | Run one stage: `ddl`, `ingest`, `bronze`, `silver`, `gold` |
| `python run.py --reset` | Drop and recreate the `bronze`/`silver`/`gold` schemas |
| `python run.py --local` | Skip downloading; reuse files already in `data/raw/` |
| `FULL_LOAD=true python run.py` | Load all delay years instead of the 2024 sample |

## Viewing the results

The three answers land in the `gold` schema:

| Question | Table |
| --- | --- |
| Q1 – avg stops per route | `gold.avg_stops_per_route` |
| Q2 – most scheduled route | `gold.route_trip_counts` (top row) |
| Q3 – avg delay | `gold.avg_delay` (and `gold.avg_delay_by_route`) |

### Option 1 — VS Code (browse the medallion schemas visually)

Install two extensions (Extensions panel, `Ctrl+Shift+X`):

- **SQLTools** — `mtxr.sqltools`
- **SQLTools PostgreSQL/Cockroach Driver** — `mtxr.sqltools-driver-pg`

Then add a connection (SQLTools icon in the sidebar → *Add New Connection* → PostgreSQL):

| Field | Value |
| --- | --- |
| Server / Host | `localhost` |
| Port | `5432` |
| Database | `ttc` |
| Username | `ttc` |
| Password | `ttc_dev_pw` |

Connect, then expand **ttc → Schemas** to browse the three medallion layers
(`bronze`, `silver`, `gold`) and open any table. You can also open
`analysis/sample_queries.sql` and run it straight from the editor — results appear
in a table pane.

### Option 2 — terminal (no install; `psql` ships inside the DB container)

```bash
# run the sample queries
docker exec -i ttc_db psql -U ttc -d ttc < analysis/sample_queries.sql   # macOS/Linux/Git Bash
Get-Content analysis/sample_queries.sql | docker exec -i ttc_db psql -U ttc -d ttc   # PowerShell

# a single ad-hoc query
docker exec ttc_db psql -U ttc -d ttc -c "SELECT * FROM gold.avg_delay;"
```

## Configuration

Everything is set through `.env` (see `.env.example`):

| Variable | Purpose |
| --- | --- |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Database name and credentials |
| `POSTGRES_HOST` / `POSTGRES_PORT` | Where to reach Postgres (defaults `localhost:5432`) |
| `FULL_LOAD` | `true` loads all delay years; otherwise just the 2024 sample |

## Design notes & assumptions

See the accompanying write-up for the architecture, the interpretation of each
question, data-quality findings, and productionization steps.
