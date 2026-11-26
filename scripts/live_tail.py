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
        return f"Pushed to {repo}"
    if t == "PullRequestEvent":
        pr = p.get("pull_request") or {}
        n = pr.get("number", p.get("number", "?"))
        if p.get("action") == "closed" and pr.get("merged"):
            return f"Merged PR #{n} in {repo}"
        if p.get("action") == "opened":
            return f"Opened PR #{n} in {repo}"
        return None
    if t == "CreateEvent" and p.get("ref_type") == "repository":
        return f"Created {repo}"
    if t == "ReleaseEvent":
        return f"Released {repo} {(p.get('release') or {}).get('tag_name', '')}".strip()
    if t == "IssuesEvent" and p.get("action") == "opened":
        return f"Opened issue #{(p.get('issue') or {}).get('number', '?')} in {repo}"
    if t == "ForkEvent":
        return f"Forked {repo}"
    return None


def render(events, user):
    lines, seen = [], set()
    # the events API is not strictly time-ordered; newest first
    for e in sorted(events, key=lambda e: e["created_at"], reverse=True):
        d = describe(e, user)
        if not d or d in seen:  # collapse repeated pushes to the same repo
            continue
        seen.add(d)
        day = e["created_at"][:10]
        lines.append(f"- {day}: {d}")
        if len(lines) == MAX_LINES:
            break
    if not lines:
        lines = ["- No recent public activity."]
    return f"{START}\n" + "\n".join(lines) + f"\n\n<sub>Updated automatically from public GitHub activity.</sub>\n{END}"


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
