import sqlite3

def create_database():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Table for study logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            subject TEXT,
            planned_time INTEGER,
            actual_time INTEGER,
            understanding INTEGER
        )
    """)

    # New Table for User Settings & Intelligence
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            theme TEXT DEFAULT 'light',
            credits INTEGER DEFAULT 15,
            intensity TEXT DEFAULT 'Standard',
            weekly_goal INTEGER DEFAULT 20
        )
    """)

    # Initialize settings if empty
    cursor.execute("SELECT COUNT(*) FROM settings")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO settings (theme, credits, intensity, weekly_goal) VALUES (?, ?, ?, ?)", 
                       ('light', 15, 'Standard', 20))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()