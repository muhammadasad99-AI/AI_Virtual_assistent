import sqlite3
from datetime import datetime

DB_NAME = "assistant.db"

# ─────────────────────────────────────────────
# INITIALIZE DATABASE
# ─────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            remind_time TEXT,
            remind_date TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_done INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            event_time TEXT,
            event_date TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_notified INTEGER DEFAULT 0
        )
    ''')

    conn.commit()
    conn.close()

# ─────────────────────────────────────────────
# REMINDER CRUD
# ─────────────────────────────────────────────
def add_reminder(title: str, remind_time: str = None, remind_date: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO reminders (title, remind_time, remind_date) VALUES (?, ?, ?)",
        (title, remind_time, remind_date)
    )
    conn.commit()
    conn.close()
    return True

def get_all_reminders():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reminders WHERE is_done = 0 ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_reminder(reminder_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    return True

def mark_reminder_done(reminder_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE reminders SET is_done = 1 WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()
    return True

# ─────────────────────────────────────────────
# SCHEDULE CRUD
# ─────────────────────────────────────────────
def add_schedule(title: str, event_time: str = None, event_date: str = None, description: str = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO schedules (title, event_time, event_date, description) VALUES (?, ?, ?, ?)",
        (title, event_time, event_date, description)
    )
    conn.commit()
    conn.close()
    return True

def get_all_schedules():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM schedules ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_schedule(schedule_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM schedules WHERE id = ?", (schedule_id,))
    conn.commit()
    conn.close()
    return True