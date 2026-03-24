# Github Profile Visitor Count

> A self-hosted, zero-dependency GitHub profile visitor counter — returns a dynamic SVG badge with a real-time total count and a 7-day visit bar chart. No tokens. No sign-ups. No third-party tracking. One line in your README.

<div align="center">

![Visitor Count](https://counter.mayank4singh.me/count/mayank4singh)

*Live badge — hosted at `counter.mayank4singh.me`*

</div>

---

## Why this exists

Every popular visitor counter either requires an account, rate-limits free users, goes down without warning, or injects tracking you never asked for. This one does none of that.

It works exactly the way GitHub's own camo proxy works — when a real human loads your profile, GitHub fetches the badge image through its camo proxy. That camo request is the visit signal. The counter records it, increments the total, and returns a fresh SVG on every request. No polling. No fake counts. No third-party in the response chain.

The service is **free to use**. Drop one line into your README and you are done.

---

## Live Demo

```
https://counter.mayank4singh.me/count/mayank4singh
```

Open it in your browser — you will see the badge with the current total and the 7-day chart.

---

## Quick Start — Use it on your profile

Add this to your GitHub profile `README.md`:

```markdown
![Visitor Count](https://counter.mayank4singh.me/count/YOUR-USERNAME)
```

Centered — recommended:

```markdown
<div align="center">

![Visitor Count](https://counter.mayank4singh.me/count/YOUR-USERNAME)

</div>
```

Replace `YOUR-USERNAME` with your GitHub username. That is all. The counter starts from the moment your README goes live.

---

## Step by Step — Adding it to your GitHub profile

**Step 1** — Find your profile repository.

Your GitHub profile README lives in a special repo named exactly the same as your username — `github.com/YOUR-USERNAME/YOUR-USERNAME`. If it does not exist, create it as a public repo and add a `README.md`.

**Step 2** — Edit `README.md` and paste the badge.

```markdown
<div align="center">

![Visitor Count](https://counter.mayank4singh.me/count/YOUR-USERNAME)

</div>
```

**Step 3** — Commit and push.

```bash
git add README.md
git commit -m "feat: add visitor counter"
git push
```

**Step 4** — Open your GitHub profile in a browser. The counter will show its first count within seconds. Every real profile visit after that increments it automatically.

---

## How it works — Technical Overview

```
Real human opens github.com/YOUR-USERNAME
              │
              │  GitHub renders README and finds the <img> tag
              ▼
    GitHub's camo proxy fetches the image
              │
              │  GET https://counter.mayank4singh.me/count/username
              │  User-Agent: github-camo/...
              ▼
        Flask server receives request
              │
              ├── Reads User-Agent header
              │   ├── "github-camo" → real visit → INSERT into Supabase
              │   ├── "curl / python / bot" → skip, do not record
              │   └── other browser agents → record (direct URL visits)
              │
              ├── SELECT COUNT(*) WHERE username = ?  →  total
              ├── SELECT day, COUNT(*) last 7 days    →  daily[]
              └── SELECT MIN(visited_at)              →  first_date
              │
              ▼
        SVG generator builds response string
              │
              │  - Formatted total with commas  (e.g. 1,247)
              │  - Date range  (Mar 07, 2026 → Mar 20, 2026)
              │  - 7 bar chart rects scaled to daily max
              │  - Today's bar highlighted in accent color
              ▼
        Response returned with Cache-Control: no-cache
              │
              ▼
    GitHub renders SVG inline in README
```

### Why GitHub's camo proxy is the visit signal

When a real human loads your GitHub profile, their browser never directly hits your counter server. GitHub proxies all external images through its camo service. This means the camo request arriving at your server is a 1-to-1 mapping of a real profile visit. This is exactly how every major GitHub counter works — including komarev.com.

### Why Supabase (PostgreSQL) and not SQLite

The original version used SQLite which stored data in a local `counter.db` file. Render's free tier does not have persistent disk storage — every time the server spins down and restarts, the file is wiped and the count resets to zero.

Supabase (PostgreSQL) solves this completely. The data lives in the cloud, independent of Render's lifecycle. The server can restart, redeploy, or spin down indefinitely — the count always continues from where it left off.

### Why SVG and not a PNG or JSON endpoint

SVG is generated as a plain string on every request. No image files, no rendering pipeline, no external dependencies. GitHub and browsers both render it as a crisp vector image at any resolution. It also means the server can modify it dynamically without any graphics library.

### Why no caching

GitHub aggressively caches external images through its camo proxy. To ensure every profile visit triggers a fresh fetch — and therefore a fresh count — every response carries `Cache-Control: no-cache, no-store, must-revalidate` along with `s-maxage: 1` to minimize GitHub's proxy cache window.

---

## API Reference

### `GET /count/<username>`

Records a visit and returns a dynamic SVG badge.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `username` | string | yes | Your GitHub username or any unique identifier |

**Response:** `Content-Type: image/svg+xml`

**Response Headers:**
```
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
s-maxage: 1
```

**Examples:**
```bash
# Your counter
curl https://counter.mayank4singh.me/count/mayank4singh

# Any username — each gets its own independent counter and chart
curl https://counter.mayank4singh.me/count/john
curl https://counter.mayank4singh.me/count/your-project-name
```

Each unique username string gets its own completely independent counter, total, and 7-day chart. There is no interference between usernames.

---

### `GET /health`

Health check. Use this to verify the service is running before adding it to your README.

```bash
curl https://counter.mayank4singh.me/health
```

```json
{ "status": "ok" }
```

---

## Badge Preview

The badge displays three pieces of information:

```
┌──────────────────────────────────────┐
│  PROFILE VIEWS                       │
│                                      │
│  1,247                               │
│  Mar 07, 2026 → Mar 20, 2026        │
│                                      │
│  ▁▂▃▅▄▇█▆   last 7 days            │
└──────────────────────────────────────┘
```

- **Total count** — cumulative from the day the badge was added, formatted with commas
- **Date range** — from the first recorded visit to today, slides forward every day
- **7-day bar chart** — daily visit breakdown, today's bar highlighted in purple

---

## Project Structure

```
Github_profile_Visitor_Count/
│
├── app.py              # Flask routes — request handling, visit recording logic
├── database.py         # Supabase/PostgreSQL — init, record_visit, get_total, get_daily_counts
├── svg_generator.py    # Builds the SVG response string from count data
├── requirements.txt    # Flask, Gunicorn, psycopg2-binary
├── render.yaml         # Render.com deployment config
└── .gitignore          # Excludes venv/, __pycache__/
```

### `app.py`
Handles all incoming HTTP requests. Reads the `User-Agent` header to decide whether to record the visit. Delegates to `database.py` for data and `svg_generator.py` for the response. Sets cache headers on every response.

### `database.py`
Manages the Supabase/PostgreSQL connection via `psycopg2`. Three core functions — `init_db()` creates the visits table on startup, `record_visit()` inserts a new row with the current UTC timestamp, `get_daily_counts()` aggregates visits by day for the chart, and `get_first_visit_date()` returns the earliest recorded visit for the date range label.

### `svg_generator.py`
Takes total count, daily counts array, and first visit date as inputs. Computes bar heights relative to the daily maximum. Builds and returns the complete SVG string. No external libraries.

---

## Customization — Fork and Modify

Fork this repo if you want to run your own instance or change the badge design.

### Change the accent color

In `svg_generator.py`:

```python
# Today's bar (bright) — previous days (dim)
color = "#7F52FF" if i == n - 1 else "#3b2f6e"
```

Replace with any hex:

| Color | Hex | Looks like |
|---|---|---|
| Purple (default) | `#7F52FF` | Kotlin / GitHub |
| Orange | `#FF9900` | AWS |
| Green | `#3DDC84` | Android |
| Blue | `#2088FF` | GitHub Actions |
| Red | `#D24939` | Jenkins |

### Change the chart range

In `app.py`:

```python
daily = get_daily_counts(username, days=7)
```

Change `7` to `14` or `30` for a wider chart.

### Change the badge label

In `svg_generator.py`:

```python
fill="#484f58" letter-spacing="2">PROFILE VIEWS</text>
```

Replace `PROFILE VIEWS` with anything.

---

## Contributing

This project is open to contributions — if you have an idea to improve it, a bug to fix, or a feature to add, feel free to fork the repo, make your changes and open a pull request. All contributions are welcome, no matter how small.

If you use this on your profile, consider giving it a ⭐ — it helps others find it.

---

*Let's build together — fork it, break it, improve it.*

---
<div align="center">
  
**Built with ❤️ and lots of ☕ by Mayank Singh**

</div>

