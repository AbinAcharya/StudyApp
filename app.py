from flask import Flask, render_template, request, redirect
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


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/log", methods=["POST"])
def log():
    subject = request.form.get("subject", "").strip()
    planned = request.form.get("planned", "").strip()
    actual = request.form.get("actual", "").strip()
    understanding = request.form.get("understanding", "").strip()

    if not subject:
        return "Error: Subject cannot be empty.", 400

    try:
        planned = int(planned)
        actual = int(actual)
        understanding = int(understanding)
    except ValueError:
        return "Error: Planned, Actual, and Understanding must be numbers.", 400

    if planned <= 0 or actual <= 0:
        return "Error: Planned and Actual time must be positive numbers.", 400

    if not (1 <= understanding <= 5):
        return "Error: Understanding must be between 1 and 5.", 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    today = date.today()
    cursor.execute(
        "INSERT INTO study_logs (subject, planned_time, actual_time, understanding, date) VALUES (?, ?, ?, ?, ?)",
        (subject, planned, actual, understanding, today)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, subject, planned_time, actual_time, understanding FROM study_logs")
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
    heatmap = get_heatmap_data()

    metrics = {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "efficiency": efficiency
    }

    return render_template(
    "dashboard.html",
    logs=logs,
    days_count=days_count,
    consistency=consistency,
    subject=subject,
    avg_understanding=avg_understanding,
    recommendation=recommendation,
    improvement=improvement,
    improvement_message=improvement_message,
    heatmap=heatmap,
    metrics=metrics,
    goal_hours=goal_hours,
    progress_hours=progress_hours,
    goal_percentage=goal_percentage
)



@app.route("/clear")
def clear():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM study_logs")

    conn.commit()
    conn.close()

    return redirect("/dashboard")


@app.route("/delete/<int:log_id>")
def delete(log_id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM study_logs WHERE id=?", (log_id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


if __name__ == "__main__":
    app.run(debug=True)