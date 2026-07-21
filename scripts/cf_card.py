#!/usr/bin/env python3
"""Fetch live Codeforces data and emit assets/cf-stats.svg."""
import os, sys, requests

HANDLE  = "PriyanshuIITGHY2006"
OUT     = "assets/cf-stats.svg"
TIMEOUT = 20

RANK_COLORS = [
    (3000, "#FF0000"), (2400, "#FF0000"), (2100, "#FF8C00"),
    (1900, "#AA00AA"), (1600, "#0000FF"), (1400, "#03A89E"),
    (1200, "#008000"), (0,    "#808080"),
]

def rank_color(r):
    for t, c in RANK_COLORS:
        if r >= t: return c
    return "#808080"

def fetch():
    h = {"User-Agent": "gh-profile-action/1.0"}
    u = requests.get(f"https://codeforces.com/api/user.info?handles={HANDLE}",
                     timeout=TIMEOUT, headers=h).json()["result"][0]
    subs = requests.get(
        f"https://codeforces.com/api/user.status?handle={HANDLE}&from=1&count=20000",
        timeout=60, headers=h).json()["result"]
    solved = {f"{s['problem'].get('contestId','')}{s['problem']['index']}"
              for s in subs if s.get("verdict") == "OK"}
    return {
        "rating":     u.get("rating",    0),
        "max_rating": u.get("maxRating", 0),
        "rank":       u.get("rank",      "newbie").title(),
        "max_rank":   u.get("maxRank",   "newbie").title(),
        "solved":     len(solved),
    }

def svg(d):
    rating, max_r  = d["rating"], d["max_rating"]
    rank,   max_rk = d["rank"],   d["max_rank"]
    solved_str = f"{(d['solved'] // 50) * 50}+"
    color  = rank_color(max_r)
    bar_w  = min(463, int(463 * max_r / 3500))
    return f"""<svg width="495" height="200" viewBox="0 0 495 200" xmlns="http://www.w3.org/2000/svg">
<style>text{{font-family:'Segoe UI',Ubuntu,sans-serif}}
.t1{{font-size:15px;font-weight:600;fill:#e6edf3}}
.t2{{font-size:11px;fill:#6e7681}}
.lbl{{font-size:12px;fill:#8b949e}}
.val{{font-size:24px;font-weight:700;fill:{color}}}
.val2{{font-size:24px;font-weight:700;fill:#e6edf3}}
.sub{{font-size:11px;fill:#6e7681}}</style>
<rect width="495" height="200" rx="6" fill="#161b22" stroke="#30363d" stroke-width="1"/>
<circle cx="30" cy="30" r="13" fill="#1f6feb"/>
<text x="30" y="35" text-anchor="middle" font-size="13" font-weight="bold" fill="white" font-family="Segoe UI,sans-serif">cf</text>
<text x="52" y="25" class="t1">Codeforces</text>
<text x="52" y="39" class="t2">@{HANDLE}</text>
<line x1="16" y1="52" x2="479" y2="52" stroke="#21262d" stroke-width="1"/>
<text x="35" y="76" class="lbl">Current Rating</text>
<text x="35" y="103" class="val">{rating}</text>
<text x="35" y="118" class="sub">{rank}</text>
<text x="200" y="76" class="lbl">Max Rating</text>
<text x="200" y="103" class="val">{max_r}</text>
<text x="200" y="118" class="sub">{max_rk}</text>
<text x="360" y="76" class="lbl">Problems Solved</text>
<text x="360" y="103" class="val2">{solved_str}</text>
<text x="360" y="118" class="sub">800 – 2400</text>
<line x1="16" y1="132" x2="479" y2="132" stroke="#21262d" stroke-width="1"/>
<text x="16" y="152" class="lbl">Progress to Legendary Grandmaster (3500)</text>
<rect x="16" y="160" width="463" height="7" rx="3" fill="#21262d"/>
<rect x="16" y="160" width="{bar_w}" height="7" rx="3" fill="{color}" opacity="0.85"/>
<text x="16" y="188" class="sub">Updated daily · GitHub Actions · codeforces.com/profile/{HANDLE}</text>
</svg>"""

def main():
    print(f"Fetching CF data for {HANDLE}…")
    try:
        data = fetch()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)
    print(f"  Rating={data['rating']}  Max={data['max_rating']}  Solved={data['solved']}")
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(svg(data))
    print(f"Saved → {OUT}")

if __name__ == "__main__":
    main()
