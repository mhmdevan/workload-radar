# src/app/analytics/pipeline.py

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Tuple

import duckdb
import polars as pl
from flask import current_app
from pony.orm import db_session, select

from app.models import Task, TaskEvent

logger = logging.getLogger(__name__)


def _ensure_dir(path: str) -> Path:
    """
    Ensure that the given directory exists and return it as a Path.
    """
    base_path = Path(path).expanduser().resolve()
    base_path.mkdir(parents=True, exist_ok=True)
    return base_path


@db_session
def _export_tasks_to_parquet(base_dir: Path) -> Path:
    """
    Export all tasks from the database into a Parquet file using Polars.

    The exported columns are intentionally simple and analytics-friendly.
    """
    tasks = select(t for t in Task)[:]  # materialize now to avoid lazy evaluation issues

    rows = []
    for t in tasks:
        rows.append(
            {
                "id": t.id,
                "project_id": t.project.id if t.project is not None else None,
                "assignee_id": t.assignee.id if getattr(t, "assignee", None) is not None else None,
                "status": t.status,
                "priority": t.priority,
                "created_at": t.created_at,
                "done_at": t.done_at,
            }
        )

    if not rows:
        logger.info("No tasks found to export to Parquet")
        df = pl.DataFrame(
            {
                "id": pl.Series([], dtype=pl.Int64),
                "project_id": pl.Series([], dtype=pl.Int64),
                "assignee_id": pl.Series([], dtype=pl.Int64),
                "status": pl.Series([], dtype=pl.Utf8),
                "priority": pl.Series([], dtype=pl.Int64),
                "created_at": pl.Series([], dtype=pl.Datetime),
                "done_at": pl.Series([], dtype=pl.Datetime),
            }
        )
    else:
        df = pl.DataFrame(rows)

    tasks_path = base_dir / "tasks.parquet"
    df.write_parquet(tasks_path)
    logger.info("Exported %d tasks to %s", len(df), tasks_path)
    return tasks_path


@db_session
def _export_task_events_to_parquet(base_dir: Path) -> Path:
    """
    Export task events into a Parquet file.

    This is optional for the first analytics, but prepared for future event-based metrics.
    """
    events = select(e for e in TaskEvent)[:]

    rows = []
    for e in events:
        rows.append(
            {
                "id": e.id,
                "task_id": e.task.id if e.task is not None else None,
                "type": e.type,
                "payload": getattr(e, "payload", None),
                "created_at": e.created_at,
            }
        )

    if not rows:
        logger.info("No task events found to export to Parquet")
        df = pl.DataFrame(
            {
                "id": pl.Series([], dtype=pl.Int64),
                "task_id": pl.Series([], dtype=pl.Int64),
                "type": pl.Series([], dtype=pl.Utf8),
                "payload": pl.Series([], dtype=pl.Utf8),
                "created_at": pl.Series([], dtype=pl.Datetime),
            }
        )
    else:
        df = pl.DataFrame(rows)

    events_path = base_dir / "task_events.parquet"
    df.write_parquet(events_path)
    logger.info("Exported %d task events to %s", len(df), events_path)
    return events_path


def _compute_analytics_with_duckdb(base_dir: Path, tasks_path: Path) -> Tuple[Path, int]:
    """
    Use DuckDB to compute analytics on top of the tasks Parquet file and
    write the result as analytics_summary.parquet.

    Metrics:
    - For each project and done_date:
      - tasks_done
      - avg_lead_time_days (difference between created_at and done_at in days)
    """
    summary_path = base_dir / "analytics_summary.parquet"

    con = duckdb.connect(database=":memory:", read_only=False)
    try:
        # Register the tasks Parquet file as a table
        con.execute(
            """
            CREATE OR REPLACE TABLE tasks AS
            SELECT * FROM read_parquet(?);
            """,
            [str(tasks_path)],
        )

        # Compute per-project, per-day aggregates using DuckDB SQL
        con.execute(
            """
            CREATE OR REPLACE TABLE analytics_summary AS
            WITH done_tasks AS (
                SELECT
                    project_id,
                    CAST(created_at AS TIMESTAMP) AS created_at,
                    CAST(done_at AS TIMESTAMP) AS done_at
                FROM tasks
                WHERE done_at IS NOT NULL
            ),
            enriched AS (
                SELECT
                    project_id,
                    DATE(done_at) AS done_date,
                    DATEDIFF('day', created_at, done_at) AS lead_time_days
                FROM done_tasks
            )
            SELECT
                project_id,
                done_date,
                COUNT(*) AS tasks_done,
                AVG(lead_time_days) AS avg_lead_time_days
            FROM enriched
            GROUP BY project_id, done_date
            ORDER BY project_id, done_date;
            """
        )

        # Persist the summary as Parquet
        con.execute(
            "COPY analytics_summary TO ? (FORMAT PARQUET);",
            [str(summary_path)],
        )

        row_count = con.execute("SELECT COUNT(*) FROM analytics_summary;").fetchone()[0]
        logger.info(
            "Analytics summary written to %s with %d rows",
            summary_path,
            row_count,
        )
    finally:
        con.close()

    return summary_path, int(row_count)


def run_offline_analytics() -> Dict[str, Any]:
    """
    High-level entrypoint for offline analytics.

    1. Resolves the analytics data directory from Flask config.
    2. Exports tasks and task events to Parquet (Polars).
    3. Runs DuckDB analytics on tasks.parquet and writes analytics_summary.parquet.
    4. Returns basic metadata about the run so callers (CLI, Airflow, Celery) can log it.

    This function assumes it is called inside an application context.
    """
    analytics_dir = current_app.config.get("ANALYTICS_DATA_DIR")
    if not analytics_dir:
        raise RuntimeError("ANALYTICS_DATA_DIR is not configured")

    base_dir = _ensure_dir(analytics_dir)

    started_at = datetime.utcnow()
    logger.info("Starting offline analytics run at %s using base_dir=%s", started_at.isoformat(), base_dir)

    # Export raw data to Parquet
    tasks_path = _export_tasks_to_parquet(base_dir)
    events_path = _export_task_events_to_parquet(base_dir)

    # Compute analytics on top of tasks.parquet
    summary_path, summary_rows = _compute_analytics_with_duckdb(base_dir, tasks_path)

    finished_at = datetime.utcnow()
    duration_sec = (finished_at - started_at).total_seconds()

    result: Dict[str, Any] = {
        "tasks_parquet": str(tasks_path),
        "task_events_parquet": str(events_path),
        "summary_parquet": str(summary_path),
        "summary_row_count": summary_rows,
        "started_at_utc": started_at.isoformat(),
        "finished_at_utc": finished_at.isoformat(),
        "duration_seconds": duration_sec,
    }

    logger.info("Offline analytics run completed in %.2f seconds", duration_sec, extra={"analytics": result})
    return result
