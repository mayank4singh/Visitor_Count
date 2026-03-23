import psycopg2
import os
from datetime import datetime, date, timedelta

DB_URL = os.environ.get("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id          SERIAL PRIMARY KEY,
            username    TEXT NOT NULL,
            visited_at  TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """)
    conn.commit()
    conn.close()

def record_visit(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "INSERT INTO visits (username, visited_at) VALUES (%s, %s)",
        (username, datetime.utcnow().isoformat())
    )
    conn.commit()
    conn.close()

def get_total(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM visits WHERE username = %s", (username,))
    total = c.fetchone()[0]
    conn.close()
    return total

def get_first_visit_date(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT MIN(visited_at) FROM visits WHERE username = %s",
        (username,)
    )
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return row[0].strftime("%b %d, %Y")
    return "Today"

def get_daily_counts(username, days=7):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT DATE(visited_at) as day, COUNT(*) as cnt
        FROM visits
        WHERE username = %s
        AND visited_at >= NOW() - INTERVAL '%s days'
        GROUP BY day
        ORDER BY day ASC
    """, (username, days))
    rows = c.fetchall()
    conn.close()

    counts = {str(row[0]): row[1] for row in rows}
    result = []
    for i in range(days - 1, -1, -1):
        day = (date.today() - timedelta(days=i)).isoformat()
        result.append(counts.get(day, 0))
    return result

