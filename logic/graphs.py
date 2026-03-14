import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sqlite3
import os

def generate_subject_graph(theme='light'):
    # --- Data Fetching (Keep as is) ---
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT subject, SUM(actual_time) FROM study_logs GROUP BY subject")
    data = cursor.fetchall()
    conn.close()

    if not data:
        return

    subjects = [row[0] for row in data]
    times = [row[1] / 60 for row in data]

    # --- HARD RESET MATPLOTLIB ---
    plt.rcParams.update(plt.rcParamsDefault) # This wipes the dark memory
    
    if theme == 'dark':
        text_color = '#f1f5f9'
        label_color = '#cbd5e1'
        bg_color = '#000000'
        plt.style.use('dark_background')
    else:
        text_color = '#0f172a'  # Solid Dark Blue
        label_color = '#1e293b' # Very Dark Slate (for visibility)
        bg_color = '#ffffff'
        plt.style.use('default')

    fig = plt.figure(figsize=(8, 5))
    fig.patch.set_facecolor(bg_color)
    ax = plt.gca()
    ax.set_facecolor(bg_color)
    
    # Draw bars
    plt.bar(subjects, times, color='#6366f1', edgecolor='#4338ca', linewidth=1)
    
    # --- FORCE AXIS VISIBILITY ---
    # We manually set the spine (axis line) colors to ensure they aren't white
    for spine in ax.spines.values():
        spine.set_edgecolor(label_color)
        spine.set_linewidth(1.5) # Make lines slightly thicker for visibility

    # Force the title and axis labels
    plt.xlabel('Subjects', fontweight='bold', color=label_color, fontsize=10)
    plt.ylabel('Hours Studied', fontweight='bold', color=label_color, fontsize=10)
    plt.title('Study Distribution', fontweight='800', fontsize=14, pad=20, color=text_color)
    
    # Force the tick numbers (the 1.0, 0.8, etc.)
    ax.tick_params(axis='x', colors=label_color, labelsize=9)
    ax.tick_params(axis='y', colors=label_color, labelsize=9)
    
    # Specifically fix the tick labels which often stay light
    plt.xticks(rotation=15, color=label_color)
    plt.yticks(color=label_color)
    
    plt.tight_layout()
    graph_path = os.path.join('static', 'study_graph.png')
    
    # Save WITHOUT transparency for testing to see if the colors stick
    # Then flip to True once you confirm visibility
    plt.savefig(graph_path, transparent=False, facecolor=fig.get_facecolor()) 
    plt.close(fig)