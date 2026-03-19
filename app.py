from flask import Flask, Response, request, redirect
from database import init_db, record_visit, get_total, get_daily_counts, get_first_visit_date
from svg_generator import build_svg
import time

app = Flask(__name__)
init_db()

@app.route("/count/<username>")
def count(username):
    agent = request.headers.get("User-Agent", "")
    if "camo" not in agent.lower():
        record_visit(username)

    # Redirect to a unique timestamped URL so GitHub cache never matches
    ts = int(time.time())
    return redirect(f"/badge/{username}?t={ts}", code=302)

@app.route("/badge/<username>")
def badge(username):
    total      = get_total(username)
    daily      = get_daily_counts(username, days=7)
    first_date = get_first_visit_date(username)
    svg        = build_svg(total, daily, first_date)

    return Response(
        svg,
        mimetype="image/svg+xml",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma":        "no-cache",
            "Expires":       "0",
            "s-maxage":      "1",
        }
    )

@app.route("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
