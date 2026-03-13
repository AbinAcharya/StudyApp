import sqlite3
from datetime import date, timedelta

def get_streaks():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT date FROM study_logs ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    # convert to date objects
    study_dates = sorted([date.fromisoformat(r[0]) for r in rows])

    # calculate current streak
    current_streak = 0
    today = date.today()
    day_check = today
    while day_check in study_dates:
        current_streak += 1
        day_check -= timedelta(days=1)

    # calculate longest streak
    longest_streak = 0
    temp_streak = 1
    for i in range(1, len(study_dates)):
        if (study_dates[i-1] - study_dates[i]).days == 1:
            temp_streak += 1
        else:
            temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak

    # edge case: if only one date
    if len(study_dates) == 1:
        longest_streak = max(longest_streak, 1)

    return current_streak, longest_streak