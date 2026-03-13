import sqlite3
from datetime import date, timedelta


def get_weekly_improvement():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    today = date.today()

    start_this_week = today - timedelta(days=today.weekday())
    start_last_week = start_this_week - timedelta(days=7)

    # this week study time
    cursor.execute("""
        SELECT SUM(actual_time)
        FROM study_logs
        WHERE date >= ?
    """, (start_this_week,))
    
    this_week = cursor.fetchone()[0] or 0

    # last week study time
    cursor.execute("""
        SELECT SUM(actual_time)
        FROM study_logs
        WHERE date >= ? AND date < ?
    """, (start_last_week, start_this_week))
    
    last_week = cursor.fetchone()[0] or 0

    conn.close()

    if last_week == 0:
        return 0, "No data from last week."

    improvement = int(((this_week - last_week) / last_week) * 100)

    if improvement > 0:
        message = "You studied more this week."
    elif improvement < 0:
        message = "You studied less than last week."
    else:
        message = "Your study time is the same as last week."

    return improvement, message