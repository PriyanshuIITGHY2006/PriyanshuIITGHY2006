#!/usr/bin/env python3
"""Fetch GitHub stats via GraphQL API and emit assets/github-metrics.svg."""
import os, sys, requests

USERNAME = "PriyanshuIITGHY2006"
OUT      = "assets/github-metrics.svg"
TOKEN    = os.environ.get("GITHUB_TOKEN", os.environ.get("METRICS_TOKEN", ""))
IGNORE   = {"HTML","CSS","SCSS","TypeScript","JavaScript","MDX",
            "Shell","Dockerfile","Makefile","TeX","Jupyter Notebook"}

def fetch():
    if not TOKEN:
        print("Set GITHUB_TOKEN or METRICS_TOKEN", file=sys.stderr)
        sys.exit(1)
    q = '''{ user(login: "%s") {
      repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
        nodes {
          stargazerCount
          languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
            edges { size node { name color } }
          }
        }
      }
      contributionsCollection {
        totalCommitContributions
        totalPullRequestContributions
        totalIssueContributions
      }
    }}''' % USERNAME
    r = requests.post("https://api.github.com/graphql",
                      json={"query": q},
                      headers={"Authorization": f"Bearer {TOKEN}",
                               "User-Agent": "gh-profile-action/1.0"},
                      timeout=15)
    r.raise_for_status()
    u = r.json()["data"]["user"]
    lang_map, stars = {}, 0
    for repo in u["repositories"]["nodes"]:
        stars += repo["stargazerCount"]
        for e in repo["languages"]["edges"]:
            n = e["node"]["name"]
            if n in IGNORE: continue
            lang_map.setdefault(n, {"color": e["node"]["color"] or "#888", "size": 0})
            lang_map[n]["size"] += e["size"]
    langs  = sorted(lang_map.items(), key=lambda x: -x[1]["size"])[:6]
    total  = sum(v["size"] for _, v in langs) or 1
    c      = u["contributionsCollection"]
    return {
        "commits": c["totalCommitContributions"],
        "prs":     c["totalPullRequestContributions"],
        "issues":  c["totalIssueContributions"],
        "stars":   stars,
        "langs":   [(k, v["color"], v["size"]/total) for k, v in langs],
    }

GH_MARK = ("M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94"
           "-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07"
           "-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 "
           "1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73"
           ".54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z")

def make_svg(d):
    W, H = 495, 205
    stats = [
        (16,  "COMMITS",       d["commits"]),
        (134, "PULL REQUESTS", d["prs"]),
        (252, "STARS EARNED",  d["stars"]),
        (370, "ISSUES",        d["issues"]),
    ]
    pod_svg = ""
    for x, lbl, val in stats:
        pod_svg += (
            f'<rect x="{x}" y="74" width="108" height="60" rx="8" '
            f'fill="#0f141b" stroke="#21262d"/>'
            f'<text x="{x+14}" y="96" class="lbl">{lbl}</text>'
            f'<text x="{x+14}" y="123" class="val">{val}</text>'
        )
    # language bar (clipped for rounded ends) + legend
    bar_segs, legend, bx = "", "", 16
    for i, (name, color, pct) in enumerate(d["langs"]):
        w = max(1, round((W-32) * pct))
        bar_segs += f'<rect x="{bx}" y="160" width="{w}" height="8" fill="{color}"/>'
        bx += w
        lx = 16 + (i % 3) * 155
        legend += (f'<circle cx="{lx+5}" cy="187" r="5" fill="{color}"/>'
                   f'<text x="{lx+15}" y="191" class="ln">{name} '
                   f'<tspan class="lp">{pct:.0%}</tspan></text>')
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect x="0.5" y="0.5" width="494" height="204" rx="12" fill="#0d1117" stroke="#30363d"/>
<rect x="0.5" y="0.5" width="494" height="4" rx="2" fill="#58a6ff"/>
<style>text{{font-family:'Segoe UI',Ubuntu,-apple-system,sans-serif}}
.title{{font-size:16px;font-weight:700;fill:#e6edf3}}
.handle{{font-size:11px;fill:#7d8590}}
.lbl{{font-size:10px;font-weight:600;letter-spacing:.5px;fill:#7d8590}}
.val{{font-size:25px;font-weight:800;fill:#e6edf3}}
.sec{{font-size:10px;font-weight:600;letter-spacing:.5px;fill:#8b949e}}
.ln{{font-size:11px;fill:#c9d1d9}}
.lp{{fill:#6e7681}}</style>
<circle cx="34" cy="36" r="15" fill="#161b22"/>
<g transform="translate(24,26) scale(1.25)"><path d="{GH_MARK}" fill="#e6edf3"/></g>
<text x="59" y="32" class="title">GitHub Overview</text>
<text x="59" y="47" class="handle">@{USERNAME}</text>
<line x1="16" y1="62" x2="479" y2="62" stroke="#21262d"/>
{pod_svg}
<text x="16" y="152" class="sec">TOP LANGUAGES</text>
<clipPath id="ghBar"><rect x="16" y="160" width="463" height="8" rx="4"/></clipPath>
<g clip-path="url(#ghBar)"><rect x="16" y="160" width="463" height="8" fill="#21262d"/>{bar_segs}</g>
{legend}
</svg>"""

def main():
    print(f"Fetching GitHub stats for {USERNAME}…")
    try:
        d = fetch()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(1)
    print(f"  commits={d['commits']} prs={d['prs']} stars={d['stars']} langs={[l[0] for l in d['langs']]}")
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    with open(OUT, "w") as f:
        f.write(make_svg(d))
    print(f"Saved → {OUT}")

if __name__ == "__main__":
    main()
