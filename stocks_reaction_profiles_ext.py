#!/usr/bin/env python3
"""Per-stock RESULTS REACTION PROFILES + P1/P2 tradability test.
Spec frozen FIRST in stock_reaction_profiles.md (2026-10-31), then scored.
EQUITY CASH intraday only. LONG/SHORT. Paper only, real Rs0.
Per 100 shares provisional, Rs40/trade flat."""
import csv, json
from datetime import date, timedelta
from statistics import median

BASE = "/home/hatch/workspace/trading/data/progressive_ext"
VBASE = "/home/hatch/workspace/trading/data/progressive_vol_ext"
OUT = "/home/hatch/workspace/trading"
SYMBOLS = ["RELIANCE","TCS","ICICIBANK","INFY","BHARTIARTL","SBIN","LT",
           "AXISBANK","KOTAKBANK","BAJFINANCE","HCLTECH","MARUTI","SUNPHARMA",
           "TITAN","M&M","ULTRACEMCO","NESTLEIND","POWERGRID","ONGC","COALINDIA",
           "JSWSTEEL","GRASIM","CIPLA","DRREDDY","EICHERMOT"]
QTY, COST = 100, 40.0
ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"
H1_HI = "2026-05-31"

def load_stock(sym):
    spot, daily = {}, []
    with open(f"{BASE}/{sym}/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            spot.setdefault(d, []).append({"timestamp": r["timestamp"][:19], "time": r["timestamp"][11:16],
                "open": float(r["open"]), "high": float(r["high"]), "low": float(r["low"]), "close": float(r["close"])})
    with open(f"{BASE}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            daily.append({"date": r["date"][:10], "open": float(r["open"]), "high": float(r["high"]),
                          "low": float(r["low"]), "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    for d in spot: spot[d].sort(key=lambda x: x["timestamp"])
    vol = {}
    with open(f"{VBASE}/{sym}/spot_5m_vol.csv") as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            if d <= ALL_HI:
                vol[d] = vol.get(d, 0.0) + float(r["volume"])
    return spot, daily, vol

stocks = {s: load_stock(s) for s in SYMBOLS}

def baseline_vol(vol, days, upto_idx, maxn=20):
    """mean daily volume over up to maxn trading days with idx < upto_idx (days = sorted vol dates).
    Returns (mean, n) or (None, n) if n < 5."""
    idxs = [i for i in range(max(0, upto_idx - maxn), upto_idx)]
    vals = [vol[days[i]] for i in idxs]
    if len(vals) < 5: return None, len(vals)
    return sum(vals) / len(vals), len(vals)

# ---------- events ----------
events = []  # per stock, chronological
with open(f"{OUT}/stock_event_calendar_ext_jan_oct_2026.csv") as f:
    for r in csv.DictReader(f):
        if r["event_type"] != "results" or r["stock"] not in SYMBOLS: continue
        ev = date.fromisoformat(r["event_date"][:10])
        react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
        eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
        ds = eff.isoformat()
        if ALL_LO <= ds <= ALL_HI:
            events.append({"symbol": r["stock"], "announce": r["event_date"][:10],
                           "quarter": r["detail"], "R": ds})
events.sort(key=lambda e: (e["symbol"], e["R"]))
print(f"usable results events: {len(events)}")

# ---------- profile rows ----------
rows = []
for e in events:
    sym, R = e["symbol"], e["R"]
    spot, daily, vol = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    vdays = sorted(vol.keys())
    vidx = {d: i for i, d in enumerate(vdays)}
    row = dict(e)
    if R not in didx:
        row["status"] = "R not a trading day in price data"; rows.append(row); continue
    ri = didx[R]
    closes = [d["close"] for d in daily]
    def ret(i_from, i_to):  # close-to-close cum return %
        return (closes[i_to] / closes[i_from] - 1) * 100
    def win_stats(i_lo, i_hi, base_before_date):
        """cum return, pace, up-days for trading days daily[i_lo..i_hi]; base_before_date = first day of window."""
        seg = daily[i_lo:i_hi + 1]
        cr = ret(i_lo - 1, i_hi)
        upd = sum(1 for k in range(i_lo, i_hi + 1) if closes[k] > closes[k - 1])
        nd = i_hi - i_lo + 1
        pace, bn = (None, 0)
        if base_before_date in vidx:
            b, bn = baseline_vol(vol, vdays, vidx[base_before_date])
            if b: pace = sum(vol.get(daily[k]["date"], 0.0) for k in range(i_lo, i_hi + 1)) / (nd * b)
        return cr, pace, upd, bn
    # PRE-A: R-7..R-3 (indices ri-7..ri-3); PRE-B: ri-2..ri-1; PRE-ALL: ri-7..ri-1
    if ri - 8 >= 0:
        cr, pace, upd, bn = win_stats(ri - 7, ri - 3, daily[ri - 7]["date"])
        row.update(preA_ret=round(cr, 2), preA_pace=(round(pace, 2) if pace is not None else None),
                   preA_up=upd, preA_base_days=bn)
        cr, pace, upd, bn = win_stats(ri - 2, ri - 1, daily[ri - 2]["date"])
        row.update(preB_ret=round(cr, 2), preB_pace=(round(pace, 2) if pace is not None else None),
                   preB_up=upd, preB_base_days=bn)
        cr, pace, upd, bn = win_stats(ri - 7, ri - 1, daily[ri - 7]["date"])
        row.update(preAll_ret=round(cr, 2), preAll_pace=(round(pace, 2) if pace is not None else None),
                   preAll_up=upd, preAll_base_days=bn)
    else:
        row.update(preA_ret=None, preA_pace=None, preA_up=None, preAll_ret=None, preAll_pace=None)
    # REACTION
    prev_close = closes[ri - 1]
    dR = daily[ri]
    bars = spot.get(R, [])
    by_time = {c["time"]: c for c in bars}
    b0925 = by_time.get("09:25")
    row.update(gap_pct=round((dR["open"] / prev_close - 1) * 100, 2),
               move0930_pct=(round((b0925["close"] / prev_close - 1) * 100, 2) if b0925 else None),
               reaction_ret_pct=round((dR["close"] / prev_close - 1) * 100, 2))
    vm, bn = (None, 0)
    if R in vidx:
        b, bn = baseline_vol(vol, vdays, vidx[R])
        if b: vm = vol[R] / b
    row.update(vol_mult=(round(vm, 2) if vm is not None else None), reaction_base_days=bn)
    # POST R+1..R+5
    if ri + 5 < len(daily):
        post = (closes[ri + 5] / closes[ri] - 1) * 100
        rr = row["reaction_ret_pct"]
        if abs(post) < 0.5: cls = "FLAT"
        elif (post > 0) == (rr > 0): cls = "CONTINUED"
        else: cls = "FADED"
        row.update(post_ret_pct=round(post, 2), post_class=cls,
                   next_day=daily[ri + 1]["date"])
    else:
        row.update(post_ret_pct=None, post_class=None,
                   next_day=(daily[ri + 1]["date"] if ri + 1 < len(daily) else None))
    row["status"] = "ok"
    rows.append(row)

ok = [r for r in rows if r["status"] == "ok"]
print(f"profiled events: {len(ok)} / {len(rows)}")

# ---------- exit engine (round-5 N4, verbatim logic) ----------
def replay(candles, ei, entry, direction, tgt_pct, stp_pct):
    sign = 1 if direction == "LONG" else -1
    target = entry * (1 + sign * tgt_pct / 100)
    stop = entry * (1 - sign * stp_pct / 100)
    last = None
    for j in range(ei + 1, len(candles)):
        c = candles[j]
        if c["time"] > "15:10": break
        last = c
        if sign == 1:
            if c["low"] <= stop: return "stop", stop, c["time"]
            if c["high"] >= target: return "target", target, c["time"]
        else:
            if c["high"] >= stop: return "stop", stop, c["time"]
            if c["low"] <= target: return "target", target, c["time"]
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"]
    if last is not None:
        return "square_off", last["close"], last["time"]
    return None

def score_one(sym, day, ei, entry, entry_time, direction, tgt_pct, stp_pct, note):
    spot, _, _ = stocks[sym]
    r = replay(spot[day], ei, entry, direction, tgt_pct, stp_pct)
    if r is None: return None
    er, ep, et = r
    sign = 1 if direction == "LONG" else -1
    return {"symbol": sym, "date": day, "direction": direction, "entry_time": entry_time,
            "entry": round(entry, 2), "exit_reason": er, "exit_price": round(ep, 2), "exit_time": et,
            "net_rs": round(sign * (ep - entry) * QTY - COST, 2), "note": note}

EXITS = {"T125": (1.25, 0.5), "T10": (1.0, 0.5)}

# ---------- P1 ----------
def signature(r):
    if r.get("preAll_ret") is None or r.get("preAll_pace") is None: return None
    if r["preAll_ret"] >= 1.5 and r["preAll_pace"] >= 1.1: return "ACCUM"
    if r["preAll_ret"] <= -1.5 and r["preAll_pace"] >= 1.1: return "DISTRIB"
    return None

p1 = {"gated": {ex: [] for ex in EXITS}, "ungated": {ex: [] for ex in EXITS}, "dropped": {ex: [] for ex in EXITS}}
p1_sig_count = {"ACCUM": 0, "DISTRIB": 0, "none": 0}
for r in ok:
    sym, R = r["symbol"], r["R"]
    spot, daily, _ = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    prev_close = daily[didx[R] - 1]["close"]
    bars = spot.get(R, [])
    by_time = {c["time"]: c for c in bars}
    idx_of = {c["timestamp"]: i for i, c in enumerate(bars)}
    b0925, b0930 = by_time.get("09:25"), by_time.get("09:30")
    sig = signature(r)
    p1_sig_count[sig if sig else "none"] += 1
    if b0925 is None or b0930 is None: continue
    move = (b0925["close"] / prev_close - 1) * 100
    if abs(move) < 1.0: continue
    direction = "LONG" if move > 0 else "SHORT"
    ei = idx_of[b0930["timestamp"]]
    keep = (sig == "ACCUM" and direction == "LONG") or (sig == "DISTRIB" and direction == "SHORT")
    for ex, (tg, st) in EXITS.items():
        t = score_one(sym, R, ei, b0930["close"], "09:35", direction, tg, st,
                      f"P1 sig={sig} move0930={move:+.2f}% preAll={r.get('preAll_ret')}% pace={r.get('preAll_pace')}")
        if t is None: continue
        p1["ungated"][ex].append(t)
        p1["gated" if keep else "dropped"][ex].append(t)

# ---------- P2 (leave-one-out) ----------
by_stock = {}
for r in ok: by_stock.setdefault(r["symbol"], []).append(r)
for s in by_stock: by_stock[s].sort(key=lambda r: r["R"])
p2 = {"gated": {ex: [] for ex in EXITS}, "ungated": {ex: [] for ex in EXITS}}
p2_gate_log = []
for sym, evs in by_stock.items():
    spot, daily, _ = stocks[sym]
    didx = {d["date"]: i for i, d in enumerate(daily)}
    for k, r in enumerate(evs):
        earlier = [x for x in evs[:k] if x.get("post_class")]
        n_cont = sum(1 for x in earlier if x["post_class"] == "CONTINUED")
        gate = n_cont >= 2
        p2_gate_log.append({"symbol": sym, "R": r["R"], "earlier_with_post": len(earlier),
                            "earlier_continued": n_cont, "gate_pass": gate})
        if abs(r["reaction_ret_pct"]) < 2.0: continue
        nd = r.get("next_day")
        if not nd or nd > ALL_HI: continue
        bars = spot.get(nd, [])
        if not bars: continue
        direction = "LONG" if r["reaction_ret_pct"] > 0 else "SHORT"
        entry = bars[0]["open"]
        for ex, (tg, st) in EXITS.items():
            t = score_one(sym, nd, 0, entry, "09:15", direction, tg, st,
                          f"P2 reaction {r['R']} {r['reaction_ret_pct']:+.2f}% earlier_cont={n_cont}/{len(earlier)} gate={gate}")
            if t is None: continue
            p2["ungated"][ex].append(t)
            if gate: p2["gated"][ex].append(t)

# ---------- metrics ----------
def metrics(trades):
    if not trades:
        return {"trades": 0, "win_pct": 0.0, "net_rs": 0.0, "gross_expectancy_rs": 0.0, "expectancy_rs": 0.0}
    net = sum(t["net_rs"] for t in trades)
    gross = net + COST * len(trades)
    return {"trades": len(trades), "win_pct": round(100 * sum(1 for t in trades if t["net_rs"] > 0) / len(trades), 1),
            "net_rs": round(net, 2), "gross_expectancy_rs": round(gross / len(trades), 2),
            "expectancy_rs": round(net / len(trades), 2)}

def halves(trades, key="date"):
    h1 = [t for t in trades if t[key] <= H1_HI]; h2 = [t for t in trades if t[key] > H1_HI]
    pst = {}
    for t in trades: pst.setdefault(t["symbol"], 0.0)
    for t in trades: pst[t["symbol"]] = round(pst[t["symbol"]] + t["net_rs"], 2)
    return {"all": metrics(trades), "H1": metrics(h1), "H2": metrics(h2),
            "both_halves_positive": bool(h1 and h2 and metrics(h1)["net_rs"] > 0 and metrics(h2)["net_rs"] > 0),
            "stocks_traded": len(pst), "stocks_net_positive": sum(1 for v in pst.values() if v > 0),
            "per_stock_net": dict(sorted(pst.items(), key=lambda kv: -kv[1]))}

results = {"events_total": len(rows), "events_profiled": len(ok),
           "p1_signatures": p1_sig_count,
           "P1": {g: {ex: halves(p1[g][ex]) for ex in EXITS} for g in p1},
           "P2": {g: {ex: halves(p2[g][ex]) for ex in EXITS} for g in p2},
           "p2_gate_log": p2_gate_log}

# ---------- per-stock profile summary ----------
summary = []
for sym in SYMBOLS:
    evs = [r for r in ok if r["symbol"] == sym]
    s = {"symbol": sym, "events": len(evs)}
    def med(key):
        vals = [r[key] for r in evs if r.get(key) is not None]
        return round(median(vals), 2) if vals else None
    def avg(key):
        vals = [r[key] for r in evs if r.get(key) is not None]
        return round(sum(vals) / len(vals), 2) if vals else None
    s.update(preA_ret_med=med("preA_ret"), preB_ret_med=med("preB_ret"), preAll_ret_med=med("preAll_ret"),
             preAll_pace_med=med("preAll_pace"),
             accum_events=sum(1 for r in evs if signature(r) == "ACCUM"),
             distrib_events=sum(1 for r in evs if signature(r) == "DISTRIB"),
             reaction_ret_med=med("reaction_ret_pct"), reaction_abs_avg=avg("reaction_ret_pct") and
             round(sum(abs(r["reaction_ret_pct"]) for r in evs) / len(evs), 2),
             reaction_pos=sum(1 for r in evs if r["reaction_ret_pct"] > 0),
             gap_med=med("gap_pct"), move0930_med=med("move0930_pct"), vol_mult_med=med("vol_mult"),
             post_with_data=sum(1 for r in evs if r.get("post_class")),
             post_continued=sum(1 for r in evs if r.get("post_class") == "CONTINUED"),
             post_faded=sum(1 for r in evs if r.get("post_class") == "FADED"),
             post_flat=sum(1 for r in evs if r.get("post_class") == "FLAT"))
    summary.append(s)
results["per_stock_summary"] = summary

# ---------- write CSVs ----------
def wcsv(fn, dicts, fields):
    with open(f"{OUT}/{fn}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for d in dicts: w.writerow(d)

ev_fields = ["symbol","announce","quarter","R","preA_ret","preA_pace","preA_up","preB_ret","preB_pace",
             "preB_up","preAll_ret","preAll_pace","preAll_up","gap_pct","move0930_pct","reaction_ret_pct",
             "vol_mult","post_ret_pct","post_class","next_day","status"]
wcsv("universe_ext_reaction_profiles_events.csv", rows, ev_fields)
wcsv("universe_ext_reaction_profiles_summary.csv", summary, list(summary[0].keys()))
tfields = ["symbol","date","direction","entry_time","entry","exit_reason","exit_price","exit_time","net_rs","note"]
for g in ("gated","ungated","dropped"):
    for ex in EXITS:
        if p1[g][ex]: wcsv(f"universe_ext_profiles_P1_{g}_{ex}_trades.csv", p1[g][ex], tfields)
for g in ("gated","ungated"):
    for ex in EXITS:
        if p2[g][ex]: wcsv(f"universe_ext_profiles_P2_{g}_{ex}_trades.csv", p2[g][ex], tfields)

with open(f"{OUT}/universe_ext_reaction_profiles_results.json", "w") as f:
    json.dump(results, f, indent=1)
with open(f"{OUT}/universe_ext_reaction_profiles_rows.json", "w") as f:
    json.dump(rows, f, indent=1)

print("ANCHOR CHECK P1-ungated T125 all net (round-5 BASE = +2924.79):", results["P1"]["ungated"]["T125"]["all"])
print("P1 signatures:", p1_sig_count)
for g in ("gated","ungated","dropped"):
    for ex in EXITS:
        m = results["P1"][g][ex]
        print(f"P1 {g} {ex}: all {m['all']} H1 {m['H1']['net_rs']} H2 {m['H2']['net_rs']} both+ {m['both_halves_positive']} breadth {m['stocks_net_positive']}/{m['stocks_traded']}")
for g in ("gated","ungated"):
    for ex in EXITS:
        m = results["P2"][g][ex]
        print(f"P2 {g} {ex}: all {m['all']} H1 {m['H1']['net_rs']} H2 {m['H2']['net_rs']} both+ {m['both_halves_positive']} breadth {m['stocks_net_positive']}/{m['stocks_traded']}")
