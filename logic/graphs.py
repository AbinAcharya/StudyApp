import matplotlib
matplotlib.use('Agg')  # Prevents thread crashes
import matplotlib.pyplot as plt
import sqlite3
import os

def generate_subject_graph():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, SUM(actual_time) FROM study_logs GROUP BY subject")
    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    subjects = [row[0] for row in data]
    times = [row[1] / 60 for row in data]

    plt.figure(figsize=(8, 5))
    plt.bar(subjects, times, color='#6366f1', edgecolor='#4338ca', linewidth=1)
    
    plt.xlabel('Subjects', fontweight='bold', color='#64748b')
    plt.ylabel('Hours Studied', fontweight='bold', color='#64748b')
    plt.title('Study Distribution', fontweight='800', fontsize=14, pad=20)
    plt.xticks(rotation=15)
    plt.tight_layout()

    graph_path = os.path.join('static', 'study_graph.png')
    plt.savefig(graph_path, transparent=True)
    plt.close()