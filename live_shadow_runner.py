#!/usr/bin/env python3
"""PaperDesk LIVE-SHADOW intraday runner — Bank Nifty + Nifty, per-index, never pooled.

PAPER ONLY. Real money Rs 0. This program places NO broker orders — there is no
order API call anywhere in it. It only READS market data (Upstox script-token
route) and maintains a paper state file + the PaperDesk display feed.

WHAT IT DOES (09:15-15:30 IST on trading days)
  * Polls live 1-min spot candles + LTP quotes via the Upstox script token
    (~/workspace/trading/upstox_refresh/.env -> UPSTOX_ACCESS_TOKEN; the token
    value is never printed or logged).
  * Executes PAPER entries/exits for the PRIMARY frozen November systems only:
      Bank  BNF-PAPER-V1  (lot 30, G0 exits: stop -50 / target +90, square-off 15:10)
      Nifty NF-PAPER-C3G7 (lot 65, G7 exits: -50/+90, then stop->entry+50, target +150)
    Controls (U1-B2 / U1-N1) are NOT run live — they exist in the official EOD log only.
  * Maintains ~/workspace/trading/live_shadow_state.json (atomic writes) and calls
    live_feed_update.py on every order event and every 60 s while a position is open.

SIGNALS — READ THIS (honest design, see live_shadow_run_plan.md)
  The U1 component systems ((lA) v2, V5 v2, Tuned Skill V3, Volrix) were scored
  historically from stored spot-signal files produced by separate backtest
  pipelines; ~/workspace/trading contains NO importable live U1 signal
  generator. This runner therefore does NOT invent signals. It consumes entry
  directives from a bridge file (live_shadow_signals.json) written by an
  intraday signal producer, and applies the FROZEN counting/filter rules
  itself before executing:
    - unique-once per (index, direction) per day, earliest entry;
    - Bank B2 filters: Skill V3 CE legs blocked; Skill-solo legs with
      entry <= 09:55 dropped;
    - Bank NS1 second leg: only after the base leg exited by target/stop with
      exit <= 13:30, signal <= 14:30, room_ratio >= 1.5, CE blocked on a
      bearish-bias day (bias supplied by the producer);
    - Nifty C3: a key is taken only with >= 2 distinct source systems.
  With no bridge file present the runner runs in OBSERVE mode: quotes, MTM and
  exit tracking for any open position still work; no entries are taken.

GUARDRAILS
  * 1 lot per index, hard-coded. Max 1 open position per (index, direction).
  * Square-off 15:10 IST at latest quote, exit_reason=square_off.
  * Kill switch: if ~/workspace/trading/live_shadow_KILLSWITCH exists, the
    runner squares off everything at latest quote, pushes a final feed, exits.
  * Every action is appended to live_shadow_runner.log with an IST timestamp.

Usage:
  python3 live_shadow_runner.py [--date YYYY-MM-DD] [--once] [--no-feed]
  --once runs a single loop iteration (smoke test outside market hours).
"""
import argparse
import csv
import gzip
import io
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, time as dtime, date as ddate
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
TR = Path.home() / "workspace" / "trading"
ENV_FILE = TR / "upstox_refresh" / ".env"
STATE_FILE = TR / "live_shadow_state.json"
SIGNALS_FILE = TR / "live_shadow_signals.json"
KILLSWITCH_FILE = TR / "live_shadow_KILLSWITCH"
LOG_FILE = TR / "live_shadow_runner.log"
FEED_UPDATER = TR / "live_feed_update.py"
API = "https://api.upstox.com"
INSTRUMENTS_URL = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"

INDEX_CFG = {
    "bank": {"spot_key": "NSE_INDEX|Nifty Bank", "underlying": "BANKNIFTY",
             "system": "BNF-PAPER-V1", "lot": 30, "geometry": "G0"},
    "nifty": {"spot_key": "NSE_INDEX|Nifty 50", "underlying": "NIFTY",
              "system": "NF-PAPER-C3G7", "lot": 65, "geometry": "G7"},
}
COST_INR = 220.0
STOP_PTS, TARGET_PTS, RUNNER_TARGET_PTS, LOCK_PTS = 50.0, 90.0, 150.0, 50.0
SQUARE_OFF = dtime(15, 10)
MARKET_CLOSE = dtime(15, 30)


def log(msg: str):
    line = f"{datetime.now(IST).strftime('%Y-%m-%dT%H:%M:%S+05:30')} {msg}"
    print(line, flush=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_token() -> str:
    for line in ENV_FILE.read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise RuntimeError("UPSTOX_ACCESS_TOKEN not found in upstox_refresh/.env")


class Upstox:
    def __init__(self):
        self.token = load_token()

    def get(self, path: str, params=None):
        url = API + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={
            "Authorization": f"Bearer {self.token}", "Accept": "application/json", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())

    def intraday_1m(self, instrument_key: str):
        enc = urllib.parse.quote(instrument_key, safe="")
        data = self.get(f"/v3/historical-candle/intraday/{enc}/minutes/1")
        return (data.get("data") or {}).get("candles") or []

    def ltp(self, instrument_key: str):
        data = self.get("/v3/market-quote/ltp", {"instrument_key": instrument_key})
        d = data.get("data") or {}
        for v in d.values():
            if isinstance(v, dict) and v.get("last_price") is not None:
                return float(v["last_price"])
        return None


# ---------------------------------------------------------------- instruments
class Instruments:
    """Resolves ATM option instrument keys from the Upstox instruments master."""

    def __init__(self):
        # Retry the master download: a truncated read (IncompleteRead) killed
        # the runner on its first entry attempt on 2026-11-09 — download only,
        # no strategy logic affected.
        last_err = None
        raw = None
        for _attempt in range(3):
            try:
                req = urllib.request.Request(INSTRUMENTS_URL, headers={"Accept": "application/gzip", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"})
                raw = urllib.request.urlopen(req, timeout=120).read()
                break
            except Exception as e:  # IncompleteRead / URLError / timeout
                last_err = e
                time.sleep(5)
        if raw is None:
            raise RuntimeError(f"instruments master download failed after 3 attempts: {last_err}")
        text = gzip.decompress(raw).decode()
        self.rows = list(csv.DictReader(io.StringIO(text)))

    def monthly_expiry(self, underlying: str, today: ddate) -> str:
        return self.expiry_in_force(underlying, today)

    def expiry_in_force(self, underlying: str, today: ddate) -> str:
        """Frozen November-spec expiry rule (October convention): the monthly
        expiry of the trade month while it is in force; for trades AFTER that
        monthly expiry, the next expiry in force (earliest expiry >= today).
        November 2026: NIFTY and BANKNIFTY monthly = 2026-11-23; a Nifty trade
        on 2026-11-24..30 therefore uses 2026-12-01, NOT the December monthly."""
        exps = sorted({r["expiry"] for r in self.rows
                       if r.get("name") == underlying and r.get("expiry")})
        month_key = today.strftime("%Y-%m")
        in_month = [e for e in exps if e.startswith(month_key) and e >= str(today)]
        if in_month:
            return in_month[-1]  # last expiry of the month = monthly expiry in force
        future = [e for e in exps if e >= str(today)]
        if not future:
            raise RuntimeError(f"no future expiry for {underlying}")
        return future[0]  # next expiry in force after the monthly has passed

    def option_key(self, underlying: str, expiry: str, strike: int, direction: str) -> str:
        typ = "CE" if direction == "CE" else "PE"
        for r in self.rows:
            if (r.get("name") == underlying and r.get("expiry") == expiry
                    and r.get("option_type") == typ
                    and float(r.get("strike") or 0) == float(strike)):
                return r["instrument_key"]
        raise RuntimeError(f"contract not found {underlying} {strike}{typ} {expiry}")


# ---------------------------------------------------------------- state
def fresh_state(day: str) -> dict:
    return {"date": day,
            "indexes": {k: {"open_positions": [], "closed_today": [],
                            "taken_keys": [], "consumed_signals": [],
                            "base_leg": None} for k in INDEX_CFG}}


def load_state(day: str) -> dict:
    if STATE_FILE.exists():
        st = json.loads(STATE_FILE.read_text())
        if st.get("date") == day:
            return st
        archive = TR / f"live_shadow_state_{st.get('date')}.json"
        STATE_FILE.replace(archive)
        log(f"archived previous state -> {archive.name}")
    return fresh_state(day)


def save_state(st: dict):
    tmp = STATE_FILE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(st, indent=2))
    os.replace(tmp, STATE_FILE)


def push_feed(no_feed: bool):
    if no_feed:
        return
    try:
        subprocess.run([sys.executable, str(FEED_UPDATER)],
                       capture_output=True, text=True, timeout=180)
    except Exception as e:  # feed failure must never kill the runner
        log(f"WARN feed update failed: {e}")


# ---------------------------------------------------------------- signal rules
def validate_and_prepare(idx: str, directive: dict, block: dict, now_t: dtime):
    """Apply the frozen counting/filter rules. Returns (ok, reason, sources)."""
    direction = directive["direction"]
    sources = list(directive.get("sources") or [])
    kind = directive.get("kind", "BASE")
    if direction in block["taken_keys"]:
        return False, "unique-once: key already taken today", sources
    if kind == "BASE" and any(p["direction"] == direction for p in block["open_positions"]):
        return False, "position already open on this key", sources

    if idx == "bank":
        # B2 filter 1: Skill V3 Bank CE blocked.
        if direction == "CE" and "Skill" in sources:
            sources = [s for s in sources if s != "Skill"]
            if not sources:
                return False, "blocked: Skill V3 Bank CE (B2 filter)", sources
        # B2 filter 2: Skill-solo legs with entry <= 09:55 dropped.
        if sources == ["Skill"] and now_t <= dtime(9, 55):
            return False, "dropped: Skill-solo entry <= 09:55 (B2 filter)", sources
        if kind == "NS1_SECOND":
            base = block.get("base_leg")
            if not base or not base.get("exited"):
                return False, "NS1: base leg has not exited", sources
            if base["exit_reason"] not in ("target", "stop"):
                return False, "NS1: base leg did not exit by target/stop", sources
            if base["exit_time"] > "13:30":
                return False, "NS1: base exit after 13:30", sources
            if now_t > dtime(14, 30):
                return False, "NS1: signal after 14:30", sources
            if float(directive.get("room_ratio") or 0) < 1.5:
                return False, "NS1: room_ratio < 1.5", sources
            if direction == "CE" and directive.get("bias") == "bearish":
                return False, "NS1: CE blocked on bearish-bias day", sources
    if idx == "nifty" and kind == "BASE":
        # C3 confirmed-only: >= 2 distinct source systems on the key.
        if len(set(sources)) < 2:
            return False, "C3: solo leg not taken (needs >= 2 sources)", sources
    return True, "ok", sources


# ---------------------------------------------------------------- exits
def check_exit(cfg: dict, pos: dict, premium: float):
    """Returns exit_reason or None. Mutates pos stop/target for G7 runner."""
    entry = pos["entry_premium"]
    if cfg["geometry"] == "G0":
        if premium <= pos["stop"]:
            return "stop"
        if premium >= pos["target"]:
            return "target"
        return None
    # G7 runner-lock50
    if not pos.get("runner_armed") and premium >= entry + TARGET_PTS:
        pos["runner_armed"] = True
        pos["stop"] = entry + LOCK_PTS
        pos["target"] = entry + RUNNER_TARGET_PTS
    if premium <= pos["stop"]:
        return "runner_lock" if pos.get("runner_armed") else "stop"
    if premium >= pos["target"]:
        return "runner_target" if pos.get("runner_armed") else "target"
    return None


def close_position(idx: str, block: dict, pos: dict, premium: float, reason: str):
    lot = INDEX_CFG[idx]["lot"]
    net = round((premium - pos["entry_premium"]) * lot - COST_INR, 2)
    closed = {**pos, "exit_time": datetime.now(IST).strftime("%Y-%m-%dT%H:%M:%S+05:30"),
              "exit_premium": premium, "exit_reason": reason, "net_inr": net}
    block["open_positions"].remove(pos)
    block["closed_today"].append(closed)
    if block.get("base_leg") and block["base_leg"].get("id") == pos["id"]:
        block["base_leg"].update({"exited": True, "exit_reason": reason,
                                  "exit_time": closed["exit_time"][11:16]})
    log(f"CLOSE {idx} {pos['direction']} {pos['strike']} @ {premium} "
        f"reason={reason} net={net:+.2f} (LIVE-SHADOW)")


# ---------------------------------------------------------------- main loop
def run(day: ddate, once: bool, no_feed: bool):
    day_s = str(day)
    api = Upstox()
    log(f"runner start {day_s} (once={once}) — PAPER ONLY, real money Rs 0")
    instruments = None  # lazy: master download only when an entry is attempted
    state = load_state(day_s)
    save_state(state)
    push_feed(no_feed)
    seq = {k: len(state["indexes"][k]["closed_today"]) +
           len(state["indexes"][k]["open_positions"]) for k in INDEX_CFG}
    last_feed_push = time.time()

    while True:
        now = datetime.now(IST)
        if KILLSWITCH_FILE.exists():
            log("KILLSWITCH present — squaring off and exiting")
            for idx, block in state["indexes"].items():
                for pos in list(block["open_positions"]):
                    px = api.ltp(pos["instrument_key"]) or pos["latest_premium"]
                    close_position(idx, block, pos, px, "square_off")
            save_state(state)
            push_feed(no_feed)
            return

        # --- consume signal directives -------------------------------------
        if SIGNALS_FILE.exists():
            try:
                sig = json.loads(SIGNALS_FILE.read_text())
            except Exception:
                sig = {}
            if sig.get("date") == day_s:
                for directive in sig.get("directives") or []:
                    idx = directive.get("index")
                    if idx not in INDEX_CFG:
                        continue
                    block = state["indexes"][idx]
                    if directive["id"] in block["consumed_signals"]:
                        continue
                    block["consumed_signals"].append(directive["id"])
                    ok, reason, sources = validate_and_prepare(
                        idx, directive, block, now.time())
                    if not ok:
                        log(f"REJECT {idx} {directive['id']}: {reason}")
                        save_state(state)
                        continue
                    cfg = INDEX_CFG[idx]
                    spot_candles = api.intraday_1m(cfg["spot_key"])
                    if not spot_candles:
                        log(f"REJECT {idx} {directive['id']}: no spot candles yet")
                        continue
                    spot = float(spot_candles[-1][4])
                    strike = int(round(spot / 100.0) * 100)
                    try:
                        if instruments is None:
                            instruments = Instruments()
                        expiry = instruments.monthly_expiry(cfg["underlying"], day)
                        ikey = instruments.option_key(cfg["underlying"], expiry,
                                                      strike, directive["direction"])
                    except Exception as e:
                        log(f"REJECT {idx} {directive['id']}: instrument resolution failed: {e}")
                        continue
                    px = api.ltp(ikey)
                    if px is None:
                        log(f"REJECT {idx} {directive['id']}: no quote for {ikey}")
                        continue
                    seq[idx] += 1
                    pos = {
                        "id": f"{idx}-{day_s}-{directive['direction']}-{seq[idx]}",
                        "direction": directive["direction"], "strike": strike,
                        "expiry": expiry,
                        "instrument": f"{cfg['underlying']} {strike} {directive['direction']} {expiry}",
                        "instrument_key": ikey,
                        "entry_time": now.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                        "entry_premium": px, "latest_premium": px,
                        "latest_at": now.strftime("%Y-%m-%dT%H:%M:%S+05:30"),
                        "stop": px - STOP_PTS, "target": px + TARGET_PTS,
                        "source": "+".join(sources), "runner_armed": False,
                    }
                    block["open_positions"].append(pos)
                    block["taken_keys"].append(directive["direction"])
                    if directive.get("kind", "BASE") == "BASE" and block["base_leg"] is None:
                        block["base_leg"] = {"id": pos["id"], "exited": False}
                    log(f"OPEN {idx} {pos['direction']} {strike} @ {px} "
                        f"(LIVE-SHADOW, sources={pos['source']})")
                    save_state(state)
                    push_feed(no_feed)
                    last_feed_push = time.time()

        # --- MTM + exits -----------------------------------------------------
        any_open = False
        for idx, block in state["indexes"].items():
            for pos in list(block["open_positions"]):
                any_open = True
                px = api.ltp(pos["instrument_key"])
                if px is None:
                    continue
                pos["latest_premium"] = px
                pos["latest_at"] = now.strftime("%Y-%m-%dT%H:%M:%S+05:30")
                reason = check_exit(INDEX_CFG[idx], pos, px)
                if now.time() >= SQUARE_OFF:
                    reason = "square_off"
                if reason:
                    close_position(idx, block, pos, px, reason)
                    save_state(state)
                    push_feed(no_feed)
                    last_feed_push = time.time()
        if any_open:
            save_state(state)
            if time.time() - last_feed_push >= 60:
                push_feed(no_feed)
                last_feed_push = time.time()

        if once:
            log("single iteration complete (--once)")
            return
        if now.time() >= MARKET_CLOSE:
            log("15:30 reached — runner stops for the day")
            push_feed(no_feed)
            return
        time.sleep(15)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--no-feed", action="store_true")
    a = ap.parse_args()
    day = (datetime.strptime(a.date, "%Y-%m-%d").date() if a.date
           else datetime.now(IST).date())
    run(day, a.once, a.no_feed)


if __name__ == "__main__":
    main()
