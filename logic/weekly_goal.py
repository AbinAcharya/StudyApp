import sqlite3
from datetime import date, timedelta

WEEKLY_GOAL_HOURS = 20  # Set your weekly goal here (hours)

def get_weekly_goal_progress():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    today = date.today()
    start_week = today - timedelta(days=today.weekday())

    cursor.execute("""
        SELECT SUM(actual_time) 
        FROM study_logs
        WHERE date >= ?
    """, (start_week,))
    result = cursor.fetchone()[0] or 0
    conn.close()

    progress_hours = result / 60  # Convert minutes to hours
    goal_hours = WEEKLY_GOAL_HOURS
    percentage = int((progress_hours / goal_hours) * 100) if goal_hours > 0 else 0

    return goal_hours, round(progress_hours, 2), percentage