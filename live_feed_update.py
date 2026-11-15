#!/usr/bin/env python3
"""PaperDesk LIVE-SHADOW feed updater.

Reads the live shadow runner's state file (live_shadow_state.json), builds the
feed payload defined in live_feed_schema.md, and publishes it.

Publish targets (first that is configured wins):
  1. Secret GitHub Gist — if env PAPERDESK_GIST_ID and GITHUB_TOKEN are set:
     PATCH https://api.github.com/gists/<id> with files.feed.json content.
     (The token is read from the environment only and is never printed.)
  2. Repo file (current route) — live_feed/feed.json in
     Chowdarichandu/trading_systems@main, via the Muse GitHub connector CLI
     (/opt/hatch/bin/github). The connector holds the auth; this script never
     sees a GitHub credential. NOTE: that repo is private, so its raw URL is
     not phone-fetchable without auth — see live_shadow_run_plan.md.

Usage:
  python3 live_feed_update.py [--state PATH] [--dry-run] [--market-open true|false]

--dry-run prints the payload and sends nothing.
Paper only. Real money Rs 0. This script places no orders of any kind.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
TR = Path.home() / "workspace" / "trading"
DEFAULT_STATE = TR / "live_shadow_state.json"
GH_CLI = "/opt/hatch/bin/github"
REPO_OWNER, REPO_NAME, REPO_BRANCH, REPO_PATH = (
    "Chowdarichandu", "trading_systems", "main", "live_feed/feed.json")

INDEX_META = {
    "bank": {"label": "Bank Nifty — BNF-PAPER-V1 (LIVE-SHADOW)",
             "system": "BNF-PAPER-V1", "lot": 30, "cost_per_trade_inr": 220},
    "nifty": {"label": "Nifty — NF-PAPER-C3G7 (LIVE-SHADOW)",
              "system": "NF-PAPER-C3G7", "lot": 65, "cost_per_trade_inr": 220},
}


def now_ist() -> datetime:
    return datetime.now(IST)


def market_state(now: datetime, override_open):
    if override_open is not None:
        return (override_open, "open" if override_open else "closed")
    if now.weekday() >= 5:
        return False, "closed (weekend)"
    t = now.time()
    if dtime(9, 15) <= t <= dtime(15, 30):
        return True, "open"
    if t < dtime(9, 15):
        return False, "pre-market"
    return False, "closed"


def build_payload(state: dict, override_open=None) -> dict:
    now = now_ist()
    is_open, mstate = market_state(now, override_open)
    indexes = {}
    for key, meta in INDEX_META.items():
        block = (state.get("indexes") or {}).get(key) or {}
        closed = block.get("closed_today") or []
        day_net = round(sum(float(c.get("net_inr", 0)) for c in closed), 2)
        indexes[key] = {
            **meta,
            "open_positions": block.get("open_positions") or [],
            "closed_today": closed,
            "day_net_inr": day_net,
        }
    return {
        "schema_version": 1,
        "mode": "LIVE-SHADOW",
        "note": ("Paper trading display feed only. Real money Rs 0. LIVE-SHADOW "
                 "numbers are a live viewing layer; the official November record "
                 "is the end-of-day candle-scored log."),
        "date": state.get("date") or now.strftime("%Y-%m-%d"),
        "updated_at": now.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
        "market_open": is_open,
        "market_state": mstate,
        "indexes": indexes,
    }


def publish_gist(payload: dict) -> str:
    gist_id = os.environ["PAPERDESK_GIST_ID"]
    token = os.environ["GITHUB_TOKEN"]  # never printed
    body = json.dumps({
        "files": {"feed.json": {"content": json.dumps(payload, indent=2)}}
    }).encode()
    req = urllib.request.Request(
        f"https://api.github.com/gists/{gist_id}", data=body, method="PATCH",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        if resp.status != 200:
            raise RuntimeError(f"gist PATCH returned HTTP {resp.status}")
    return f"gist:{gist_id}"


def _gh_json(args):
    out = subprocess.run([GH_CLI] + args, capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        raise RuntimeError(f"github CLI failed: {out.stderr.strip()[:300]}")
    return json.loads(out.stdout)


def publish_repo(payload: dict) -> str:
    # Current blob sha is required to update an existing file.
    sha = None
    try:
        res = _gh_json(["call-read-tool", "--name", "get_file_contents",
                        "--arguments-json", json.dumps(
                            {"owner": REPO_OWNER, "repo": REPO_NAME,
                             "path": REPO_PATH, "ref": REPO_BRANCH})])
        text = res["result"]["content"][0]["text"]
        sha = json.loads(text).get("sha")
    except Exception:
        sha = None  # file may not exist yet -> create without sha
    args = {"owner": REPO_OWNER, "repo": REPO_NAME, "branch": REPO_BRANCH,
            "path": REPO_PATH,
            "message": f"live feed update {payload['updated_at']}",
            "content": json.dumps(payload, indent=2)}
    if sha:
        args["sha"] = sha
    _gh_json(["call-tool", "--name", "create_or_update_file",
              "--arguments-json", json.dumps(args)])
    return f"repo:{REPO_OWNER}/{REPO_NAME}@{REPO_BRANCH}:{REPO_PATH}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default=str(DEFAULT_STATE))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--market-open", choices=["true", "false"], default=None)
    a = ap.parse_args()

    state = {}
    sp = Path(a.state)
    if sp.exists():
        state = json.loads(sp.read_text())
    override = None if a.market_open is None else a.market_open == "true"
    payload = build_payload(state, override)

    if a.dry_run:
        print(json.dumps(payload, indent=2))
        print("[dry-run] nothing sent", file=sys.stderr)
        return 0

    if os.environ.get("PAPERDESK_GIST_ID") and os.environ.get("GITHUB_TOKEN"):
        target = publish_gist(payload)
    else:
        target = publish_repo(payload)
    print(f"[feed] published -> {target} at {payload['updated_at']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
