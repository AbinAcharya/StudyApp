from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import date, timedelta
from database import create_database
from logic.recommendation import get_recommendation
from logic.improvement import get_weekly_improvement
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
    cursor.execute("SELECT id, date, subject, planned_time, actual_time, understanding FROM study_logs ORDER BY id DESC")
    logs = cursor.fetchall()

    today = date.today()
    start_week = today - timedelta(days=today.weekday())
    cursor.execute("SELECT DISTINCT date FROM study_logs WHERE date >= ?", (start_week,))
    study_days = cursor.fetchall()
    days_count = len(study_days)
    consistency = int((days_count / 7) * 100)
    goal_hours, progress_hours, goal_percentage = get_weekly_goal_progress()
    conn.close()

    current_streak, longest_streak = get_streaks()
    efficiency = get_efficiency()
    subject, avg_understanding, recommendation = get_recommendation()
    improvement, improvement_message = get_weekly_improvement()
    
    try:
        generate_subject_graph()
    except:
        pass
    
    heatmap_html = get_heatmap_data()

    return render_template(
        "dashboard.html",
        logs=logs,
        streak=current_streak,
        efficiency=efficiency,
        total_hours_this_week=progress_hours,
        recommendation=recommendation,
        heatmap_html=heatmap_html
    )

@app.route("/clear", methods=["POST"])
def clear():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_logs")
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route("/delete/<int:log_id>", methods=["POST"])
def delete(log_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM study_logs WHERE id=?", (log_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)