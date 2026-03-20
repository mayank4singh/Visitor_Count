from flask import Flask, Response, request
from database import init_db, record_visit, get_total, get_daily_counts, get_first_visit_date
from svg_generator import build_svg

app = Flask(__name__)
init_db()

@app.route("/count/<username>")
def count(username):
    agent = request.headers.get("User-Agent", "").lower()

    # GitHub's camo proxy IS the real visit signal
    # When camo fetches this image, a real human just loaded your profile
    # Everything else (curl, bots, GitHub Actions) should be ignored
    skip = ["curl", "python", "github-action", "bot", "spider", "crawler"]
    is_skip = any(s in agent for s in skip)

    if not is_skip:
        # This includes camo requests — they are real visits
        record_visit(username)

    total = get_total(username)
    daily = get_daily_counts(username, days=7)
    first = get_first_visit_date(username)
    svg   = build_svg(total, daily, first)

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
