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
from logic.advisor import calculate_recommendation

create_database()

app = Flask(__name__)
app.secret_key = "study_app_secret"

# Helper function to get theme and goal for every page
def get_user_settings():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT theme, weekly_goal FROM settings WHERE id=1")
    settings = cursor.fetchone()
    conn.close()
    return settings if settings else ('light', 20)

@app.route('/', methods=['GET', 'POST'])
def index():
    theme, _ = get_user_settings()
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
    
    return render_template('index.html', theme=theme)

@app.route("/dashboard")
def dashboard():
    theme, _ = get_user_settings()
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
        version=random.randint(1, 9999),
        theme=theme
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

# --- NEW SETTINGS ROUTE ---
@app.route("/settings", methods=["GET", "POST"])
def settings():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        theme = request.form.get("theme")
        credits = int(request.form.get("credits"))
        intensity = request.form.get("intensity")
        
        # Advisor logic
        suggested_goal, _ = calculate_recommendation(credits, intensity)
        
        cursor.execute("""
            UPDATE settings SET theme=?, credits=?, intensity=?, weekly_goal=? WHERE id=1
        """, (theme, credits, intensity, suggested_goal))
        conn.commit()
        flash("Settings Updated!")
        return redirect(url_for('settings'))

    cursor.execute("SELECT theme, credits, intensity, weekly_goal FROM settings WHERE id=1")
    user_settings = cursor.fetchone()
    conn.close()
    
    _, bracket = calculate_recommendation(user_settings[1], user_settings[2])

    return render_template("settings.html", 
                           settings=user_settings, 
                           bracket=bracket, 
                           theme=user_settings[0])

if __name__ == "__main__":
    app.run(debug=True)