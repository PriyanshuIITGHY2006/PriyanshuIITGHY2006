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

def make_svg(d):
    W, H = 495, 195
    # language bar
    bar_segs, x = "", 16
    for _, color, pct in d["langs"]:
        w = max(1, int((W-32) * pct))
        bar_segs += f'<rect x="{x}" y="130" width="{w}" height="8" rx="2" fill="{color}"/>'
        x += w
    # legend
    legend = ""
    for i, (name, color, pct) in enumerate(d["langs"]):
        lx = 16 + (i % 3) * 155
        ly = 156 + (i // 3) * 18
        legend += (f'<circle cx="{lx+5}" cy="{ly-4}" r="5" fill="{color}"/>'
                   f'<text x="{lx+14}" y="{ly}" class="ln">{name} '
                   f'<tspan class="lp">{pct:.0%}</tspan></text>')
    return f"""<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">
<style>text{{font-family:'Segoe UI',Ubuntu,sans-serif}}
.t1{{font-size:14px;font-weight:600;fill:#e6edf3}}
.t2{{font-size:11px;fill:#6e7681}}
.lbl{{font-size:11px;fill:#8b949e}}
.val{{font-size:24px;font-weight:700;fill:#e6edf3}}
.ln{{font-size:11px;fill:#8b949e}}
.lp{{fill:#6e7681}}</style>
<rect width="{W}" height="{H}" rx="6" fill="#161b22" stroke="#30363d" stroke-width="1"/>
<text x="16" y="26" class="t1">GitHub Overview · @{USERNAME}</text>
<line x1="16" y1="36" x2="479" y2="36" stroke="#21262d" stroke-width="1"/>
<text x="40"  y="64" class="lbl">Commits</text><text x="40"  y="90" class="val">{d["commits"]}</text>
<text x="160" y="64" class="lbl">Pull Requests</text><text x="160" y="90" class="val">{d["prs"]}</text>
<text x="290" y="64" class="lbl">Stars Earned</text><text x="290" y="90" class="val">{d["stars"]}</text>
<text x="400" y="64" class="lbl">Issues</text><text x="400" y="90" class="val">{d["issues"]}</text>
<line x1="16" y1="108" x2="479" y2="108" stroke="#21262d" stroke-width="1"/>
<text x="16" y="124" class="lbl">Top Languages</text>
<rect x="16" y="130" width="{W-32}" height="8" rx="4" fill="#21262d"/>
{bar_segs}
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
