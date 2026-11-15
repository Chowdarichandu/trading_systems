#!/usr/bin/env python3
"""STOCK ENGINE — LIVE engine (owner order 2026-11-11 19:48 IST: run
DURING market hours, work like Bank Nifty — picks lock intraday, no
after-close selection).

Construction (simulation: stock_engine_live_sim.py; report:
stock_engine_live_2026-11-11.md):
  Universe 1,081 names. Components: ONLY the four that are causally
  determinable intraday in their own frozen form — P2F, P2F-R2,
  R2-LOWBAND (reaction family; determined pre-open from the prior
  reaction-day close + event calendar; entry = 09:15 open) and
  N4-V3 (09:25-bar move >= 1%; entry = 09:30-bar close, determined
  09:35). F4 / INV-LONG / INV-ABOVE are NOT_LIVE: their frozen
  pool_pick chooses each round's signal by rank across both detector
  heads' first signals over the whole day (v4 windows to 14:30), so
  a trade's identity is not fixed at its entry time (truncation
  audit evidence in the sim report). They are excluded, never
  approximated.
  Selection (Variant D economics): representative = the component's
  trade for the stock-day; magnitude = |reaction %| (reaction comps)
  or |09:25 move %| (N4); within-component percentile (populations
  are COMPLETE before entry for these four, so live percentiles are
  the retrospective ones); owner = strongest component; score =
  confluence x 100 + owner percentile (confluence = distinct
  components determined so far flagging the stock); lock at the
  decision points 09:10 (reaction batch) and 09:35 (N4 batch) while
  slots remain: owner percentile >= 90, entry <= Rs 5,000, max 6
  picks/day, each stock once. A locked pick is final; a candidate
  not locked at its batch's decision point is dead.
  Detection runs through the frozen book Evaluator (the same code
  the wide producer uses) — entries/exits are the components' own;
  this script's selection layer only designates which Evaluator
  positions are official Stock Engine picks, announces them on lock
  (STOCK_ENGINE_LIVE_PICK) and their exits (STOCK_ENGINE_EXIT), and
  ledgers the picks. Paper only, real money Rs 0. Basis: provisional
  per 100 shares, Rs 40/trade; Rs 25,000/trade lens tracked.

Modes:
  (default)   one live tick (cron Phase 1, 09:15-15:35)
  --summary   accounting only (cron Phase 2): day + November totals
              from the ledger; selects nothing
  --replay D  offline: run the simulation derivation for date D over
              the stored pool and print the picks it would have
              locked (dry-run evidence; writes no ledger)
  --dry-run   tick mechanics with .dryrun state/ledger files

Guard: November 2026, Mon-Fri only (December needs an amendment).
Upstox: browser User-Agent on every request (via the wide producer's
fetcher); HTTP 429 = hard stop, no writes that tick.
"""
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stocks_wide_nse_shadow_producer as wide

IST = ZoneInfo("Asia/Kolkata")
HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "stock_engine_live_state.json")
LEDGER = os.path.join(HERE, "stock_engine_live_log.csv")
LOG = os.path.join(HERE, "stock_engine_live.log")
DRY_STATE = os.path.join(HERE, "stock_engine_live_state.dryrun.json")
DRY_LEDGER = os.path.join(HERE, "stock_engine_live_log.dryrun.csv")

REACTION_COMPS = ("P2F", "P2F-R2", "R2-LOWBAND")
LIVE_COMPS = set(REACTION_COMPS) | {"N4-V3"}
FLOOR_PCT = 90.0
PRICE_CAP = 5000.0
MAX_PICKS = 6
CAPITAL = 25000.0
LEDGER_FIELDS = ["date", "stock", "comp", "dir", "lock_time",
                 "entry_time", "entry", "exit_time", "exit",
                 "exit_reason", "net", "fc_shares", "fc_net",
                 "norm_pct", "confluence", "mode"]


def lens(entry, net):
    if entry and entry > 0:
        shares = max(1, int(CAPITAL // entry)) if entry <= CAPITAL else 1
    else:
        shares = 1
    return shares, round((net + 40.0) / 100.0 * shares - 40.0, 2)


def norm_pct(reps):
    """Within-component percentile (100*(n-i)/n), ranked by
    (-magnitude, entry_time, stock) — the v2 convention."""
    by_comp = defaultdict(list)
    for r in reps:
        by_comp[r["comp"]].append(r)
    out = {}
    for comp, rows in by_comp.items():
        rows = sorted(rows, key=lambda r: (-r["magnitude"],
                                           r["entry_time"], r["stock"]))
        n = len(rows)
        for i, r in enumerate(rows):
            out[(comp, r["stock"])] = 100.0 * (n - i) / n
    return out


def evaluate_locks(state, batch_det):
    """Lock picks from the batch determined at `batch_det`, per the
    live construction spec. Mutates state; returns new lock dicts."""
    reps = state["reps"]
    pcts = norm_pct(reps)
    for r in reps:
        r["norm_pct"] = pcts[(r["comp"], r["stock"])]
    batch_stocks = {r["stock"] for r in reps if r["det"] == batch_det}
    locked = {l["stock"] for l in state["locks"]}
    cands = []
    for stock in batch_stocks - locked:
        s_reps = [r for r in reps if r["stock"] == stock]
        owner = max(s_reps, key=lambda r: r["norm_pct"])
        conf = len({r["comp"] for r in s_reps})
        cands.append((conf * 100 + owner["norm_pct"], stock, owner, conf))
    cands.sort(key=lambda x: (-x[0], x[1]))
    new = []
    for score, stock, owner, conf in cands:
        if len(state["locks"]) >= MAX_PICKS:
            break
        if owner["norm_pct"] < FLOOR_PCT or owner["entry"] > PRICE_CAP:
            continue
        lk = {"stock": stock, "comp": owner["comp"], "dir": owner["dir"],
              "entry_time": owner["entry_time"], "entry": owner["entry"],
              "lock_time": batch_det, "norm_pct": owner["norm_pct"],
              "confluence": conf, "exited": False}
        state["locks"].append(lk)
        new.append(lk)
    return new


def load_state(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None


def save_state(path, state):
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f)
    os.replace(tmp, path)


def append_ledger(path, row):
    new = not os.path.exists(path)
    with open(path, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LEDGER_FIELDS)
        if new:
            w.writeheader()
        w.writerow(row)


# ---------------------------------------------------------------- tick
def run_tick(dry=False):
    now = datetime.now(IST)
    today = now.date().isoformat()
    hm = now.strftime("%H:%M")
    if not (today.startswith("2026-11") and now.weekday() < 5):
        print(f"STOCK_ENGINE_LIVE_GUARD date={today} outside Nov 2026 "
              f"Mon-Fri — no run", flush=True)
        return 0
    state_path = DRY_STATE if dry else STATE
    ledger_path = DRY_LEDGER if dry else LEDGER
    state = load_state(state_path)
    if not state or state.get("date") != today:
        state = {"date": today, "ev_entered": [], "ev_positions": {},
                 "reps": [], "locks": [], "stepped_ok": [],
                 "n4_bars_ready": False, "scan_done": False,
                 "reaction_dp_done": False, "n4_dp_done": False,
                 "scan_coverage": None}
    # universe data + runtime calendar + frozen Evaluator (the same
    # path the wide producer runs)
    wide.refresh_daily(today)
    wide.seed_and_merge_calendar(today)
    wide.build_runtime_calendar(today)
    ev = wide.base.Evaluator(today, wide.RUNTIME_CAL)
    ev.entered = {tuple(x) for x in state["ev_entered"]}
    ev.positions = {tuple(k.split("|")): v
                    for k, v in state["ev_positions"].items()}
    cand_syms = {c["stock"] for c in ev.cands}
    n4_syms = {s for (s, d) in ev.n4_days if d == today}
    actives = sorted(cand_syms | n4_syms |
                     {s for (_, s) in ev.positions})
    do_scan = (not state["scan_done"]) and hm >= "09:32"
    fetch_syms = list(wide.WIDE) if do_scan else actives
    try:
        fetched = wide.fetch_many(fetch_syms)
    except wide.RateLimited:
        print(f"STOCK_ENGINE_LIVE_RATELIMITED date={today} — no "
              f"writes this tick", flush=True)
        return 3
    if do_scan:
        state["scan_done"] = True
        state["scan_coverage"] = sum(1 for s in wide.WIDE
                                     if fetched.get(s))
    cand_mag = {(c["comp"], c["stock"]): abs(c["reaction_ret_pct"])
                for c in ev.cands}
    stepped_ok = set(state["stepped_ok"])
    new_locks = []
    exit_rows = []
    for sym in fetch_syms:
        bars = wide.completed(fetched.get(sym) or [], now, dry)
        if not bars:
            continue
        actions = ev.step(sym, bars)
        stepped_ok.add(sym)
        if sym in n4_syms and any(b["time"] == "09:30" for b in bars):
            state["n4_bars_ready"] = True
        for a in actions:
            if a.get("layer") != "book":
                continue
            if a["action"] == "ENTRY" and a["comp"] in LIVE_COMPS:
                if a["comp"] in REACTION_COMPS:
                    mag = cand_mag.get((a["comp"], a["stock"]), 0.0)
                    det = "09:10"
                else:
                    pc = ev.prev_close(sym)
                    b925 = next((b for b in bars
                                 if b["time"] == "09:25"), None)
                    mag = (abs(b925["close"] / pc - 1) * 100
                           if pc and b925 else 0.0)
                    det = "09:35"
                if not any(r["comp"] == a["comp"]
                           and r["stock"] == a["stock"]
                           for r in state["reps"]):
                    state["reps"].append(
                        {"comp": a["comp"], "stock": a["stock"],
                         "dir": a["dir"], "entry_time": a["entry_time"],
                         "entry": a["entry"], "magnitude": mag,
                         "det": det})
            elif a["action"] == "EXIT":
                for lk in state["locks"]:
                    if (lk["comp"] == a["comp"]
                            and lk["stock"] == a["stock"]
                            and not lk["exited"]):
                        lk["exited"] = True
                        sh, fc = lens(lk["entry"], a["net"])
                        row = {"date": today, "stock": lk["stock"],
                               "comp": lk["comp"], "dir": lk["dir"],
                               "lock_time": lk["lock_time"],
                               "entry_time": lk["entry_time"],
                               "entry": lk["entry"],
                               "exit_time": a["exit_time"],
                               "exit": a["exit"],
                               "exit_reason": a["exit_reason"],
                               "net": a["net"], "fc_shares": sh,
                               "fc_net": fc,
                               "norm_pct": lk["norm_pct"],
                               "confluence": lk["confluence"],
                               "mode": "LIVE-SHADOW"}
                        append_ledger(ledger_path, row)
                        exit_rows.append(row)
    state["stepped_ok"] = sorted(stepped_ok)
    # decision points
    if not state["reaction_dp_done"]:
        if cand_syms <= stepped_ok or hm >= "09:45":
            new_locks += evaluate_locks(state, "09:10")
            state["reaction_dp_done"] = True
    if not state["n4_dp_done"]:
        if (state["scan_done"] and state["n4_bars_ready"]) or hm >= "10:15":
            new_locks += evaluate_locks(state, "09:35")
            state["n4_dp_done"] = True
    state["ev_entered"] = sorted([list(x) for x in ev.entered])
    state["ev_positions"] = {"|".join(k): v
                             for k, v in ev.positions.items()}
    save_state(state_path, state)
    for lk in new_locks:
        print("STOCK_ENGINE_LIVE_PICK " + json.dumps(
            {"date": today, "stock": lk["stock"], "comp": lk["comp"],
             "dir": lk["dir"], "entry_time": lk["entry_time"],
             "entry": lk["entry"], "lock_time": lk["lock_time"],
             "basis": (f"Stock Engine live — {lk['comp']} locked at "
                       f"the {lk['lock_time']} decision point; "
                       f"percentile {lk['norm_pct']:.1f} in component, "
                       f"confluence {lk['confluence']}; provisional "
                       f"per 100 shares, paper")}), flush=True)
    for row in exit_rows:
        print("STOCK_ENGINE_EXIT " + json.dumps(
            {"date": today, "stock": row["stock"], "comp": row["comp"],
             "dir": row["dir"], "entry_time": row["entry_time"],
             "entry": row["entry"], "exit_time": row["exit_time"],
             "exit": row["exit"], "exit_reason": row["exit_reason"],
             "net": row["net"], "fc_net": row["fc_net"]}), flush=True)
    print(f"STOCK_ENGINE_TICK date={today} time={hm} "
          f"reps={len(state['reps'])} locks={len(state['locks'])} "
          f"exits_total={sum(1 for l in state['locks'] if l['exited'])} "
          f"scan={'done' if state['scan_done'] else 'pending'} "
          f"dry={dry}", flush=True)
    return 0


# ------------------------------------------------------------- summary
def run_summary():
    now = datetime.now(IST)
    today = now.date().isoformat()
    rows = []
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            rows = list(csv.DictReader(f))
    nov = [r for r in rows if r["date"].startswith("2026-11")]
    day = [r for r in nov if r["date"] == today]
    state = load_state(STATE) or {}
    locks_today = state.get("locks", []) if state.get("date") == today \
        else []

    def agg(rs):
        net = sum(float(r["net"]) for r in rs)
        fc = sum(float(r["fc_net"]) for r in rs)
        by_stock = defaultdict(float)
        for r in rs:
            by_stock[r["stock"]] += float(r["net"])
        top3 = sum(sorted(by_stock.values(), reverse=True)[:3]) \
            if by_stock else 0.0
        return net, fc, net - top3

    dn, dfc, _ = agg(day)
    mn, mfc, mex = agg(nov)
    print("STOCK ENGINE — DAY SUMMARY", flush=True)
    print(f"date={today} picks_locked={len(locks_today)} "
          f"exited={len(day)}", flush=True)
    for lk in locks_today:
        ex = next((r for r in day if r["stock"] == lk["stock"]
                   and r["comp"] == lk["comp"]), None)
        print(f"  {lk['lock_time']} {lk['stock']} {lk['comp']} "
              f"{lk['dir']} entry {lk['entry_time']} @{lk['entry']}"
              + (f" -> exit {ex['exit_time']} @{ex['exit']} "
                 f"({ex['exit_reason']}) net {float(ex['net']):+.2f} "
                 f"lens {float(ex['fc_net']):+.2f}" if ex
                 else " -> still open at summary time"), flush=True)
    print(f"DAY net={dn:+.2f} lens={dfc:+.2f} (provisional per 100 "
          f"shares / Rs 25,000 lens, paper, real money Rs 0)",
          flush=True)
    print(f"NOVEMBER total: trades={len(nov)} net={mn:+.2f} "
          f"lens={mfc:+.2f} ex-top-3={mex:+.2f}", flush=True)
    return 0


# -------------------------------------------------------------- replay
def run_replay(date):
    import stock_engine_live_sim as SIM
    import sarvasetu_top3_build as V1
    g = V1.load_machinery(SIM.ROOT, SIM.HI)
    days = [d for d in SIM.ALL_DAYS
            if any(dd == d for (_s, dd) in g["DAYCTX"])]
    pct_full, _sizes = V1.inv_pool_percentiles(g, days)
    pool = V1.build_book_detailed(g, SIM.MERGED_CAL, SIM.LO, SIM.HI,
                                  days, pct_full)
    day_pool = [t for t in pool if t["date"] == date
                and t["comp"] in SIM.LIVE_COMPS]
    _reps, picks = SIM.derive_day(date, day_pool, [], g["NS"]["RANK"])
    print(f"STOCK ENGINE LIVE REPLAY {date}: {len(picks)} picks",
          flush=True)
    tot = 0.0
    for c in picks:
        p = c["rep"]
        tot += p["net"]
        print("STOCK_ENGINE_LIVE_PICK " + json.dumps(
            {"date": date, "stock": p["stock"], "comp": p["comp"],
             "dir": p["dir"], "entry_time": p["entry_time"],
             "entry": p["entry"], "lock_time": c["lock_time"],
             "exit_time": p["exit_time"], "exit": p["exit"],
             "exit_reason": p["exit_reason"], "net": p["net"],
             "fc_net": SIM.lens_net(p)[1], "norm_pct": c["owner_pct"],
             "confluence": c["confluence"]}), flush=True)
    print(f"REPLAY {date} total net={tot:+.2f} (provisional per 100 "
          f"shares, paper)", flush=True)
    return 0


def main():
    args = sys.argv[1:]
    if "--summary" in args:
        return run_summary()
    if "--replay" in args:
        return run_replay(args[args.index("--replay") + 1])
    return run_tick(dry="--dry-run" in args)


if __name__ == "__main__":
    sys.exit(main())
