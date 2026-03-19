import sqlite3
from datetime import datetime, date, timedelta

DB = "counter.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL,
            visited_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def record_visit(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(
        "INSERT INTO visits (username, visited_at) VALUES (?, ?)",
        (username, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_total(username):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits WHERE username = ?", (username,))
    total = c.fetchone()[0]
    conn.close()
    return total

def get_daily_counts(username, days=7):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        SELECT DATE(visited_at) as day, COUNT(*) as cnt
        FROM visits
        WHERE username = ?
        AND visited_at >= DATE('now', ?)
        GROUP BY day
        ORDER BY day ASC
    """, (username, f'-{days} days'))
    rows = c.fetchall()
    conn.close()

    counts = {row[0]: row[1] for row in rows}
    result = []
    for i in range(days - 1, -1, -1):
        day = (date.today() - timedelta(days=i)).isoformat()
        result.append(counts.get(day, 0))
    return result
