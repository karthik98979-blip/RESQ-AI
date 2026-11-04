"""SQLite storage helpers for the RESQ AI Streamlit prototype."""

from pathlib import Path
import os
import sqlite3


PROJECT_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = PROJECT_DIR / "schema.sql"
DATABASE_PATH = Path(
    os.environ.get("RESQ_AI_DATABASE_PATH", PROJECT_DIR / "resq_ai.db")
).expanduser()


def get_connection():
    """Open the local database and create its tables if needed."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return connection


def init_db():
    """Initialize the database at application startup."""
    connection = get_connection()
    connection.close()


def save_emergency_report(
    *,
    disaster_type,
    location_text,
    description,
    affected_people,
    people_trapped,
    severity_score,
    severity,
    priority_score,
    priority_level,
    latitude=None,
    longitude=None,
):
    """Save an analyzed report and its initial status-history entry."""
    detected_type = str(disaster_type or "Other").strip().title()
    supported_types = {
        "Flood", "Cyclone", "Earthquake", "Fire", "Landslide", "Tsunami", "Other"
    }
    stored_type = detected_type if detected_type in supported_types else "Other"
    classification_notes = (
        None if stored_type == detected_type
        else f"Classifier output: {detected_type}"
    )

    connection = get_connection()
    try:
        with connection:
            type_row = connection.execute(
                "SELECT disaster_type_id FROM disaster_types WHERE name = ?",
                (stored_type,),
            ).fetchone()
            cursor = connection.execute(
                """
                INSERT INTO emergency_reports (
                    disaster_type_id, location_text, latitude, longitude,
                    description, affected_people, people_trapped,
                    severity_score, severity, priority_score, priority_level,
                    classification_method, classification_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'rule_based', ?)
                """,
                (
                    type_row["disaster_type_id"], location_text.strip() or "Not provided",
                    latitude, longitude, description.strip(), int(affected_people),
                    int(bool(people_trapped)), severity_score, severity,
                    priority_score, priority_level, classification_notes,
                ),
            )
            report_id = cursor.lastrowid
            connection.execute(
                """
                INSERT INTO report_updates (
                    report_id, update_type, new_status, message, updated_by
                ) VALUES (?, 'status_change', 'new', ?, 'RESQ AI')
                """,
                (report_id, "Emergency report submitted and analyzed."),
            )
        return report_id
    finally:
        connection.close()


def fetch_recent_reports(limit=100):
    """Return recent reports, with highest-priority reports first."""
    limit = max(1, min(int(limit), 500))
    connection = get_connection()
    try:
        return connection.execute(
            """
            SELECT
                r.report_id,
                d.name AS disaster_type,
                r.location_text,
                r.affected_people,
                r.people_trapped,
                r.severity,
                r.severity_score,
                r.priority_level,
                r.priority_score,
                r.status,
                r.description,
                r.created_at
            FROM emergency_reports AS r
            JOIN disaster_types AS d
              ON d.disaster_type_id = r.disaster_type_id
            ORDER BY r.priority_score DESC, r.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    finally:
        connection.close()
        