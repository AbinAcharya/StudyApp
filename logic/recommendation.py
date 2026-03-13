import sqlite3

def get_recommendation():
    """
    Returns:
    - Weakest subject based on lowest understanding
    - Average understanding
    - Recommendation message considering efficiency
    """
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT subject, AVG(understanding), SUM(actual_time), SUM(planned_time)
        FROM study_logs
        WHERE subject != ''
        GROUP BY subject
        ORDER BY AVG(understanding) ASC
        LIMIT 1
    """)
    result = cursor.fetchone()
    conn.close()

    if result:
        subject = result[0]
        avg_understanding = round(result[1], 2)
        total_actual = result[2] or 0
        total_planned = result[3] or 1
        efficiency = round((total_actual / total_planned) * 100, 2)

        message = f"Focus on {subject} tomorrow.\n"
        message += f"Your average understanding is {avg_understanding} and efficiency is {efficiency}%.\n"

        if avg_understanding < 3:
            message += "Your understanding is low, try revising key concepts.\n"
        if efficiency < 60:
            message += "Your study efficiency is low, try shorter focused sessions (30–45 min)."

        return subject, avg_understanding, message

    return None, None, None