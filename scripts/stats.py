#!/usr/bin/env python3
"""Build assets/stats-{dark,light}.svg from the GitHub API (no third-party service).

Runs in GitHub Actions. Env: GH_USER, GITHUB_TOKEN.
For local testing: STATS_JSON=path/to/data.json renders from saved data.
"""
import json
import os
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape as esc

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_svgs import THEMES, SANS, MONO  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "assets"
API = "https://api.github.com"
LANG_COLORS = {
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Go": "#00ADD8", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#663399", "Shell": "#89e051", "HCL": "#844FBA",
    "Dockerfile": "#384d54", "Java": "#b07219", "C++": "#f34b7d", "C": "#555555",
    "Jupyter Notebook": "#DA5B0B", "Makefile": "#427819", "Smarty": "#f0c040",
    "Mustache": "#724b3b", "Kotlin": "#A97BFF", "Swift": "#F05138", "Rust": "#dea584",
}
SKIP_LANGS = {"HTML", "CSS", "Makefile", "Dockerfile", "Smarty", "Mustache", "Procfile"}


def req(url, data=None):
    r = urllib.request.Request(url, data=data, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "profile-stats"})
    if os.environ.get("GITHUB_TOKEN"):
        r.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    if data:
        r.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(r, timeout=30) as resp:
        return json.load(resp)


def fetch(user):
    profile = req(f"{API}/users/{user}")
    repos, page = [], 1
    while True:
        batch = req(f"{API}/users/{user}/repos?per_page=100&type=owner&page={page}")
        repos += batch
        if len(batch) < 100:
            break
        page += 1
    own = [r for r in repos if not r["fork"]]
    langs = {}
    for r in own:
        for lang, n in req(r["languages_url"]).items():
            langs[lang] = langs.get(lang, 0) + n
    data = {"repos": len(own), "stars": sum(r["stargazers_count"] for r in own),
            "followers": profile["followers"], "langs": langs}
    q = {"query": """query($u:String!){user(login:$u){contributionsCollection{
        totalCommitContributions totalPullRequestContributions
        contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}""",
         "variables": {"u": user}}
    try:
        cc = req(f"{API}/graphql", json.dumps(q).encode())["data"]["user"]["contributionsCollection"]
        cal = cc["contributionCalendar"]
        data.update(commits=cc["totalCommitContributions"], prs=cc["totalPullRequestContributions"],
                    contributions=cal["totalContributions"],
                    weeks=[[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]])
    except Exception as e:  # heatmap is optional
        print("graphql unavailable:", e)
    return data


def fmt(n):
    return f"{n / 1000:.1f}k" if n >= 1000 else str(n)


def render(d, t):
    W = 880
    has_cal = "weeks" in d
    H = 330 if has_cal else 200
    b = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{t["card"]}" stroke="{t["line"]}"/>']
    # metrics
    metrics = [("repositories", d["repos"]), ("stars", d["stars"]), ("followers", d["followers"])]
    if has_cal:
        metrics = [("contributions · 1y", d["contributions"]), ("commits · 1y", d["commits"]),
                   ("pull requests · 1y", d["prs"])] + metrics
    cw = (W - 44) / len(metrics)
    for i, (label, val) in enumerate(metrics):
        x = 22 + i * cw
        b.append(f'<text x="{x}" y="52" font-family="{SANS}" font-size="26" font-weight="700" fill="{t["fg"]}">{fmt(val)}</text>'
                 f'<text x="{x}" y="72" font-family="{MONO}" font-size="11" fill="{t["muted"]}">{esc(label)}</text>')
    # languages
    langs = {k: v for k, v in d["langs"].items() if k not in SKIP_LANGS}
    total = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    other = total - sum(v for _, v in top)
    if other > 0:
        top.append(("Other", other))
    y = 100
    b.append(f'<text x="22" y="{y}" font-family="{MONO}" font-size="11" fill="{t["muted"]}">languages · across own public repos</text>')
    x, bw = 22, W - 44
    b.append(f'<clipPath id="lc"><rect x="22" y="{y + 10}" width="{bw}" height="10" rx="5"/></clipPath><g clip-path="url(#lc)">')
    for lang, v in top:
        w = bw * v / total
        b.append(f'<rect x="{x}" y="{y + 10}" width="{w + 0.5}" height="10" fill="{LANG_COLORS.get(lang, t["muted"])}"/>')
        x += w
    b.append("</g>")
    lx, ly = 22, y + 44
    for lang, v in top:
        label = f"{lang} {100 * v / total:.1f}%"
        if lx + len(label) * 7 + 30 > W - 22:
            lx, ly = 22, ly + 22
        b.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{LANG_COLORS.get(lang, t["muted"])}"/>'
                 f'<text x="{lx + 16}" y="{ly}" font-family="{MONO}" font-size="12" fill="{t["fg"]}">{esc(label)}</text>')
        lx += len(label) * 7.2 + 34
    # contribution heatmap
    if has_cal:
        weeks = d["weeks"][-53:]
        peak = max((c for w in weeks for c in w), default=0) or 1
        levels = [t["chip"], t["green"] + "55", t["green"] + "88", t["green"] + "bb", t["green"]]
        y0, cell, gap = 196, 12, 3
        x0 = W - 22 - len(weeks) * (cell + gap) + gap
        b.append(f'<text x="22" y="{y0 - 10}" font-family="{MONO}" font-size="11" fill="{t["muted"]}">last 12 months</text>')
        for wi, week in enumerate(weeks):
            for di, c in enumerate(week):
                lvl = 0 if c == 0 else min(4, 1 + int(3 * c / peak))
                b.append(f'<rect x="{x0 + wi * (cell + gap)}" y="{y0 + di * (cell + gap)}" width="{cell}" height="{cell}" rx="2.5" fill="{levels[lvl]}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="GitHub stats: {d["repos"]} repositories, {d["stars"]} stars"><title>GitHub stats</title>{"".join(b)}</svg>')


def main():
    if os.environ.get("STATS_JSON"):
        d = json.loads(Path(os.environ["STATS_JSON"]).read_text())
    else:
        d = fetch(os.environ.get("GH_USER") or sys.exit("GH_USER not set"))
    for name, t in THEMES.items():
        (OUT / f"stats-{name}.svg").write_text(render(d, t), encoding="utf-8")
    print("stats:", {k: v for k, v in d.items() if k != "weeks"})


if __name__ == "__main__":
    main()
