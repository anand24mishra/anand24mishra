#!/usr/bin/env python3
"""Rewrite the LIVE-TAIL block in README.md with recent public GitHub activity.

Runs in GitHub Actions (see .github/workflows/live-tail.yml).
Env: GH_USER (required), GITHUB_TOKEN (optional, raises rate limit),
     EVENTS_FILE (optional: read events JSON from a file instead of the API, for testing).
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- LIVE-TAIL:START -->", "<!-- LIVE-TAIL:END -->"
MAX_LINES = 7


def fetch(user):
    if os.environ.get("EVENTS_FILE"):
        return json.loads(Path(os.environ["EVENTS_FILE"]).read_text())
    req = urllib.request.Request(
        f"https://api.github.com/users/{user}/events/public?per_page=100",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-live-tail"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def describe(e, user):
    p, repo = e.get("payload") or {}, e["repo"]["name"]
    repo = repo.split("/", 1)[1] if repo.startswith(f"{user}/") else repo
    t = e["type"]
    if t == "PushEvent":
        branch = (p.get("ref") or "").replace("refs/heads/", "")
        return "INFO ", "push", f"{repo}" + (f" @ {branch}" if branch else "")
    if t == "PullRequestEvent":
        pr = p.get("pull_request") or {}
        action = "merged" if p.get("action") == "closed" and pr.get("merged") else p.get("action", "")
        level = "OK   " if action == "merged" else "INFO "
        return level, f"pr.{action}", f"{repo}#{pr.get('number', p.get('number', '?'))}"
    if t == "CreateEvent" and p.get("ref_type") == "repository":
        return "OK   ", "deploy", f"new repo → {repo}"
    if t == "ReleaseEvent":
        return "OK   ", "release", f"{repo} {(p.get('release') or {}).get('tag_name', '')}".strip()
    if t == "IssuesEvent":
        return "WARN ", f"issue.{p.get('action', '')}", f"{repo}#{(p.get('issue') or {}).get('number', '?')}"
    if t == "WatchEvent":
        return "DEBUG", "star", repo
    if t == "ForkEvent":
        return "DEBUG", "fork", repo
    return None


def render(events, user):
    lines, seen = [], set()
    for e in events:
        d = describe(e, user)
        if not d or (d[1], d[2]) in seen:  # collapse repeated pushes to the same branch
            continue
        seen.add((d[1], d[2]))
        ts = datetime.strptime(e["created_at"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M")
        lines.append(f"{ts}Z  {d[0]}  {d[1]:<13} {d[2]}")
        if len(lines) == MAX_LINES:
            break
    if not lines:
        lines = ["(quiet on the public wire — probably building something private)"]
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    body = "\n".join(lines)
    return (f"{START}\n```console\n$ tail -f /var/log/{user}.log\n{body}\n```\n"
            f"<sub>auto-updated by a GitHub Action · last sync {now} UTC</sub>\n{END}")


def main():
    user = os.environ.get("GH_USER") or sys.exit("GH_USER not set")
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        sys.exit("LIVE-TAIL markers missing from README.md")
    new = re.sub(re.escape(START) + r".*?" + re.escape(END),
                 lambda _: render(fetch(user), user), text, flags=re.S)
    README.write_text(new, encoding="utf-8")


if __name__ == "__main__":
    main()
