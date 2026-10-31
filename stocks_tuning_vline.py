#!/usr/bin/env python3
"""LINE 2 (V-line) tuning engine. Spec: stocks_tuning_vline_frozen.md
(frozen BEFORE scoring). Equity cash intraday, LONG/SHORT, paper only.
Per 100 shares provisional, Rs40/trade flat unless a mode states else.

Modes:
  gate_v3  reproduce published V3 exactly via the generalised ladder
  u1|u2|u3|u4  ladder families (spec U1-U4)
  gate_u5  reproduce Round 6 unfiltered V5 x T125 chain totals
  u5       probe-chain / skip-probe (spec U5)
  u6       cost sensitivity on the best cell recorded in the state file
State (best direction, best cell) is kept in stocks_tuning_vline_state.json.
"""
import csv, json, math, os, statistics, sys
from collections import defaultdict

OUT = "/home/hatch/workspace/trading"
VOLBASE = f"{OUT}/data/progressive_vol"
SYMBOLS = ["GODREJCP","GLENMARK","ITC","RECLTD","TVSMOTOR","UNITDSPR","OBEROIRLTY",
           "NTPC","INDUSTOWER","KALYANKJIL","HDFCBANK","NHPC","PFC","IRCTC","WIPRO",
           "NATIONALUM","VEDL","HINDCOPPER","HINDZINC","HINDALCO","TATASTEEL",
           "ASTRAL","BDL","OIL","HINDUNILVR"]
QTY, COST = 100, 40.0
LO, HI = "2026-01-01", "2026-10-28"
SQ, LAST_ENTRY, TRIG_FROM = "15:10", "15:05", "09:45"
STATE_F = f"{OUT}/stocks_tuning_vline_state.json"
RESULTS_F = f"{OUT}/stocks_tuning_vline_results.json"

# ---- hunt1 provides DAYS / WINDOWS / exits (same loader the vol engine used)
MODE = sys.argv[1] if len(sys.argv) > 1 else ""
import importlib.util
spec = importlib.util.spec_from_file_location("hunt1", f"{OUT}/stocks_hunt1.py")
H = importlib.util.module_from_spec(spec)
sys.argv = ["hunt1"]
spec.loader.exec_module(H)
DAYS = H.DAYS; WINDOWS = H.WINDOWS

def load_state():
    return json.load(open(STATE_F)) if os.path.exists(STATE_F) else {}
def save_state(s):
    json.dump(s, open(STATE_F, "w"), indent=1)
def load_results():
    return json.load(open(RESULTS_F)) if os.path.exists(RESULTS_F) else {}
def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)

# ================= LADDER (generalised V3) =================
def load_vol(sym):
    days = {}
    path = f"{VOLBASE}/{sym}/spot_5m_vol.csv"
    if not os.path.exists(path): return days
    with open(path) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            if not (LO <= d <= HI): continue
            days.setdefault(d, []).append({"time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]),
                "low": float(r["low"]), "close": float(r["close"]),
                "volume": float(r["volume"])})
    for d in days: days[d] = sorted(days[d], key=lambda x: x["time"])
    return days

VOLDATA = {s: load_vol(s) for s in SYMBOLS}

def vr(bars, i):
    if i < 20: return None
    med = statistics.median(b["volume"] for b in bars[i-20:i])
    if med <= 0: return None
    return bars[i]["volume"] / med

def sq_index(bars):
    return next((i for i, b in enumerate(bars) if b["time"] == SQ), len(bars) - 1)

def sim_ladder(bars, step=0.004, vol_mult=1.5, stop_pct=0.010, dirmode=0,
               exit_time=None, cap=6):
    """Generalised V3. dirmode: 0=both, 1=LONG only, -1=SHORT only.
    stop_pct=None -> no intraday stop. exit_time=None -> 15:10 square-off.
    Blocked-direction signals consume the band extreme exactly like a
    volume-gate block in the base engine (frozen spec)."""
    sq_i = sq_index(bars)
    if sq_i < 8: return []
    anchor = bars[0]["open"]
    def band(price):
        return math.floor(math.log(price / anchor) / math.log(1 + step))
    seed = [b for b in bars if b["time"] < TRIG_FROM] or bars[:6]
    if not seed: return []
    bhi = max(band(b["close"]) for b in seed)
    blo = min(band(b["close"]) for b in seed)
    trades = []
    i = next((k for k, b in enumerate(bars) if b["time"] >= TRIG_FROM), None)
    if i is None: return []
    while i <= sq_i:
        b = bars[i]
        if b["time"] > LAST_ENTRY: break
        if cap is not None and len(trades) >= cap: break
        cb = band(b["close"])
        sign = 0; eband = None
        if cb > bhi: sign, eband = 1, cb
        elif cb < blo: sign, eband = -1, cb
        bhi = max(bhi, cb); blo = min(blo, cb)
        if sign == 0:
            i += 1; continue
        if dirmode != 0 and sign != dirmode:
            i += 1; continue  # blocked direction: extreme consumed, no entry
        r = vr(bars, i)
        if r is None or r < vol_mult:
            i += 1; continue
        entry = b["close"]
        stop = entry * (1 - stop_pct * sign) if stop_pct is not None else None
        xp = xi = reason = None
        for j in range(i + 1, sq_i + 1):
            bj = bars[j]
            if stop is not None:
                if sign > 0 and bj["low"] <= stop:
                    xp, xi, reason = (bj["open"] if bj["open"] < stop else stop), j, "stop"; break
                if sign < 0 and bj["high"] >= stop:
                    xp, xi, reason = (bj["open"] if bj["open"] > stop else stop), j, "stop"; break
            if exit_time is not None and bj["time"] >= exit_time:
                xp, xi, reason = bj["close"], j, "time_exit"; break
            if j == sq_i: xp, xi, reason = bj["close"], j, "squareoff"
        if xp is None: xp, xi, reason = bars[sq_i]["close"], sq_i, "squareoff"
        net = (xp - entry) * sign * QTY - COST
        trades.append({"entry_time": b["time"], "dir": "LONG" if sign > 0 else "SHORT",
            "entry": round(entry, 2), "exit": round(xp, 2), "exit_time": bars[xi]["time"],
            "exit_reason": reason, "net": round(net, 2), "round": len(trades) + 1,
            "kind": "ladder_vol", "level": eband, "vr": round(r, 2)})
        i = xi + 1
        upto = bars[:i]
        if upto:
            bhi = max(bhi, max(band(x["close"]) for x in upto))
            blo = min(blo, min(band(x["close"]) for x in upto))
    return trades

def run_ladder(fn):
    all_trades = []
    for sym in SYMBOLS:
        for day in DAYS:
            bars = VOLDATA[sym].get(day)
            if not bars or len(bars) < 40: continue
            for t in fn(bars):
                t.update({"symbol": sym, "date": day,
                          "event": "event" if day in WINDOWS[sym] else "no_event"})
                all_trades.append(t)
    return all_trades

# ================= metrics =================
def metrics(ts):
    if not ts: return {"trades": 0, "net": 0.0, "win_pct": 0.0, "exp": 0.0, "gross_exp": 0.0,
                       "gross": 0.0}
    net = sum(t["net"] for t in ts); wins = sum(1 for t in ts if t["net"] > 0)
    return {"trades": len(ts), "net": round(net, 2), "win_pct": round(100 * wins / len(ts), 1),
            "exp": round(net / len(ts), 2), "gross_exp": round(net / len(ts) + COST, 2),
            "gross": round(net + COST * len(ts), 2)}

def split(ts, a, b): return [t for t in ts if a <= t["date"] <= b]

def summarize(ts):
    s = {"all": metrics(ts),
         "jan_may": metrics(split(ts, "2026-01-01", "2026-05-31")),
         "jun_oct": metrics(split(ts, "2026-06-01", "2026-10-28")),
         "october": metrics(split(ts, "2026-10-01", "2026-10-28")),
         "per_day": round(len(ts) / len(DAYS), 2),
         "long": metrics([t for t in ts if t["dir"] == "LONG"]),
         "short": metrics([t for t in ts if t["dir"] == "SHORT"]),
         "long_jm": metrics([t for t in ts if t["dir"] == "LONG" and t["date"] <= "2026-05-31"]),
         "long_jo": metrics([t for t in ts if t["dir"] == "LONG" and t["date"] >= "2026-06-01"]),
         "short_jm": metrics([t for t in ts if t["dir"] == "SHORT" and t["date"] <= "2026-05-31"]),
         "short_jo": metrics([t for t in ts if t["dir"] == "SHORT" and t["date"] >= "2026-06-01"])}
    by_stock = defaultdict(list)
    for t in ts: by_stock[t["symbol"]].append(t)
    sm = sorted(((metrics(v)["net"], k, metrics(v)["trades"]) for k, v in by_stock.items()),
                reverse=True)
    tot = s["all"]["net"]
    s["breadth"] = {"stocks_positive": sum(1 for x in sm if x[0] > 0), "stocks_total": 25,
                    "top3_share_pct": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None,
                    "best5": sm[:5], "worst5": sm[-5:],
                    "per_stock": {k: metrics(v)["net"] for k, v in by_stock.items()}}
    s["pass"] = (s["jan_may"]["net"] > 0 and s["jun_oct"]["net"] > 0
                 and s["breadth"]["stocks_positive"] >= 10)
    return s

def save_trades(fid, ts):
    if not ts: return
    cols = ["family", "symbol", "date", "round", "kind", "dir", "entry_time", "entry",
            "level", "vr", "exit_time", "exit", "exit_reason", "net", "event"]
    with open(f"{OUT}/vline_{fid}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(ts, key=lambda x: (x["date"], x["symbol"], x["entry_time"])):
            w.writerow({c: t.get(c, "") for c in cols})

def score_ladder(fid, fn, results):
    ts = run_ladder(fn)
    for t in ts: t["family"] = fid
    save_trades(fid, ts)
    s = summarize(ts)
    results[fid] = s
    save_results(results)
    print(f"{fid}: n={s['all']['trades']} net={s['all']['net']} exp={s['all']['exp']} "
          f"gExp={s['all']['gross_exp']} win={s['all']['win_pct']} | JM {s['jan_may']['net']} "
          f"(n={s['jan_may']['trades']}, gExp={s['jan_may']['gross_exp']}) | JO {s['jun_oct']['net']} "
          f"(n={s['jun_oct']['trades']}, gExp={s['jun_oct']['gross_exp']}) | Oct {s['october']['net']} "
          f"| breadth {s['breadth']['stocks_positive']}/25 | PASS={s['pass']}", flush=True)
    return s

# ================= modes: ladder =================
def mode_gate_v3(results):
    ts = run_ladder(lambda bars: sim_ladder(bars))
    s = summarize(ts)
    exp = {"trades": 3275, "jan_may": 45413.60, "jun_oct": -61697.60, "all": -16284.00,
           "breadth": 10}
    ok = (s["all"]["trades"] == exp["trades"] and abs(s["jan_may"]["net"] - exp["jan_may"]) < 0.01
          and abs(s["jun_oct"]["net"] - exp["jun_oct"]) < 0.01
          and abs(s["all"]["net"] - exp["all"]) < 0.01
          and s["breadth"]["stocks_positive"] == exp["breadth"])
    print(f"GATE_V3: trades {s['all']['trades']} vs {exp['trades']}, JM {s['jan_may']['net']} vs "
          f"{exp['jan_may']}, JO {s['jun_oct']['net']} vs {exp['jun_oct']}, all {s['all']['net']} "
          f"vs {exp['all']}, breadth {s['breadth']['stocks_positive']} vs {exp['breadth']} "
          f"-> {'PASS' if ok else 'FAIL'}", flush=True)
    results["GATE_V3"] = {"pass": ok, "got": s["all"], "jan_may": s["jan_may"],
                          "jun_oct": s["jun_oct"]}
    save_results(results)
    return ok

def mode_u1(results):
    score_ladder("U1-BOTH", lambda bars: sim_ladder(bars), results)
    sl = score_ladder("U1-LONG", lambda bars: sim_ladder(bars, dirmode=1), results)
    ss = score_ladder("U1-SHORT", lambda bars: sim_ladder(bars, dirmode=-1), results)
    best = 1 if sl["all"]["net"] >= ss["all"]["net"] else -1
    st = load_state(); st["best_direction"] = best
    st["best_direction_name"] = "LONG" if best == 1 else "SHORT"
    save_state(st)
    print(f"U1 best direction (frozen rule): {st['best_direction_name']} "
          f"(LONG net {sl['all']['net']} vs SHORT net {ss['all']['net']})", flush=True)

def mode_u2(results):
    for stop, tag in ((0.0075, "S075"), (0.0125, "S125"), (None, "SNONE")):
        for dm, dn in ((0, "BOTH"), (1, "LONG"), (-1, "SHORT")):
            score_ladder(f"U2-{tag}-{dn}",
                         lambda bars, sp=stop, d=dm: sim_ladder(bars, stop_pct=sp, dirmode=d),
                         results)

def mode_u3(results):
    st = load_state(); best = st["best_direction"]; bn = st["best_direction_name"]
    for et in ("13:00", "14:30"):
        tag = et.replace(":", "")
        score_ladder(f"U3-{tag}-BOTH",
                     lambda bars, e=et: sim_ladder(bars, exit_time=e), results)
        score_ladder(f"U3-{tag}-{bn}",
                     lambda bars, e=et, d=best: sim_ladder(bars, exit_time=e, dirmode=d),
                     results)

def mode_u4(results):
    st = load_state(); best = st["best_direction"]; bn = st["best_direction_name"]
    for step in (0.003, 0.005, 0.006):
        tag = f"S{int(step * 1000):03d}"
        score_ladder(f"U4-{tag}-{bn}",
                     lambda bars, s=step, d=best: sim_ladder(bars, step=s, dirmode=d),
                     results)

# ================= V5 re-entry stream (U5) =================
def _load_reentry():
    src = open(f"{OUT}/stocks_equity_reentry.py").read()
    head = src.split("# ---------- score both modes")[0]
    NS = {}
    exec(compile(head, "stocks_equity_reentry_head", "exec"), NS)
    return NS

def replay_plain(candles, entry_idx, sign, entry, tgt_pct, stp_pct):
    target = entry * (1 + sign * tgt_pct / 100); stop = entry * (1 - sign * stp_pct / 100)
    for j in range(entry_idx, len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop: er, ep = "stop", stop
            elif c["high"] >= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        else:
            if c["high"] >= stop: er, ep = "stop", stop
            elif c["low"] <= target: er, ep = "target", target
            elif c["time"] == "15:10": er, ep = "square_off", c["close"]
            else: continue
        return er, ep, c["time"], j, 100.0 * sign * (ep - entry)
    c = candles[-1]
    return "square_off", c["close"], c["time"], len(candles) - 1, 100.0 * sign * (c["close"] - entry)

def build_chain(NS, sym, day, mode, cap=2):
    """mode: 'gate' (all T125, uncapped), 'U5a', 'U5b'.
    Returns (trades, premoved_flag)."""
    ctx = NS["DAYCTX"].get((sym, day))
    if ctx is None: return [], False
    candles = ctx["candles"]
    premoved = False
    if mode == "U5b":
        day_open = candles[0]["open"]
        pre = [c for c in candles if c["time"] < "10:00"]
        if pre and day_open:
            premoved = abs(pre[-1]["close"] / day_open - 1) >= 0.01
    trades, start, sig_seen = [], 0, 0
    while True:
        if cap is not None and len(trades) >= cap: break
        chosen = NS["pool_pick"](ctx, NS["v4_head"](ctx, start), NS["skor_head"](ctx, start))
        if chosen is None: break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles): break
        sig_seen += 1
        if mode == "U5b" and premoved and sig_seen == 1:
            start = idx + 1  # discard the first signal entirely (no probe, no cost)
            continue
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if mode == "gate":
            tp, sp, leg = 1.25, 0.5, "gate"
        elif mode == "U5a":
            tp, sp, leg = (0.5, 0.35, "probe") if not trades else (1.25, 0.5, "round2")
        else:  # U5b
            if premoved or trades:
                tp, sp, leg = 1.25, 0.5, ("direct" if not trades else "round2")
            else:
                tp, sp, leg = 0.5, 0.35, "probe"
        er, ep, et, exit_idx, gross = replay_plain(candles, entry_idx, sign, entry, tp, sp)
        trades.append({"date": day, "symbol": sym, "dir": direction, "setup": setup,
                       "leg": leg, "round": len(trades) + 1,
                       "entry_time": candles[entry_idx]["time"], "entry": round(entry, 2),
                       "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2), "net": round(gross - COST, 2),
                       "event": ctx["event_status"], "premoved": premoved})
        start = exit_idx
    return trades, premoved

def mode_gate_u5(results):
    NS = _load_reentry()
    rows = []
    for sym in NS["SYMBOLS"]:
        for day in NS["ALL_DAYS"]:
            ts, _ = build_chain(NS, sym, day, "gate", cap=None)
            rows.extend(ts)
    net = round(sum(r["net"] for r in rows), 2)
    ok = len(rows) == 6625 and abs(net - (-184394.90)) < 0.01
    print(f"GATE_U5: trades {len(rows)} vs 6625, net {net} vs -184394.90 "
          f"-> {'PASS' if ok else 'FAIL'}", flush=True)
    results["GATE_U5"] = {"pass": ok, "trades": len(rows), "net": net}
    save_results(results)
    return ok

def chain_stats(chains):
    """chains: list of trade-lists (one per initiated stock-day chain)."""
    flat = [t for c in chains for t in c]
    def csum(cs): return round(sum(sum(t["net"] for t in c) for c in cs), 2)
    def part(a, b): return [c for c in chains if c and a <= c[0]["date"] <= b]
    def block(cs):
        n = len(cs); tot = csum(cs)
        wins = sum(1 for c in cs if sum(t["net"] for t in c) > 0)
        return {"chains": n, "chain_net": tot,
                "chain_win_pct": round(100 * wins / n, 1) if n else 0.0,
                "exp_per_chain": round(tot / n, 2) if n else 0.0,
                "trades": sum(len(c) for c in cs)}
    s = {"all": block(chains), "jan_may": block(part("2026-01-01", "2026-05-31")),
         "jun_oct": block(part("2026-06-01", "2026-10-28")),
         "october": block(part("2026-10-01", "2026-10-28")),
         "trade_level": metrics(flat),
         "with_round2": block([c for c in chains if len(c) >= 2]),
         "probe_only": block([c for c in chains if len(c) == 1])}
    by_stock = defaultdict(float); by_stock_n = defaultdict(int)
    for c in chains:
        if c:
            by_stock[c[0]["symbol"]] += sum(t["net"] for t in c); by_stock_n[c[0]["symbol"]] += 1
    sm = sorted(((round(v, 2), k, by_stock_n[k]) for k, v in by_stock.items()), reverse=True)
    tot = s["all"]["chain_net"]
    s["breadth"] = {"stocks_positive": sum(1 for x in sm if x[0] > 0), "stocks_total": 25,
                    "top3_share_pct": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None,
                    "best5": sm[:5], "worst5": sm[-5:],
                    "per_stock": {k: round(v, 2) for k, v in by_stock.items()}}
    s["pass"] = (s["jan_may"]["chain_net"] > 0 and s["jun_oct"]["chain_net"] > 0
                 and s["breadth"]["stocks_positive"] >= 10)
    return s

def mode_u5(results):
    NS = _load_reentry()
    for mode, fid in (("U5a", "U5a-PROBE"), ("U5b", "U5b-SKIP")):
        chains, premoved_chains = [], []
        for sym in NS["SYMBOLS"]:
            for day in NS["ALL_DAYS"]:
                ts, pm = build_chain(NS, sym, day, mode, cap=2)
                if ts:
                    chains.append(ts)
                    if pm: premoved_chains.append(ts)
        s = chain_stats(chains)
        if mode == "U5b":
            s["premoved_subset"] = chain_stats(premoved_chains)["all"]
            s["premoved_chains"] = len(premoved_chains)
        results[fid] = s
        save_results(results)
        flat = [t for c in chains for t in c]
        with open(f"{OUT}/vline_{fid}_trades.csv", "w", newline="") as f:
            cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time", "entry",
                    "exit_time", "exit", "exit_reason", "gross", "net", "event", "premoved"]
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for t in sorted(flat, key=lambda x: (x["date"], x["symbol"], x["round"])):
                w.writerow({c: t.get(c, "") for c in cols})
        a = s["all"]
        print(f"{fid}: chains={a['chains']} trades={a['trades']} chainNet={a['chain_net']} "
              f"exp/chain={a['exp_per_chain']} chainWin={a['chain_win_pct']} | "
              f"JM {s['jan_may']['chain_net']} (chains={s['jan_may']['chains']}) | "
              f"JO {s['jun_oct']['chain_net']} (chains={s['jun_oct']['chains']}) | "
              f"Oct {s['october']['chain_net']} | breadth {s['breadth']['stocks_positive']}/25 "
              f"| withR2 {s['with_round2']['chain_net']} (n={s['with_round2']['chains']}) "
              f"probeOnly {s['probe_only']['chain_net']} (n={s['probe_only']['chains']}) "
              f"| PASS={s['pass']}", flush=True)

# ================= U6 =================
def mode_u6(results):
    # candidate cells: ladder cells have metrics() shape; U5 cells have chain shape.
    cands = {}
    for fid, s in results.items():
        if fid.startswith("GATE"): continue
        if "jan_may" in s and "chain_net" in s.get("all", {}):
            jm, jo = s["jan_may"]["chain_net"], s["jun_oct"]["chain_net"]
            tot, n = s["all"]["chain_net"], s["all"]["trades"]
            gross = tot + COST * n
            cands[fid] = {"min_half": min(jm, jo), "jm": jm, "jo": jo, "total": tot,
                          "trades": n, "gross": gross,
                          "gross_jm": s["jan_may"]["chain_net"] + COST * s["jan_may"]["trades"],
                          "gross_jo": s["jun_oct"]["chain_net"] + COST * s["jun_oct"]["trades"],
                          "n_jm": s["jan_may"]["trades"], "n_jo": s["jun_oct"]["trades"],
                          "pass": s.get("pass", False)}
        elif "jan_may" in s and "net" in s.get("all", {}):
            jm, jo = s["jan_may"]["net"], s["jun_oct"]["net"]
            tot, n = s["all"]["net"], s["all"]["trades"]
            cands[fid] = {"min_half": min(jm, jo), "jm": jm, "jo": jo, "total": tot,
                          "trades": n, "gross": s["all"]["gross"],
                          "gross_jm": s["jan_may"]["gross"], "gross_jo": s["jun_oct"]["gross"],
                          "n_jm": s["jan_may"]["trades"], "n_jo": s["jun_oct"]["trades"],
                          "pass": s.get("pass", False)}
    if not cands:
        print("U6: no candidate cells recorded.", flush=True); return
    passers = {k: v for k, v in cands.items() if v["pass"]}
    if passers:
        best = max(passers, key=lambda k: passers[k]["total"])
    else:
        best = max(cands, key=lambda k: cands[k]["min_half"])
    v = cands[best]
    def at(cost):
        return {"total": round(v["gross"] - cost * v["trades"], 2),
                "jan_may": round(v["gross_jm"] - cost * v["n_jm"], 2),
                "jun_oct": round(v["gross_jo"] - cost * v["n_jo"], 2)}
    out = {"best_cell": best, "selection": "passer w/ highest total" if passers
           else "highest min(half nets) at Rs40",
           "trades": v["trades"], "at_40": at(40.0), "at_25": at(25.0), "at_60": at(60.0),
           "breakeven_cost": round(v["gross"] / v["trades"], 2) if v["trades"] else None,
           "breakeven_jm": round(v["gross_jm"] / v["n_jm"], 2) if v["n_jm"] else None,
           "breakeven_jo": round(v["gross_jo"] / v["n_jo"], 2) if v["n_jo"] else None}
    results["U6"] = out
    save_results(results)
    st = load_state(); st["best_cell"] = best; save_state(st)
    print(f"U6 best cell: {best} ({out['selection']}) trades={v['trades']} "
          f"at25={out['at_25']} at60={out['at_60']} breakeven={out['breakeven_cost']} "
          f"(JM {out['breakeven_jm']} / JO {out['breakeven_jo']})", flush=True)

if __name__ == "__main__":
    mode = MODE
    results = load_results()
    if mode == "gate_v3": mode_gate_v3(results)
    elif mode == "u1": mode_u1(results)
    elif mode == "u2": mode_u2(results)
    elif mode == "u3": mode_u3(results)
    elif mode == "u4": mode_u4(results)
    elif mode == "gate_u5": mode_gate_u5(results)
    elif mode == "u5": mode_u5(results)
    elif mode == "u6": mode_u6(results)
    else: print("unknown mode", mode)
