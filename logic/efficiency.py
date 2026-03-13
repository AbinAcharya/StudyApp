import sqlite3

def get_efficiency():
    """
    Calculates overall efficiency:
    Efficiency = (total actual time / total planned time) * 100
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT SUM(actual_time), SUM(planned_time) FROM study_logs")
    row = cursor.fetchone()
    conn.close()

    total_actual = row[0] or 0
    total_planned = row[1] or 1  # avoid division by zero

    efficiency = round((total_actual / total_planned) * 100, 2)
    return efficiency