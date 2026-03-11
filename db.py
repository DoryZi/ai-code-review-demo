import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "todos.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def add_todo(title):
    """Insert a new todo into the database."""
    conn = get_connection()
    conn.execute("INSERT INTO todos (title) VALUES (?)", (title,))
    conn.commit()
    conn.close()


def list_todos(show_all=True):
    conn = get_connection()
    if show_all:
        rows = conn.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM todos WHERE completed = 0 ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return rows


def toggle_todo(todo_id):
    conn = get_connection()
    conn.execute(
        "UPDATE todos SET completed = NOT completed WHERE id = ?", (todo_id,)
    )
    conn.commit()
    conn.close()


def delete_todo(todo_id):
    conn = get_connection()
    conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    conn.commit()
    conn.close()
