import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).resolve().parent / "patients.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                dob TEXT NOT NULL,
                email TEXT NOT NULL,
                glucose REAL NOT NULL,
                haemoglobin REAL NOT NULL,
                cholesterol REAL NOT NULL,
                remarks TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def create_patient(data):
    with get_connection() as connection:
        cursor = connection.execute("""
            INSERT INTO patients (
                full_name, dob, email, glucose,
                haemoglobin, cholesterol, remarks
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data["full_name"], data["dob"], data["email"],
            data["glucose"], data["haemoglobin"],
            data["cholesterol"], data["remarks"]
        ))
        return cursor.lastrowid


def get_all_patients():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM patients ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_patient(patient_id):
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM patients WHERE id = ?", (patient_id,)
        ).fetchone()
        return dict(row) if row else None


def update_patient(patient_id, data):
    with get_connection() as connection:
        cursor = connection.execute("""
            UPDATE patients
            SET full_name = ?, dob = ?, email = ?, glucose = ?,
                haemoglobin = ?, cholesterol = ?, remarks = ?
            WHERE id = ?
        """, (
            data["full_name"], data["dob"], data["email"],
            data["glucose"], data["haemoglobin"],
            data["cholesterol"], data["remarks"], patient_id
        ))
        return cursor.rowcount > 0


def update_patient_email(patient_id, email):
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE patients SET email = ? WHERE id = ?",
            (email, patient_id)
        )
        return cursor.rowcount > 0


def delete_patient(patient_id):
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM patients WHERE id = ?", (patient_id,)
        )
        return cursor.rowcount > 0
