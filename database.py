import sqlite3

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS study_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    planned_time INTEGER,
    actual_time INTEGER,
    understanding INTEGER,
    date TEXT
)
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        planned_time INTEGER,
        actual_time INTEGER,
        understanding INTEGER
    )
    """)

    conn.commit()
    conn.close()