import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, timedelta
from database import create_database
from logic.recommendation import get_recommendation
from logic.graphs import generate_subject_graph 
from logic.heatmap import get_heatmap_data
from logic.streak import get_streaks
from logic.efficiency import get_efficiency
from logic.weekly_goal import get_weekly_goal_progress

create_database()

app = Flask(__name__)
app.secret_key = "study_app_secret"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        subject = request.form.get("subject", "").strip()
        planned = request.form.get("planned_time", "").strip()
        actual = request.form.get("actual_time", "").strip()
        understanding = request.form.get("understanding", "").strip()

        if not subject or not planned or not actual:
            flash("Error: Please fill all fields.")
            return redirect(url_for('index'))

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        today = date.today()
        cursor.execute(
            "INSERT INTO study_logs (subject, planned_time, actual_time, understanding, date) VALUES (?, ?, ?, ?, ?)",
            (subject, int(planned), int(actual), int(understanding), today)
        )
        conn.commit()
        conn.close()

        flash("Session Saved!") 
        return redirect(url_for('index'))
    
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    # Ascending order (oldest at top) as requested
    cursor.execute("SELECT id, date, subject, planned_time, actual_time, understanding FROM study_logs ORDER BY id ASC")
    logs = cursor.fetchall()
    conn.close()

    current_streak, longest_streak = get_streaks()
    efficiency = get_efficiency()
    goal_hours, progress_hours, goal_percentage = get_weekly_goal_progress()
    subject, avg_understanding, recommendation = get_recommendation()
    
    # Only attempt to generate the graph if logs exist
    if logs:
        generate_subject_graph()
    
    heatmap_html = get_heatmap_data()

    return render_template(
        "dashboard.html",
        logs=logs,
        streak=current_streak,
        efficiency=efficiency,
        total_hours_this_week=progress_hours,
        recommendation=recommendation,
        heatmap_html=heatmap_html,
        # version variable for cache-busting the graph image
        version=random.randint(1, 9999) 
    )

@app.route("/clear", methods=["POST"])
def clear():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_logs")
    conn.commit()
    conn.close()
    
    # Physically remove the graph file from the static folder
    graph_path = os.path.join('static', 'study_graph.png')
    if os.path.exists(graph_path):
        os.remove(graph_path)
        
    return redirect(url_for('dashboard'))

@app.route("/delete/<int:log_id>", methods=["POST"])
def delete(log_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_logs WHERE id=?", (log_id,))
    conn.commit()
    
    # After deletion, check if there are zero logs left
    cursor.execute("SELECT COUNT(*) FROM study_logs")
    if cursor.fetchone()[0] == 0:
        graph_path = os.path.join('static', 'study_graph.png')
        if os.path.exists(graph_path):
            os.remove(graph_path)
            
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)