from flask import Flask, Response, request
from database import init_db, record_visit, get_total, get_daily_counts
from svg_generator import build_svg

app = Flask(__name__)
init_db()

@app.route("/count/<username>")
def count(username):
    agent = request.headers.get("User-Agent", "")
    # Skip GitHub's camo image proxy cache pings
    if "camo" not in agent.lower():
        record_visit(username)

    total = get_total(username)
    daily = get_daily_counts(username, days=7)
    svg   = build_svg(total, daily)

    return Response(
        svg,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
            "Expires":       "0",
        }
    )

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
