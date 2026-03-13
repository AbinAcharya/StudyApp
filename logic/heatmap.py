import sqlite3
from datetime import date, timedelta

def get_heatmap_data():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    today = date.today()
    # We still look at the last 31 days
    start_date = today - timedelta(days=30)
    
    cursor.execute("""
        SELECT date, SUM(actual_time) 
        FROM study_logs 
        WHERE date >= ? 
        GROUP BY date
    """, (start_date,))
    
    data = dict(cursor.fetchall())
    conn.close()

    heatmap_html = ""
    
    # CHANGED: We start from 0 and subtract from 'today' to go backwards in time
    for i in range(31):
        current_date = today - timedelta(days=i) # Now it starts with Today
        date_str = current_date.strftime("%Y-%m-%d")
        minutes = data.get(date_str, 0)
        
        # Logic for colors remains the same
        if current_date > today:
            level = "upcoming"
        elif minutes == 0:
            level = "none"
        elif minutes < 120:
            level = "partial"
        else:
            level = "full"
            
        heatmap_html += f'<div class="heatmap-day {level}" title="{date_str}: {minutes} mins"></div>'
        
    return heatmap_html