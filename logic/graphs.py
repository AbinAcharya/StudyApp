import sqlite3
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend for Flask
import matplotlib.pyplot as plt

def generate_subject_graph():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, SUM(actual_time)
        FROM study_logs
        WHERE subject != ''
        GROUP BY subject
    """)
    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    subjects = [row[0] for row in data]
    hours = [row[1] for row in data]

    plt.figure()
    plt.bar(subjects, hours)
    plt.xlabel("Subjects")
    plt.ylabel("Total Study Hours")
    plt.title("Study Hours per Subject")
    plt.tight_layout()

    plt.savefig("static/study_graph.png")
    plt.close()