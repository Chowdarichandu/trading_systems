#!/usr/bin/env python3
"""Workstream B — Monday-readiness DRY RUN for 2026-10-30 (Friday).
Simulates BOTH November logging crons end-to-end on real fetched data.
Writes ONLY dry-run files. NEVER touches the real November log CSVs,
NEVER writes to the OHLC/volume caches.
Equity cash, paper only, provisional per 100 shares, Rs40/trade.
"""
import csv, json, os, sys, time, urllib.parse
from datetime import date, timedelta

BASE = "/home/hatch/workspace/trading"
RAW = f"{BASE}/data/dryrun_2026-10-30"
os.makedirs(RAW, exist_ok=True)
sys.path.insert(0, BASE)
from fetch_upstox_via_connector import call, candles_df

DAY = "2026-10-30"; PREV = "2026-10-29"
KEYS = json.load(open(f"{BASE}/data/progressive/keys.json"))
SYMBOLS = [s for s in KEYS if s not in ("NIFTY", "BANKNIFTY")]
log = []
def note(x): log.append(x); print(x)

# ---------------------------------------------------------------- fetch 5m
def fetch_5m(sym, first, last):
    enc = urllib.parse.quote(KEYS[sym], safe="")
    df = candles_df(call(f"/v3/historical-candle/{enc}/minutes/5/{last}/{first}"))
    out = {}
    for _, r in df.iterrows():
        ts = str(r["timestamp"])
        out.setdefault(ts[:10], []).append(
            {"time": ts[11:16], "open": float(r["open"]), "high": float(r["high"]),
             "low": float(r["low"]), "close": float(r["close"]), "volume": float(r["volume"])})
    for d in out: out[d].sort(key=lambda b: b["time"])
    return out

bars = {}
for sym in SYMBOLS:
    bars[sym] = fetch_5m(sym, PREV, DAY)
    # robustness: a short-range response can silently omit the newest day
    # (observed live: HDFCBANK 2026-10-30 = 0 bars in the 2-day response,
    # 75 bars in a 5-trading-day response). Assert and refetch wide.
    if len(bars[sym].get(DAY, [])) != 75 or len(bars[sym].get(PREV, [])) != 75:
        wide = fetch_5m(sym, "2026-10-24", DAY)
        for d, bs in wide.items(): bars[sym][d] = bs
        note(f"FETCH RETRY-WIDE {sym}: short-range response incomplete; "
             f"after wide refetch {PREV}={len(bars[sym].get(PREV, []))} {DAY}={len(bars[sym].get(DAY, []))}")
    with open(f"{RAW}/{sym}_5m.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "time", "open", "high", "low", "close", "volume"])
        for d in sorted(bars[sym]):
            for b in bars[sym][d]: w.writerow([d, b["time"], b["open"], b["high"], b["low"], b["close"], b["volume"]])
    time.sleep(0.25)
note(f"FETCH 5m: {len(SYMBOLS)} stocks, bars on {DAY}: " +
     ", ".join(f"{s}={len(bars[s].get(DAY, []))}" for s in SYMBOLS))
note(f"FETCH 5m: bars on {PREV}: min={min(len(bars[s].get(PREV, [])) for s in SYMBOLS)} "
     f"max={max(len(bars[s].get(PREV, [])) for s in SYMBOLS)}")

def agg_daily(sym, d):
    bs = bars[sym][d]
    return {"date": d, "open": bs[0]["open"], "high": max(b["high"] for b in bs),
            "low": min(b["low"] for b in bs), "close": bs[-1]["close"]}

# validate the aggregation method against the cache for 2026-10-28
vol28 = {}
for sym in SYMBOLS:
    days = {}
    with open(f"{BASE}/data/progressive_vol/{sym}/spot_5m_vol.csv") as f:
        for r in csv.DictReader(f):
            if r["timestamp"][:10] == "2026-10-28":
                days.setdefault("2026-10-28", []).append(
                    {"open": float(r["open"]), "high": float(r["high"]),
                     "low": float(r["low"]), "close": float(r["close"])})
    bs = days["2026-10-28"]
    vol28[sym] = {"open": bs[0]["open"], "high": max(b["high"] for b in bs),
                  "low": min(b["low"] for b in bs), "close": bs[-1]["close"]}
worst = 0.0
import stocks_hunt1 as H
for sym in SYMBOLS:
    dmap = {d["date"]: d for d in H.stocks[sym][1]}
    c = dmap["2026-10-28"]
    for k in ("open", "high", "low", "close"):
        worst = max(worst, abs(vol28[sym][k] - c[k]))
note(f"AGGREGATION CHECK 2026-10-28 (5m-aggregated vs daily cache): max abs diff = {worst}")

# ---------------------------------------------------------------- NIFTY daily
nifty_cache = []
with open(f"{BASE}/data/progressive/NIFTY/spot_daily.csv") as f:
    for r in csv.DictReader(f):
        nifty_cache.append({"date": r["date"][:10], "open": float(r["open"]), "high": float(r["high"]),
                            "low": float(r["low"]), "close": float(r["close"])})
daily_endpoint_status = "not tried"
nifty_fetched = []
try:
    enc = urllib.parse.quote(KEYS["NIFTY"], safe="")
    df = candles_df(call(f"/v3/historical-candle/{enc}/days/1/2026-10-30/2026-08-14"))
    for _, r in df.iterrows():
        ts = str(r["timestamp"])
        nifty_fetched.append({"date": ts[:10], "open": float(r["open"]), "high": float(r["high"]),
                              "low": float(r["low"]), "close": float(r["close"])})
    daily_endpoint_status = f"OK ({len(nifty_fetched)} daily bars 2026-08-14..2026-10-30)"
except Exception as e:
    daily_endpoint_status = f"FAILED: {e}"
note(f"NIFTY DAILY ENDPOINT days/1: {daily_endpoint_status}")
with open(f"{RAW}/NIFTY_daily_fetched.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["date", "open", "high", "low", "close"]); w.writeheader()
    for r in nifty_fetched: w.writerow(r)
cache_map = {d["date"]: d for d in nifty_cache}
overlap = [(r["date"], abs(r["close"] - cache_map[r["date"]]["close"]))
           for r in nifty_fetched if r["date"] in cache_map]
note(f"NIFTY DAILY overlap vs cache: {len(overlap)} shared dates, max close diff = "
     f"{max((d for _, d in overlap), default=None)}")
nifty_all = dict(cache_map)
for r in nifty_fetched: nifty_all[r["date"]] = r
ndates = sorted(nifty_all)
closes = [nifty_all[d]["close"] for d in ndates]
i29 = ndates.index(PREV)
prev_close, dma50 = closes[i29], sum(closes[i29 - 49:i29 + 1]) / 50.0
inv_met = prev_close <= dma50
note(f"INV1 CONDITION for {DAY}: NIFTY close {PREV} = {prev_close} vs 50DMA = {round(dma50, 2)} "
     f"-> {'MET' if inv_met else 'NOT MET'} (prev close {'<=' if inv_met else '>'} 50DMA)")

# ---------------------------------------------------------------- N4-V3 dry run
# candidates: reaction day == 2026-10-30 per November watchlist (verified refresh
# of 2026-10-30) = GODREJCP only (board 2026-10-29, Q2 FY27 results).
def replay(daybars, entry_idx, sign, entry, tgt_pct, stp_pct):
    target = entry * (1 + sign * tgt_pct / 100); stop = entry * (1 - sign * stp_pct / 100)
    for j in range(entry_idx + 1, len(daybars)):
        c = daybars[j]
        if sign == 1:
            if c["low"] <= stop: return stop, c["time"], "stop"
            if c["high"] >= target: return target, c["time"], "target"
        else:
            if c["high"] >= stop: return stop, c["time"], "stop"
            if c["low"] <= target: return target, c["time"], "target"
        if c["time"] == "15:10": return c["close"], c["time"], "squareoff"
    c = daybars[-1]
    return c["close"], c["time"], "squareoff"

n4_rows = []
g = bars["GODREJCP"][DAY]
gmap = {b["time"]: b for b in g}
prev_close_g = agg_daily("GODREJCP", PREV)["close"]
trig = (gmap["09:25"]["close"] / prev_close_g - 1) * 100
note(f"N4 GODREJCP: prev close ({PREV}) = {prev_close_g}, 09:25 close {DAY} = {gmap['09:25']['close']}, "
     f"trigger = {trig:+.3f}% (bars present: 09:25={'09:25' in gmap}, 09:30={'09:30' in gmap})")
if abs(trig) >= 1.0:
    sign = 1 if trig > 0 else -1
    ei = [i for i, b in enumerate(g) if b["time"] == "09:30"][0]
    entry = g[ei]["close"]
    res = {}
    for lbl, tg in (("T125", 1.25), ("T10", 1.0)):
        ep, et, er = replay(g, ei, sign, entry, tg, 0.5)
        res[lbl] = (ep, et, er, round(sign * (ep - entry) * 100 - 40.0, 2))
    ep, et, er, net = res["T125"]
    n4_rows.append({
        "date": DAY, "stock": "GODREJCP", "event_type": "results",
        "event_date": PREV, "reaction_date": DAY, "trigger_pct": round(trig, 3),
        "direction": "LONG" if sign > 0 else "SHORT", "entry_time": "09:35",
        "entry": entry, "stop": round(entry * (1 - sign * 0.005), 2),
        "target": round(entry * (1 + sign * 0.0125), 2), "exit_price": round(ep, 2),
        "exit_time": et, "exit_reason": er, "net_rs_provisional_per100": net,
        "shadow_T10_net_rs_provisional_per100": res["T10"][3],
        "notes": "DRYRUN; Q2 FY27 results board 2026-10-29 (watchlist verified); T10 shadow exit "
                 f"{res['T10'][2]} {res['T10'][1]} @ {round(res['T10'][0], 2)}"})
    note(f"N4 GODREJCP TRADE: {'LONG' if sign > 0 else 'SHORT'} entry {entry} @09:35, "
         f"T125 exit {er} {et} @ {round(ep, 2)} net {net}; T10 shadow net {res['T10'][3]}")
else:
    n4_rows.append({
        "date": DAY, "stock": "GODREJCP", "event_type": "results",
        "event_date": PREV, "reaction_date": DAY, "trigger_pct": round(trig, 3),
        "direction": "", "entry_time": "", "entry": "", "stop": "", "target": "",
        "exit_price": "", "exit_time": "", "exit_reason": "no_trigger",
        "net_rs_provisional_per100": "", "shadow_T10_net_rs_provisional_per100": "",
        "notes": "DRYRUN; Q2 FY27 results board 2026-10-29 (watchlist verified); |trigger| < 1.0%"})
    note("N4 GODREJCP: NO TRIGGER -> no_trigger row")

N4_COLS = ["date", "stock", "event_type", "event_date", "reaction_date", "trigger_pct",
           "direction", "entry_time", "entry", "stop", "target", "exit_price", "exit_time",
           "exit_reason", "net_rs_provisional_per100", "shadow_T10_net_rs_provisional_per100", "notes"]
with open(f"{BASE}/stocks_nov_dryrun_n4_2026-10-30.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=N4_COLS); w.writeheader()
    for r in n4_rows: w.writerow(r)

# ---------------------------------------------------------------- INV1 / P2 dry run
# extended wide-window sets (cache dates + 29/30 Oct) for event_status only
def build_windows_ext(sym):
    _, daily = H.stocks[sym]
    tdays = [d["date"] for d in daily] + [PREV, DAY]
    idx = {d: i for i, d in enumerate(tdays)}
    wide = set()
    with open(f"{BASE}/stock_event_calendar_jan_oct_2026.csv") as f:
        for r in csv.DictReader(f):
            if r["stock"] != sym: continue
            ev = date.fromisoformat(r["event_date"][:10]) if r["event_date"] else None
            react = date.fromisoformat(r["reaction_date"][:10]) if r["reaction_date"] else None
            if ev is None: continue
            eff = react if (react and ev <= react <= ev + timedelta(days=7)) else ev
            if ev.isoformat() not in idx or eff.isoformat() not in idx: continue
            a = max(0, idx[ev.isoformat()] - 7); b = min(len(tdays) - 1, idx[eff.isoformat()] + 7)
            wide.update(tdays[a:b + 1])
    if sym == "GODREJCP": wide.add(DAY)  # its own reaction day, per watchlist (not in Jan-Oct calendar)
    return wide

NS8 = {}
exec(compile(open(f"{BASE}/stocks_equity_round8.py").read(), "round8", "exec"), NS8)
DAYCTX, ADR = NS8["DAYCTX"], NS8["ADR"]
bias_of = NS8["NS"]["bias_of"]
for sym in SYMBOLS:
    daily_ext = list(H.stocks[sym][1]) + [agg_daily(sym, PREV)]
    didx = {d["date"]: i for i, d in enumerate(daily_ext)}
    i = didx[DAY] if DAY in didx else len(daily_ext)
    prior = daily_ext[max(0, i - 10):i]
    ADR[(sym, DAY)] = round(sum((x["high"] - x["low"]) / x["close"] * 100 for x in prior) / len(prior), 3)
    if DAY not in bars[sym]:
        note(f"P2 CTX FAILURE {sym}: no {DAY} bars even after wide refetch — stock skipped, "
             f"run_chain returns [] (a live cron must report this, not skip silently)")
        continue
    raw = bars[sym][DAY]
    candles = [c for c in raw if c["time"] >= "09:30"]
    or_c = [c for c in raw if c["time"] < "09:30"]
    prev = daily_ext[-1]
    bias, _ = bias_of(prev)
    wide = build_windows_ext(sym)
    DAYCTX[(sym, DAY)] = {"raw": raw, "candles": candles,
                          "orh": max(c["high"] for c in or_c), "orl": min(c["low"] for c in or_c),
                          "or_width": max(c["high"] for c in or_c) - min(c["low"] for c in or_c),
                          "day_open": raw[0]["open"], "pdh": prev["high"], "pdc": prev["close"],
                          "pdl": prev["low"], "bias": bias,
                          "event_status": "event_window" if DAY in wide else "no_event"}
note(f"P2 CTX built for {DAY}: ADR>=3% stocks = {sum(1 for s in SYMBOLS if ADR[(s, DAY)] >= 3.0)}/25")

inv_rows = []
for cell, lbl in ((("PLAIN", 1.25, 0.5), "T125"), (("PLAIN", 1.0, 0.5), "T10")):
    rows = []
    for sym in SYMBOLS: rows.extend(NS8["run_chain"](sym, DAY, cell))
    p2 = NS8["pools"](rows)["P2_M5"]
    if lbl == "T125": inv_rows = p2
    note(f"P2 {DAY} @{lbl}: chain trades={len(rows)}, after P2 filters={len(p2)}, "
         f"net={round(sum(r['net'] for r in p2), 2)}")
    if lbl == "T125": p2_125 = {(r["stock"], r["entry_time"], r["round"]): r for r in p2}
    else: p2_10 = {(r["stock"], r["entry_time"], r["round"]): r for r in p2}

INV_COLS = ["date", "stock", "direction", "setup", "chain_round", "entry_time", "entry",
            "stop", "target", "exit_price", "exit_time", "exit_reason",
            "gross_rs_provisional_per100", "net_rs_provisional_per100",
            "shadow_net_T10_rs_provisional_per100", "nifty_prev_close", "nifty_50dma",
            "event_status", "notes"]
out_rows = []
for r in sorted(inv_rows, key=lambda r: (r["entry_time"], r["stock"])):
    sh = p2_10.get((r["stock"], r["entry_time"], r["round"]))
    sign = 1 if r["direction"] == "LONG" else -1
    out_rows.append({
        "date": DAY, "stock": r["stock"], "direction": r["direction"], "setup": r["setup"],
        "chain_round": r["round"], "entry_time": r["entry_time"], "entry": r["entry"],
        "stop": round(r["entry"] * (1 - sign * 0.005), 2),
        "target": round(r["entry"] * (1 + sign * 0.0125), 2),
        "exit_price": r["exit_price"], "exit_time": r["exit_time"], "exit_reason": r["exit_reason"],
        "gross_rs_provisional_per100": r["gross"], "net_rs_provisional_per100": r["net"],
        "shadow_net_T10_rs_provisional_per100": sh["net"] if sh else "",
        "nifty_prev_close": prev_close, "nifty_50dma": round(dma50, 2),
        "event_status": r["event_status"],
        "notes": ("DRYRUN — INV1 condition MET, row would be logged" if inv_met else
                  "DRYRUN — INV1 condition NOT met, row would NOT be logged (counterfactual)")})
with open(f"{BASE}/stocks_nov_dryrun_inv1_2026-10-30.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=INV_COLS); w.writeheader()
    for r in out_rows: w.writerow(r)
note(f"INV1 {DAY}: condition {'MET' if inv_met else 'NOT MET'}; P2 trades generated = {len(out_rows)}; "
     f"rows that would be logged = {len(out_rows) if inv_met else 0}")

json.dump({"log": log, "inv_condition_met": inv_met, "nifty_prev_close": prev_close,
           "nifty_50dma": round(dma50, 2), "daily_endpoint_status": daily_endpoint_status,
           "n4_rows": n4_rows, "inv1_would_log_n": len(out_rows) if inv_met else 0,
           "inv1_generated_n": len(out_rows)},
          open(f"{RAW}/dryrun_summary.json", "w"), indent=1)
note("DRY RUN COMPLETE")
