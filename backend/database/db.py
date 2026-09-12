"""Database setup with Supabase PostgreSQL support and a local SQLite fallback."""

import os
import sqlite3
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

DB_DIR = Path(__file__).resolve().parent
DB_PATH = os.getenv("PATTERN_GUARD_DB_PATH", "").strip() or str(DB_DIR / "pattern_guard.db")
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


class PostgresCursor:
    """Makes the existing SQLite-style query calls portable to PostgreSQL."""

    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, query, params=None):
        # Application queries use SQLite's ? placeholders. psycopg uses %s.
        self._cursor.execute(query.replace("?", "%s"), params)
        return self

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class PostgresConnection:
    """Compatibility wrapper so the rest of the application remains database-agnostic."""

    def __init__(self, connection):
        self._connection = connection

    def cursor(self):
        return PostgresCursor(self._connection.cursor())

    def execute(self, query, params=None):
        return self.cursor().execute(query, params)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        self._connection.close()


def using_postgres():
    return bool(DATABASE_URL)


def get_db_connection():
    """Open Supabase PostgreSQL when DATABASE_URL is configured, otherwise local SQLite."""
    if using_postgres():
        import psycopg
        from psycopg.rows import dict_row

        return PostgresConnection(psycopg.connect(DATABASE_URL, row_factory=dict_row))

    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def init_db():
    """Create Pattern Guard's schema and apply its forward migration, if needed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if not using_postgres():
        cursor.execute("PRAGMA journal_mode = WAL")

    # Sites Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sites (
        id TEXT PRIMARY KEY,
        domain TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        manipulation_index REAL DEFAULT 0.0,
        grade TEXT DEFAULT 'A',
        status TEXT DEFAULT 'audited',
        scans_count INTEGER DEFAULT 0,
        critical_count INTEGER DEFAULT 0,
        high_count INTEGER DEFAULT 0,
        medium_count INTEGER DEFAULT 0,
        low_count INTEGER DEFAULT 0,
        top_violation TEXT DEFAULT '',
        primary_pattern TEXT DEFAULT '',
        ftc_risk_level TEXT DEFAULT 'Low',
        last_scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Scans Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id TEXT PRIMARY KEY,
        site_id TEXT NOT NULL,
        target_url TEXT NOT NULL,
        flow_type TEXT NOT NULL,
        status TEXT NOT NULL,
        manipulation_index REAL DEFAULT 0.0,
        grade TEXT DEFAULT 'A',
        total_steps INTEGER DEFAULT 0,
        findings_count INTEGER DEFAULT 0,
        duration_ms INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (site_id) REFERENCES sites (id)
    )
    """)

    # Flow Steps Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS flow_steps (
        id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL,
        step_number INTEGER NOT NULL,
        step_name TEXT NOT NULL,
        url TEXT NOT NULL,
        action_type TEXT,
        screenshot_path TEXT,
        annotated_screenshot_path TEXT,
        dom_snapshot TEXT,
        price_detected REAL,
        raw_metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id) REFERENCES scans (id)
    )
    """)

    # Findings Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        scan_id TEXT NOT NULL,
        step_id TEXT,
        site_id TEXT NOT NULL,
        category TEXT NOT NULL,
        pattern_name TEXT NOT NULL,
        severity TEXT NOT NULL,
        score_impact REAL NOT NULL,
        dom_selector TEXT,
        dom_snippet TEXT,
        element_text TEXT,
        bounding_box TEXT,
        screenshot_path TEXT,
        annotated_path TEXT,
        plain_explanation TEXT NOT NULL,
        psychological_mechanism TEXT,
        regulatory_citation TEXT,
        regulatory_statute TEXT,
        remedy_recommendation TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (scan_id) REFERENCES scans (id),
        FOREIGN KEY (site_id) REFERENCES sites (id)
    )
    """)

    # Regulator-workflow records. These deliberately store a decision recommendation,
    # not a legally binding approval: a human reviewer remains the decision maker.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compliance_submissions (
        id TEXT PRIMARY KEY,
        reference_code TEXT UNIQUE NOT NULL,
        company_name TEXT NOT NULL,
        contact_email TEXT NOT NULL,
        target_url TEXT NOT NULL,
        flow_type TEXT NOT NULL DEFAULT 'general',
        declaration_text TEXT NOT NULL,
        declared_claims TEXT NOT NULL DEFAULT '[]',
        status TEXT NOT NULL DEFAULT 'submitted',
        scan_id TEXT,
        ai_recommendation TEXT NOT NULL DEFAULT 'pending',
        reconciliation TEXT NOT NULL DEFAULT '[]',
        human_review_reason TEXT,
        reviewer_name TEXT,
        reviewer_notes TEXT,
        reviewer_decision TEXT NOT NULL DEFAULT 'pending',
        decision_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        final_conclusion TEXT,
        FOREIGN KEY (scan_id) REFERENCES scans (id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submission_events (
        id TEXT PRIMARY KEY,
        submission_id TEXT NOT NULL,
        event_type TEXT NOT NULL,
        actor TEXT NOT NULL,
        detail TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (submission_id) REFERENCES compliance_submissions (id)
    )
    """)

    # Lightweight forward migration for databases created before the authority
    # conclusion field was introduced.
    if using_postgres():
        cursor.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND table_name = ?",
            ("compliance_submissions",),
        )
        submission_columns = {row["column_name"] for row in cursor.fetchall()}
    else:
        cursor.execute("PRAGMA table_info(compliance_submissions)")
        submission_columns = {row["name"] for row in cursor.fetchall()}
    if "final_conclusion" not in submission_columns:
        cursor.execute("ALTER TABLE compliance_submissions ADD COLUMN final_conclusion TEXT")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized using", "Supabase PostgreSQL" if using_postgres() else f"SQLite at {DB_PATH}")

