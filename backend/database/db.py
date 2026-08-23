import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "houdini.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at:", DB_PATH)

