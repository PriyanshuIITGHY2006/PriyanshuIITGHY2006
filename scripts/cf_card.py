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

def lighten(hex_color, amt=0.45):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r = int(r + (255 - r) * amt); g = int(g + (255 - g) * amt); b = int(b + (255 - b) * amt)
    return f"#{r:02x}{g:02x}{b:02x}"

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
    color   = rank_color(max_r)
    cur_col = rank_color(rating)
    glow    = lighten(color, 0.45)
    bar_w   = min(463, round(463 * max_r / 3500))
    pods = [
        (16,  "CURRENT RATING", str(rating), rank,   cur_col),
        (174, "MAX RATING",     str(max_r),  max_rk, color),
        (332, "SOLVED",         solved_str,  "rated 800 – 2400", "#e6edf3"),
    ]
    pod_svg = ""
    for x, lbl, val, sub, vcol in pods:
        pod_svg += (
            f'<rect x="{x}" y="76" width="147" height="72" rx="8" '
            f'fill="#0f141b" stroke="#21262d"/>'
            f'<text x="{x+15}" y="99" class="lbl">{lbl}</text>'
            f'<text x="{x+15}" y="128" class="val" fill="{vcol}">{val}</text>'
            f'<text x="{x+15}" y="142" class="sub">{sub}</text>'
        )
    return f"""<svg width="495" height="215" viewBox="0 0 495 215" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs>
<linearGradient id="cfLogo" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="#1f6feb"/><stop offset="1" stop-color="#0a4bc2"/>
</linearGradient>
<linearGradient id="cfBar" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{color}" stop-opacity="0.55"/>
<stop offset="1" stop-color="{glow}"/>
</linearGradient>
</defs>
<rect x="0.5" y="0.5" width="494" height="214" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect x="0.5" y="0.5" width="494" height="4" rx="2" fill="{color}"/>
<style>text{{font-family:'Segoe UI',Ubuntu,-apple-system,sans-serif}}
.title{{font-size:16px;font-weight:700;fill:#e6edf3}}
.handle{{font-size:11px;fill:#7d8590}}
.lbl{{font-size:10px;font-weight:600;letter-spacing:.5px;fill:#7d8590}}
.val{{font-size:27px;font-weight:800}}
.sub{{font-size:10.5px;fill:#6e7681}}
.pill{{font-size:11px;font-weight:700;fill:{color}}}
.foot{{font-size:9.5px;fill:#565c64}}</style>
<circle cx="34" cy="38" r="15" fill="url(#cfLogo)"/>
<text x="34" y="43" text-anchor="middle" font-size="14" font-weight="800" fill="#fff" font-family="Segoe UI,sans-serif">CF</text>
<text x="59" y="34" class="title">Codeforces</text>
<text x="59" y="49" class="handle">@{HANDLE}</text>
<rect x="393" y="24" width="86" height="26" rx="13" fill="{color}" fill-opacity="0.12" stroke="{color}" stroke-opacity="0.5"/>
<text x="436" y="41" text-anchor="middle" class="pill">{rank}</text>
<line x1="16" y1="64" x2="479" y2="64" stroke="#21262d"/>
{pod_svg}
<text x="16" y="172" class="lbl" fill="#8b949e" style="letter-spacing:0">Progress to Legendary Grandmaster · 3500</text>
<rect x="16" y="180" width="463" height="8" rx="4" fill="#21262d"/>
<rect x="16" y="180" width="{bar_w}" height="8" rx="4" fill="url(#cfBar)"/>
<text x="16" y="205" class="foot">Auto-updated daily via GitHub Actions · codeforces.com/profile/{HANDLE}</text>
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
