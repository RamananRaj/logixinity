#!/usr/bin/env python3
"""
Confluence Sync — Logixinity Website
Runs on every push to main via GitHub Actions.
Reads git commit info, generates an AI summary via Claude, and appends
a changelog entry to the Logixinity Website Changelog page in Confluence.
"""

import os
import json
import subprocess
import urllib.request
import base64
from datetime import datetime, timezone

# ── Config ────────────────────────────────────────────────────────────────────
CONFLUENCE_BASE   = "https://logixinity-team.atlassian.net/wiki"
CHANGELOG_PAGE_ID = "229590"   # Logixinity Website Changelog page in Confluence

# ── Secrets (injected by GitHub Actions) ─────────────────────────────────────
ANTHROPIC_API_KEY    = os.environ["ANTHROPIC_API_KEY"]
CONFLUENCE_EMAIL     = os.environ["CONFLUENCE_EMAIL"]
CONFLUENCE_API_TOKEN = os.environ["CONFLUENCE_API_TOKEN"]


# ── Helpers ───────────────────────────────────────────────────────────────────
def run(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True, text=True).strip()


def git_info() -> tuple:
    msg    = run("git log -1 --pretty=%s")
    author = run("git log -1 --pretty=%an")
    sha    = run("git log -1 --pretty=%h")
    date   = datetime.now(timezone.utc).strftime("%d %B %Y, %H:%M UTC")
    try:
        files = run("git diff HEAD~1 HEAD --name-only | head -20")
        stat  = run("git diff HEAD~1 HEAD --shortstat")
        diff  = run(
            "git diff HEAD~1 HEAD -- '*.html' '*.css' '*.js' 2>/dev/null | head -c 4000"
        )
    except subprocess.CalledProcessError:
        files = run("git show --name-only --pretty='' HEAD | head -20")
        stat  = "Initial commit"
        diff  = ""
    return msg, author, sha, date, files, stat, diff


def claude_summary(commit_msg: str, files: str, diff: str) -> str:
    prompt = (
        "Summarise this website change in 2-3 plain English sentences for a "
        "non-technical stakeholder. Be specific about what visitors or content editors will notice. "
        f"Commit: {commit_msg}. "
        f"Files changed: {files[:400]}. "
        f"Diff excerpt: {diff[:2500]}"
    )
    payload = json.dumps({
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 200,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["content"][0]["text"].strip()


def auth_headers() -> dict:
    token = base64.b64encode(
        f"{CONFLUENCE_EMAIL}:{CONFLUENCE_API_TOKEN}".encode()
    ).decode()
    return {"Authorization": f"Basic {token}", "Content-Type": "application/json"}


def get_page(page_id: str) -> tuple:
    url = f"{CONFLUENCE_BASE}/api/v2/pages/{page_id}?body-format=storage"
    req = urllib.request.Request(url, headers=auth_headers())
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return (
        data["version"]["number"],
        data["body"]["storage"]["value"],
        data["title"],
    )


def update_page(page_id: str, title: str, version: int, body: str) -> None:
    payload = json.dumps({
        "id": page_id,
        "status": "current",
        "title": title,
        "version": {"number": version + 1},
        "body": {"representation": "storage", "value": body},
    }).encode()
    req = urllib.request.Request(
        f"{CONFLUENCE_BASE}/api/v2/pages/{page_id}",
        data=payload,
        method="PUT",
        headers=auth_headers(),
    )
    with urllib.request.urlopen(req) as resp:
        resp.read()


def build_entry(date, sha, commit_msg, author, files, stat, summary) -> str:
    files_html = "".join(
        f"<li><code>{f.strip()}</code></li>"
        for f in files.splitlines() if f.strip()
    )
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    return (
        f"<hr />"
        f"<h3>&#128197; {esc(date)} &nbsp;&middot;&nbsp; <code>{esc(sha)}</code></h3>"
        f"<p><strong>{esc(commit_msg)}</strong></p>"
        f"<p>{esc(summary)}</p>"
        f'<table data-layout="default"><tbody>'
        f"<tr><th><p>Author</p></th><td><p>{esc(author)}</p></td></tr>"
        f"<tr><th><p>Stats</p></th><td><p>{esc(stat)}</p></td></tr>"
        f"<tr><th><p>Files changed</p></th><td><ul>{files_html}</ul></td></tr>"
        f"</tbody></table>"
    )


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    msg, author, sha, date, files, stat, diff = git_info()
    print(f"Commit: {sha} — {msg}")

    if msg.startswith("Merge ") or "[skip ci]" in msg or "[no-doc]" in msg:
        print("Skipping: merge commit or skip flag detected.")
        return

    print("Generating AI summary with Claude...")
    summary = claude_summary(msg, files, diff)
    print(f"Summary: {summary}")

    print(f"Fetching Confluence page {CHANGELOG_PAGE_ID}...")
    version, body, title = get_page(CHANGELOG_PAGE_ID)

    entry    = build_entry(date, sha, msg, author, files, stat, summary)
    new_body = body + entry

    print(f"Updating Confluence (v{version} → v{version + 1})...")
    update_page(CHANGELOG_PAGE_ID, title, version, new_body)
    print("✅ Logixinity Website Changelog updated in Confluence.")


if __name__ == "__main__":
    main()
