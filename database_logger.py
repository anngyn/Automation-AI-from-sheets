import sqlite3
import datetime

DB_NAME = 'automation_logs.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL,
            output_url TEXT,
            error_message TEXT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def log_task_status(task_id, description, status, output_url=None, error_message=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    
    cursor.execute('''
        INSERT INTO task_logs (task_id, description, status, output_url, error_message, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (task_id, description, status, output_url, error_message, timestamp))
    conn.commit()
    conn.close()
    print(f"Logged task {task_id} with status: {status}")

# Call this once at the beginning of the script
init_db()