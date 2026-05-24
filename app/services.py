import os
import psycopg2
import psycopg2.extras
from flask import jsonify

DATABASE_URL = os.environ.get("DATABASE_URL")
# Set this env variable before running:
# export DATABASE_URL="postgresql://username:password@localhost:5432/students_db"

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id   SERIAL PRIMARY KEY,
            student_name TEXT    NOT NULL,
            age          INTEGER NOT NULL,
            standard     INTEGER NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()


def fetch_data() -> dict:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM students ORDER BY student_id;")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(row) for row in rows]


def fetch_by_id(student_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM students WHERE student_id = %s;", (student_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return dict(row)
    return {"error": f"No record with id:{student_id} found"}, 404


def update_record(student_id: int, updates: dict) -> dict:
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT * FROM students WHERE student_id = %s;", (student_id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        return {"error": f"No record with id:{student_id} found"}, 404

    record = dict(row)
    record.update(updates)  # same logic as before — merge updates into existing record

    cursor.execute(
        "UPDATE students SET student_name=%s, age=%s, standard=%s WHERE student_id=%s;",
        (record["student_name"], record["age"], record["standard"], student_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return record


def add_student(entry: dict) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (student_name, age, standard) VALUES (%s, %s, %s);",
        (entry["student_name"], entry["age"], entry["standard"])
    )
    conn.commit()
    cursor.close()
    conn.close()
    return True

def delete_student(student_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = %s RETURNING student_id;", (student_id,))
    deleted = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return deleted is not None