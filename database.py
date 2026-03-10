import sqlite3
import json
import uuid
import os
from typing import Dict, Any, Optional

DB_PATH = "audio_app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            status TEXT NOT NULL,
            transcript TEXT,
            summary TEXT,
            topics TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_task(filename: str) -> str:
    task_id = str(uuid.uuid4())
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (id, filename, status) VALUES (?, ?, ?)",
        (task_id, filename, "processing")
    )
    conn.commit()
    conn.close()
    return task_id

def update_task_status(task_id: str, status: str, transcript: Optional[str] = None, 
                       summary: Optional[str] = None, topics: Optional[list] = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    updates = ["status = ?"]
    values = [status]
    
    if transcript is not None:
        updates.append("transcript = ?")
        values.append(transcript)
    if summary is not None:
        updates.append("summary = ?")
        values.append(summary)
    if topics is not None:
        updates.append("topics = ?")
        values.append(json.dumps(topics))
        
    values.append(task_id)
    
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
    cursor.execute(query, tuple(values))
    conn.commit()
    conn.close()

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        result = dict(row)
        if result.get("topics"):
            result["topics"] = json.loads(result["topics"])
        return result
    return None

def get_all_tasks() -> list[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    results = []
    for row in rows:
        result = dict(row)
        if result.get("topics"):
            result["topics"] = json.loads(result["topics"])
        results.append(result)
    return results

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
