import sqlite3, hashlib, time
from pathlib import Path

# Where the database lives. The folder is created automatically if it's missing.
DB_FOLDER = Path(r"D:\Study\Python Project 2026\DB")
DB_FOLDER.mkdir(parents=True, exist_ok=True)
DB_FILE = DB_FOLDER / "prompts.db"

def connect():
    conn = sqlite3.connect(DB_FILE, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")  # lets several users share the file safely
    return conn

def init_db():
    conn = connect()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_hash TEXT UNIQUE NOT NULL,
            prompt TEXT NOT NULL,
            answer TEXT NOT NULL,
            tokens INTEGER NOT NULL DEFAULT 0,
            user_id TEXT NOT NULL,
            created_at REAL NOT NULL
        )""")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            prompt_hash TEXT NOT NULL,
            was_hit INTEGER NOT NULL,
            created_at REAL NOT NULL
        )""")
    conn.commit()
    conn.close()

def make_hash(prompt):
    cleaned = " ".join(prompt.lower().split())  # ignore case and extra spaces
    return hashlib.sha256(cleaned.encode()).hexdigest()

def find_exact(prompt):
    """Returns (answer, tokens) if this prompt was saved before, else None."""
    conn = connect()
    row = conn.execute("SELECT answer, tokens FROM prompts WHERE prompt_hash = ?",
                       (make_hash(prompt),)).fetchone()
    conn.close()
    return row if row else None

def save(prompt, answer, tokens, user_id):
    """Saves a prompt and answer. If the prompt already exists, the answer is replaced."""
    conn = connect()
    conn.execute("""
        INSERT INTO prompts (prompt_hash, prompt, answer, tokens, user_id, created_at)
        VALUES (?,?,?,?,?,?)
        ON CONFLICT(prompt_hash) DO UPDATE SET
            answer = excluded.answer, tokens = excluded.tokens,
            user_id = excluded.user_id, created_at = excluded.created_at
        """, (make_hash(prompt), prompt, answer, tokens, user_id, time.time()))
    conn.commit()
    conn.close()

def log_request(user_id, prompt, was_hit):
    conn = connect()
    conn.execute("INSERT INTO requests (user_id, prompt_hash, was_hit, created_at) VALUES (?,?,?,?)",
                 (user_id, make_hash(prompt), int(was_hit), time.time()))
    conn.commit()
    conn.close()