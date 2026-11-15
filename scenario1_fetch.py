#!/usr/bin/env python3
"""SCENARIO-PROOFING ITEM 1 — Nifty REGIME-REV premium rescue fetch.

Computes the frozen REGIME-REV signals on Nifty Jan-Oct 2026 spot
(identical logic to november_regime_family.py) and lists every
premium contract-day the gate needs:
  - each fired REGIME day: reversal side (real + P3) and morning
    side (P2), same confirmation strike;
  - each fired NON-regime day with a confirmation: reversal side
    (P1).
For each needed contract-day: if the shared fetched-cache file
(oi_buildup_data/candles_NIFTY_<strike><TYP>_<exp>_<day>.json)
already holds a complete series (first bar <= 09:20 and a 15:10
bar), skip. Otherwise fetch via round 1's frozen machinery
(oi_buildup_score.fetch_bars — expired-instruments route, browser
User-Agent, caches into oi_buildup_data itself, 0.3s pacing).
Sequential and gentle. On HTTP 429 (RateLimited): HARD STOP —
progress is written to scenario1_fetch_progress.json and the
script exits 3 without retrying or switching routes.
Paper only; no orders; no book or ledger is touched.
"""
import csv, json, sys, time
import importlib.util
from pathlib import Path
import pandas as pd

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
_spec = importlib.util.spec_from_file_location(
    "oi_buildup_score", TR / "oi_buildup_score.py")
obs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(obs)

Q3 = 0.574
STEP = 50
PROG = TR / "scenario1_fetch_progress.json"
FETCH_DIR = TR / "oi_buildup_data"


def load_spot():
    s = pd.read_csv(TR / "data/progressive/NIFTY/spot_5m.csv")
    s["timestamp"] = pd.to_datetime(s["timestamp"]).dt.tz_localize(None)
    s = s[(s["timestamp"] >= "2026-01-01") & (s["timestamp"] <= "2026-10-31")]
    s["date"] = s["timestamp"].dt.strftime("%Y-%m-%d")
    s["time"] = s["timestamp"].dt.strftime("%H:%M")
    out = {}
    for d, g in s.groupby("date"):
        if len(g) >= 70:
            out[d] = {r.time: (float(r.open), float(r.high),
                               float(r.low), float(r.close))
                      for r in g.itertuples()}
    return out


def morning_info(bars):
    win = [t for t in sorted(bars) if "09:15" <= t <= "10:55"]
    if len(win) < 21 or "09:15" not in bars or "10:55" not in bars:
        return None
    O = bars["09:15"][0]; C11 = bars["10:55"][3]
    H = max(bars[t][1] for t in win); L = min(bars[t][2] for t in win)
    return dict(O=O, C11=C11, M=(H + L) / 2.0,
                move_pct=(C11 - O) / O * 100.0,
                dirn=(1 if C11 > O else (-1 if C11 < O else 0)))


def confirmation(bars, mi):
    for t in sorted(bars):
        if "11:00" <= t <= "15:05":
            c = bars[t][3]
            if mi["dirn"] > 0 and c < mi["M"]:
                return t, c
            if mi["dirn"] < 0 and c > mi["M"]:
                return t, c
    return None, None


EXP = {}
with open(TR / "oi_history/nifty_daily_oi.csv") as f:
    for r in csv.DictReader(f):
        EXP[r["date"]] = r["expiry"]


def needed_contracts():
    days = load_spot()
    need = {}   # (exp, strike, typ, day) -> [roles]
    prev_close = None
    fired_regime = fired_nonreg = 0
    for day in sorted(days):
        bars = days[day]
        first_open = bars[sorted(bars)[0]][0]
        gap = ((first_open - prev_close) / prev_close * 100
               if prev_close else None)
        prev_close = bars[sorted(bars)[-1]][3]
        mi = morning_info(bars)
        if mi is None or mi["dirn"] == 0 or gap is None:
            continue
        regime = abs(gap) >= Q3 or abs(mi["move_pct"]) >= 0.7
        ct, cc = confirmation(bars, mi)
        if ct is None:
            continue
        strike = int(round(cc / STEP)) * STEP
        exp = EXP.get(day)
        if not exp:
            continue
        rev = "PE" if mi["dirn"] > 0 else "CE"
        morn = "CE" if mi["dirn"] > 0 else "PE"
        if regime:
            fired_regime += 1
            need.setdefault((exp, strike, rev, day), []).append("real/P3")
            need.setdefault((exp, strike, morn, day), []).append("P2")
        else:
            fired_nonreg += 1
            need.setdefault((exp, strike, rev, day), []).append("P1")
    return need, fired_regime, fired_nonreg


def cache_complete(exp, strike, typ, day):
    fn = FETCH_DIR / f"candles_NIFTY_{int(strike)}{typ}_{exp}_{day}.json"
    if not fn.exists():
        return False
    try:
        body = json.loads(fn.read_text())
    except Exception:
        return False
    cd = [c for c in ((body.get("data") or {}).get("candles") or [])
          if c[0][:10] == day]
    if not cd:
        return False
    times = {c[0][11:16] for c in cd}
    return min(times) <= "09:20" and "15:10" in times


def main():
    need, fr, fnr = needed_contracts()
    print(f"fired regime={fr} nonregime={fnr} contract-days needed="
          f"{len(need)}", flush=True)
    todo = [k for k in sorted(need, key=lambda k: (k[3], k[0]))
            if not cache_complete(*k)]
    print(f"already complete in cache: {len(need) - len(todo)}; "
          f"to fetch: {len(todo)}", flush=True)
    done, failed = [], []
    state = dict(needed=len(need), already=len(need) - len(todo),
                 fetched=0, failed=[], rate_limited=False,
                 stopped_at=None)
    try:
        for i, (exp, strike, typ, day) in enumerate(todo):
            bars = obs.fetch_bars("NIFTY", exp, strike, typ, day)
            if bars and cache_complete(exp, strike, typ, day):
                done.append((exp, strike, typ, day))
            else:
                failed.append((exp, strike, typ, day,
                               "no_bars" if not bars else "incomplete"))
            state["fetched"] = len(done)
            state["failed"] = failed
            if i % 20 == 19:
                PROG.write_text(json.dumps(state, indent=1))
                print(f"progress {i + 1}/{len(todo)} fetched_ok="
                      f"{len(done)} failed={len(failed)}", flush=True)
            time.sleep(0.2)
    except obs.RateLimited:
        state["rate_limited"] = True
        state["stopped_at"] = (todo[len(done) + len(failed)]
                               if len(done) + len(failed) < len(todo)
                               else None)
        PROG.write_text(json.dumps(state, indent=1))
        print("RATE_LIMIT_STOP — hard stop, progress saved", flush=True)
        return 3
    state["fetched"] = len(done)
    state["failed"] = failed
    PROG.write_text(json.dumps(state, indent=1))
    print(f"FETCH DONE: ok={len(done)} failed={len(failed)}", flush=True)
    for f_ in failed:
        print("  FAILED", f_, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
