import sqlite3
from datetime import date, timedelta

def get_heatmap_data():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    today = date.today()
    start_date = today - timedelta(days=29)

    cursor.execute("""
        SELECT date, SUM(actual_time)
        FROM study_logs
        WHERE date >= ?
        GROUP BY date
    """, (start_date,))

    rows = cursor.fetchall()
    conn.close()

    heatmap = {}

    for i in range(30):
        day = today - timedelta(days=i)
        heatmap[i] = 0

        for row in rows:
            if row[0] == str(day):
                heatmap[i] = row[1]

    return heatmap