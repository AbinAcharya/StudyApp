import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3
import os

def generate_subject_graph(theme='light'): # Added theme argument
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, SUM(actual_time) FROM study_logs GROUP BY subject")
    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    subjects = [row[0] for row in data]
    times = [row[1] / 60 for row in data]

    # --- THEME LOGIC ---
    if theme == 'dark':
        text_color = '#f1f5f9'  # Light gray (var--text-main)
        label_color = '#cbd5e1' # Muted gray (var--text-muted)
        plt.style.use('dark_background')
    else:
        text_color = '#0f172a'  # Dark blue-black
        label_color = '#64748b' # Original gray
        plt.style.use('default')

    plt.figure(figsize=(8, 5))
    
    # Matching your 3D/OLED style
    plt.bar(subjects, times, color='#6366f1', edgecolor='#4338ca', linewidth=1)
    
    plt.xlabel('Subjects', fontweight='bold', color=label_color)
    plt.ylabel('Hours Studied', fontweight='bold', color=label_color)
    plt.title('Study Distribution', fontweight='800', fontsize=14, pad=20, color=text_color)
    
    # Fix the tick colors specifically
    plt.xticks(rotation=15, color=label_color)
    plt.yticks(color=label_color)
    
    # Make the background of the image transparent so it sits perfectly on the card
    plt.tight_layout()
    graph_path = os.path.join('static', 'study_graph.png')
    plt.savefig(graph_path, transparent=True) 
    plt.close()