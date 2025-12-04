import os
import pathlib
from datetime import datetime

import psycopg2

from app.config import Config


def get_connection():
    """Create a raw psycopg2 connection using Config."""
    cfg = Config()
    if cfg.DB_PROVIDER != "postgres":
        raise RuntimeError("apply_migrations is designed for PostgreSQL provider")

    conn = psycopg2.connect(
        host=cfg.DB_HOST,
        port=cfg.DB_PORT,
        user=cfg.DB_USER,
        password=cfg.DB_PASSWORD,
        dbname=cfg.DB_NAME,
    )
    conn.autocommit = True
    return conn


def ensure_schema_migrations_table(cur) -> None:
    """Ensure schema_migrations table exists."""
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            version VARCHAR(255) PRIMARY KEY,
            applied_at TIMESTAMP WITHOUT TIME ZONE NOT NULL
        );
        """
    )


def get_applied_versions(cur) -> set[str]:
    """Return a set of migration versions that are already applied."""
    cur.execute("SELECT version FROM schema_migrations;")
    rows = cur.fetchall()
    return {row[0] for row in rows}


def apply_migration(cur, version: str, sql_path: pathlib.Path) -> None:
    """Apply a single migration script and record it in schema_migrations."""
    with sql_path.open("r", encoding="utf-8") as f:
        sql = f.read()

    cur.execute(sql)
    cur.execute(
        "INSERT INTO schema_migrations (version, applied_at) VALUES (%s, %s);",
        (version, datetime.utcnow()),
    )


def main() -> None:
    """Apply all pending SQL migrations in numeric order."""
    migrations_dir = pathlib.Path(__file__).resolve().parent.parent / "migrations"
    if not migrations_dir.exists():
        print(f"migrations directory not found at {migrations_dir}")
        return

    migration_files = sorted(migrations_dir.glob("*.sql"))
    if not migration_files:
        print("No migration files found.")
        return

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            ensure_schema_migrations_table(cur)
            applied = get_applied_versions(cur)

            for path in migration_files:
                version = path.stem  # e.g. "001_init"
                if version in applied:
                    print(f"Skipping already applied migration: {version}")
                    continue

                print(f"Applying migration: {version}")
                apply_migration(cur, version, path)

            print("Migrations applied successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
