"""One-time, idempotent migration of local Pattern Guard data into Supabase."""

import sqlite3
import sys
from pathlib import Path

from backend.database.db import DATABASE_URL, DB_PATH, get_db_connection, init_db, using_postgres


TABLES = (
    "sites",
    "scans",
    "flow_steps",
    "findings",
    "compliance_submissions",
    "submission_events",
)


def migrate():
    if not DATABASE_URL or not using_postgres():
        raise RuntimeError("DATABASE_URL is required to migrate data into Supabase.")

    source_path = Path(DB_PATH)
    if not source_path.exists():
        raise RuntimeError(f"Local SQLite database was not found at {source_path}.")

    init_db()
    source = sqlite3.connect(source_path)
    source.row_factory = sqlite3.Row
    destination = get_db_connection()
    copied = {}

    try:
        destination_cursor = destination.cursor()
        for table in TABLES:
            columns = [row["name"] for row in source.execute(f"PRAGMA table_info({table})").fetchall()]
            if not columns:
                copied[table] = 0
                continue

            rows = source.execute(f"SELECT * FROM {table}").fetchall()
            placeholders = ", ".join("?" for _ in columns)
            column_list = ", ".join(columns)
            statement = (
                f"INSERT INTO {table} ({column_list}) VALUES ({placeholders}) "
                "ON CONFLICT (id) DO NOTHING"
            )
            for row in rows:
                destination_cursor.execute(statement, tuple(row[column] for column in columns))
            copied[table] = len(rows)

        destination.commit()
    except Exception:
        destination.rollback()
        raise
    finally:
        source.close()
        destination.close()

    print("Local data migration completed.")
    for table, count in copied.items():
        print(f"{table}: {count} row(s) checked")


if __name__ == "__main__":
    try:
        migrate()
    except Exception as error:
        print(f"Migration failed: {error}", file=sys.stderr)
        raise SystemExit(1)
