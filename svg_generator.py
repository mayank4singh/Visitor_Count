from datetime import date

def build_svg(total, daily_counts, first_date=""):
    max_val  = max(daily_counts) if max(daily_counts) > 0 else 1
    bar_w    = 18
    bar_gap  = 4
    chart_h  = 32
    bars_x   = 20
    chart_y  = 80
    n        = len(daily_counts)
    svg_w    = max(220, bars_x * 2 + n * (bar_w + bar_gap) - bar_gap)
    today    = date.today().strftime("%b %d, %Y")
    svg_h    = chart_y + chart_h + 28
    formatted = f"{total:,}"

    # Date range line
    date_range = f"{first_date} → {today}" if first_date else today

    bars = ""
    for i, count in enumerate(daily_counts):
        h     = max(4, int((count / max_val) * chart_h))
        x     = bars_x + i * (bar_w + bar_gap)
        y     = chart_y + chart_h - h
        color = "#7F52FF" if i == n - 1 else "#3b2f6e"
        bars += f'<rect x="{x}" y="{y}" width="{bar_w}" height="{h}" rx="3" fill="{color}"/>'

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
  width="{svg_w}" height="{svg_h}"
  viewBox="0 0 {svg_w} {svg_h}">

  <rect width="{svg_w}" height="{svg_h}" rx="8"
        fill="#0d1117" stroke="#21262d" stroke-width="1"/>

  <text x="{bars_x}" y="22"
        font-family="monospace" font-size="10"
        fill="#484f58" letter-spacing="2">PROFILE VIEWS</text>

  <text x="{bars_x}" y="56"
        font-family="monospace" font-size="28"
        font-weight="bold" fill="#e6edf3">{formatted}</text>

  <text x="{bars_x}" y="74"
        font-family="monospace" font-size="9"
        fill="#484f58">{date_range}</text>

  {bars}

  <text x="{bars_x}" y="{svg_h - 6}"
        font-family="monospace" font-size="9"
        fill="#484f58">7 days ago</text>

  <text x="{svg_w - bars_x}" y="{svg_h - 6}"
        font-family="monospace" font-size="9"
        fill="#484f58" text-anchor="end">today</text>

</svg>'''
    return svg
