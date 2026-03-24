import psycopg2
import os
from datetime import date

DB_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username    TEXT PRIMARY KEY,
            total       INTEGER NOT NULL DEFAULT 0,
            first_seen  DATE NOT NULL DEFAULT CURRENT_DATE,
            last_seen   DATE NOT NULL DEFAULT CURRENT_DATE
        )
    """)

    # Daily visits table
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_visits (
            username    TEXT NOT NULL REFERENCES users(username),
            date        DATE NOT NULL DEFAULT CURRENT_DATE,
            count       INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (username, date)
        )
    """)

    conn.commit()
    conn.close()

def record_visit(username):
    conn = get_conn()
    c = conn.cursor()
    today = date.today().isoformat()

    # Upsert user — create if new, update total and last_seen
    c.execute("""
        INSERT INTO users (username, total, first_seen, last_seen)
        VALUES (%s, 1, %s, %s)
        ON CONFLICT (username) DO UPDATE
        SET total     = users.total + 1,
            last_seen = EXCLUDED.last_seen
    """, (username, today, today))

    # Upsert today's daily count
    c.execute("""
        INSERT INTO daily_visits (username, date, count)
        VALUES (%s, %s, 1)
        ON CONFLICT (username, date) DO UPDATE
        SET count = daily_visits.count + 1
    """, (username, today))

    # Delete anything older than 7 days for this user
    c.execute("""
        DELETE FROM daily_visits
        WHERE username = %s
        AND date < CURRENT_DATE - INTERVAL '7 days'
    """, (username,))

    conn.commit()
    conn.close()

def get_total(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT total FROM users WHERE username = %s", (username,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else 0

def get_first_visit_date(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT first_seen FROM users WHERE username = %s", (username,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return row[0].strftime("%b %d, %Y")
    return "Today"

def get_daily_counts(username, days=7):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT date, count
        FROM daily_visits
        WHERE username = %s
        AND date >= CURRENT_DATE - INTERVAL '7 days'
        ORDER BY date ASC
    """, (username,))
    rows = c.fetchall()
    conn.close()

    counts = {str(row[0]): row[1] for row in rows}
    result = []
    from datetime import timedelta
    for i in range(days - 1, -1, -1):
        day = (date.today() - timedelta(days=i)).isoformat()
        result.append(counts.get(day, 0))
    return result