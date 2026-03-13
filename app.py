import os
import sqlite3
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
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
        cursor.execute(
            "INSERT INTO study_logs (subject, planned_time, actual_time, understanding, date) VALUES (?, ?, ?, ?, ?)",
            (subject, int(planned), int(actual), int(understanding), date.today())
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
    cursor.execute("SELECT id, date, subject, planned_time, actual_time, understanding FROM study_logs ORDER BY id ASC")
    logs = cursor.fetchall()
    conn.close()

    current_streak, _ = get_streaks()
    efficiency = get_efficiency()
    _, progress_hours, _ = get_weekly_goal_progress()
    _, _, recommendation = get_recommendation()
    
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
        version=random.randint(1, 9999) 
    )

@app.route("/clear", methods=["POST"])
def clear():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_logs")
    conn.commit()
    conn.close()
    
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
    
    cursor.execute("SELECT COUNT(*) FROM study_logs")
    if cursor.fetchone()[0] == 0:
        graph_path = os.path.join('static', 'study_graph.png')
        if os.path.exists(graph_path):
            os.remove(graph_path)
            
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)