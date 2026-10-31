#!/usr/bin/env python3
"""FROZEN ENGINE BOOK — JAN-2025 -> OCT-2026 VALIDATION RUN (not tuning).

Runs the six-component book frozen in stocks_engine_candidate_spec.md
VERBATIM. 2025 is out-of-sample; 2026 Jan-Oct is the in-sample control and
must reproduce the plateau (+Rs197,607.74 / 663 trades) before any 2025
number is trusted. Event components (N4-V3, P2F, P2F-R2, R2-LOWBAND) are
NOT RUNNABLE for 2025: no same-rules 2025 event/reaction calendar exists
(the 2026 calendar was per-event web research; its only 2025 rows are 15
Q2-FY26 results rows with placeholder reaction_date 2026-01-01). They are
run for 2026 only, from their frozen dumps, exactly as SAT-36 assembled
the plateau. F4 and INV-LONG are candle/state-driven and are rebuilt from
machinery over both years.

Machinery transcribed verbatim from: stocks_equity_reentry.py (head),
stocks_equity_round8.py (run_chain / replay_plain / adr_map),
stocks_tuning_inv.py + stocks_tuning_universe.py (regime_maps / cond /
p2_filter), stocks_M2_fix.py (build2 / collect2), stocks_tuning_mover.py
(premove / pick), stocks_H1.py (agg_5min / build_extra_ctx / below50 /
nifty extension fetch). Data: workspace progressive cache + Upstox fills
fetched with the existing pipeline (Q4-2024 daily lookback for all 26;
Sep-2025 5m+daily for ASTRAL/BDL/HINDUNILVR/OIL whose cache files lack
that month). Pipeline consistency proven: fetched Sep-2025 NIFTY daily
== cache to the paisa (22 days x 4 fields, 0 mismatches).

Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0, square-off 15:10, RF-1 weekend stand-aside.
"""
import csv, json, os, sys, urllib.parse
from collections import defaultdict
from datetime import date

WS = "/home/hatch/workspace/trading"
SHADOW = "/tmp/val2025/data"
RAW = "/tmp/val2025/raw"
OUTD = "/tmp/val2025/out"
os.makedirs(OUTD, exist_ok=True)
sys.path.insert(0, WS)

SYMBOLS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR",
           "OBEROIRLTY", "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK",
           "NHPC", "PFC", "IRCTC", "WIPRO", "NATIONALUM", "VEDL",
           "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL", "ASTRAL",
           "BDL", "OIL", "HINDUNILVR"]
GAP = ["ASTRAL", "BDL", "HINDUNILVR", "OIL"]
COST = 40.0
LOG = []
def log(*a):
    s = " ".join(str(x) for x in a)
    LOG.append(s)
    print(s, flush=True)

# =====================================================================
# 1. SHADOW DATA (cache untouched; merged copies under /tmp)
# =====================================================================
def build_shadow():
    for sym in SYMBOLS + ["NIFTY"]:
        d = f"{SHADOW}/{sym}"
        os.makedirs(d, exist_ok=True)
        rows = {}
        for r in csv.DictReader(open(f"{RAW}/{sym}_q4_2024_daily.csv")):
            rows[r["date"][:10]] = r
        if sym in GAP:
            for r in csv.DictReader(open(f"{RAW}/{sym}_sep2025_daily.csv")):
                rows[r["date"][:10]] = r
        for r in csv.DictReader(open(f"{WS}/data/progressive/{sym}/spot_daily.csv")):
            rows[r["date"][:10]] = r
        with open(f"{d}/spot_daily.csv", "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "open", "high", "low", "close"])
            for dt in sorted(rows):
                r = rows[dt]
                w.writerow([dt, r["open"], r["high"], r["low"], r["close"]])
        dst = f"{d}/spot_5m.csv"
        if os.path.lexists(dst):
            os.remove(dst)
        if sym in GAP:
            bars = {}
            for r in csv.DictReader(open(f"{WS}/data/progressive/{sym}/spot_5m.csv")):
                bars[r["timestamp"][:19]] = r
            for r in csv.DictReader(open(f"{RAW}/{sym}_sep2025_5m.csv")):
                bars[r["timestamp"][:19]] = r
            with open(dst, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["timestamp", "open", "high", "low", "close"])
                for ts in sorted(bars):
                    r = bars[ts]
                    w.writerow([r["timestamp"], r["open"], r["high"],
                                r["low"], r["close"]])
        else:
            os.symlink(f"{WS}/data/progressive/{sym}/spot_5m.csv", dst)
    log("shadow data built")

build_shadow()

# =====================================================================
# 2. REENTRY HEAD over 2025-01-01..2026-10-28 on shadow data
# =====================================================================
src = open(f"{WS}/stocks_equity_reentry.py").read()
head = src.split("# ---------- score both modes")[0]
assert 'BASE = "/home/hatch/workspace/trading/data/progressive"' in head
assert 'ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"' in head
head = head.replace('BASE = "/home/hatch/workspace/trading/data/progressive"',
                    f'BASE = "{SHADOW}"')
head = head.replace('ALL_LO, ALL_HI = "2026-01-01", "2026-10-28"',
                    'ALL_LO, ALL_HI = "2025-01-01", "2026-10-28"')
NS = {}
exec(compile(head, "reentry_head_2025", "exec"), NS)
DAYCTX = NS["DAYCTX"]
ALL_DAYS = NS["ALL_DAYS"]
log(f"head exec ok: ALL_DAYS {ALL_DAYS[0]}..{ALL_DAYS[-1]} n={len(ALL_DAYS)}; "
    f"DAYCTX entries={len(DAYCTX)}")

# =====================================================================
# 3. OCT 29/30 2026 EXTRA CTX (stocks_H1.py verbatim)
# =====================================================================
BASE = WS
def agg_5min(sym, which, day):
    """Aggregate the Line-7 1-min cache to 5-min bars for one day.
    Returns raw-format bar dicts (09:15..15:25) or None. (O1 verbatim.)"""
    path = f"{BASE}/data/1min_stocks_oct2026/{which}/{sym}.csv"
    if not os.path.exists(path):
        return None
    buckets = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            ts = r["timestamp"][:16]
            if ts[:10] != day:
                continue
            hh, mm = int(ts[11:13]), int(ts[14:16])
            mins = hh * 60 + mm
            b = (mins - (9 * 60 + 15)) // 5
            if b < 0 or b > 74:
                continue
            bt = 9 * 60 + 15 + b * 5
            key = f"{bt // 60:02d}:{bt % 60:02d}"
            o, h, l, c = (float(r["open"]), float(r["high"]),
                          float(r["low"]), float(r["close"]))
            if key in buckets:
                bb = buckets[key]
                bb["high"] = max(bb["high"], h); bb["low"] = min(bb["low"], l)
                bb["close"] = c
            else:
                buckets[key] = {"timestamp": f"{day} {key}:00", "time": key,
                                "open": o, "high": h, "low": l, "close": c}
    if len(buckets) != 75:
        return None
    return [buckets[k] for k in sorted(buckets)]

def build_extra_ctx(ns, which):
    """Validate aggregation on 2026-10-28, then add DAYCTX entries for
    Oct 29/30 built with the head's own construction. (O1 verbatim.)"""
    info = {"agg_check_bars": 0, "agg_mismatch_bars": 0, "added": {}}
    daily_extra = {}
    for sym in ns["SYMBOLS"]:
        cached = ns["DAYCTX"].get((sym, "2026-10-28"))
        agg = agg_5min(sym, which, "2026-10-28")
        if cached and agg:
            cb = {c["time"]: c for c in cached["raw"]}
            for b in agg:
                info["agg_check_bars"] += 1
                c0 = cb.get(b["time"])
                if c0 is None or any(abs(c0[k] - b[k]) > 0.051
                                     for k in ("open", "high", "low", "close")):
                    info["agg_mismatch_bars"] += 1
        spot_daily = {d["date"]: d for d in ns["stocks"][sym][1]}
        for day in ("2026-10-29", "2026-10-30"):
            if (sym, day) in ns["DAYCTX"]:
                continue
            raw = agg_5min(sym, which, day)
            if not raw:
                continue
            daily_extra[(sym, day)] = {
                "date": day, "open": raw[0]["open"],
                "high": max(c["high"] for c in raw),
                "low": min(c["low"] for c in raw),
                "close": raw[-1]["close"]}
            prev_day = "2026-10-28" if day == "2026-10-29" else "2026-10-29"
            prev = spot_daily.get(prev_day) or daily_extra.get((sym, prev_day))
            if prev is None:
                continue
            candles = [c for c in raw if c["time"] >= "09:30"]
            or_c = [c for c in raw if c["time"] < "09:30"]
            if not candles or not or_c:
                continue
            orh = max(c["high"] for c in or_c); orl = min(c["low"] for c in or_c)
            bias, _ = ns["bias_of"](prev)
            ns["DAYCTX"][(sym, day)] = {
                "raw": raw, "candles": candles, "orh": orh, "orl": orl,
                "or_width": orh - orl, "day_open": raw[0]["open"],
                "pdh": prev["high"], "pdc": prev["close"], "pdl": prev["low"],
                "bias": bias,
                "event_status": "no_event" if day not in ns["WINDOWS"][sym]
                                else "event_window"}
            info["added"].setdefault(day, []).append(sym)
    return info

extra_info = build_extra_ctx(NS, "old")
log(f"extra ctx: agg check {extra_info['agg_check_bars']} bars, "
    f"{extra_info['agg_mismatch_bars']} mismatches; added "
    f"{ {k: len(v) for k, v in extra_info['added'].items()} }")

# =====================================================================
# 4. NIFTY REGIME MAP (tuning_inv.regime_maps verbatim; merged daily +
#    H1's Oct 29/30 extension fetch)
# =====================================================================
def load_daily_shadow(sym):
    rows = []
    with open(f"{SHADOW}/{sym}/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            try:
                rows.append({"date": r["date"][:10], "high": float(r["high"]),
                             "low": float(r["low"]), "close": float(r["close"])})
            except Exception:
                pass
    rows.sort(key=lambda x: x["date"])
    return rows

def regime_maps_from(daily):
    closes = [d["close"] for d in daily]
    out = {}
    for i, d in enumerate(daily):
        if i == 0:
            continue
        prev_close = closes[i - 1]
        def ma(n):
            if i < n:
                return None
            return sum(closes[i - n:i]) / n
        out[d["date"]] = {"prev_close": prev_close, "ma20": ma(20), "ma50": ma(50)}
    return out

nifty_daily = load_daily_shadow("NIFTY")
# H1.nifty_regime extension, verbatim logic: fetch days/1 for the last
# week of Oct 2026, validate overlap, append Oct 29/30 closes.
try:
    from fetch_upstox_via_connector import call, candles_df
    keys = json.load(open(f"{WS}/data/progressive/keys.json"))
    enc = urllib.parse.quote(keys["NIFTY"], safe="")
    df = candles_df(call(f"/v3/historical-candle/{enc}/days/1/2026-10-31/2026-10-26"))
    got = {str(r["timestamp"])[:10]: float(r["close"]) for _, r in df.iterrows()}
    last = nifty_daily[-1]
    assert abs(got.get(last["date"], -1) - last["close"]) < 0.51, "nifty overlap mismatch"
    for d in ("2026-10-29", "2026-10-30"):
        if d in got:
            nifty_daily.append({"date": d, "high": got[d], "low": got[d],
                                "close": got[d]})
    nifty_daily.sort(key=lambda x: x["date"])
    log(f"nifty daily extended: last={nifty_daily[-1]}")
except Exception as e:
    log("NIFTY EXTENSION FAILED:", str(e)[:160])

NIFTY_REG = regime_maps_from(nifty_daily)
def below50(day):
    r = NIFTY_REG.get(day)
    return bool(r and r["ma50"] is not None and r["prev_close"] <= r["ma50"])
def g1(day):
    r = NIFTY_REG.get(day)
    return bool(r and r["ma50"] is not None and r["prev_close"] > r["ma50"])
def cond_inv1(day):
    return not g1(day)

# independent spot-check of the 50DMA math on raw closes
_cl = [d["close"] for d in nifty_daily]
_cd = [d["date"] for d in nifty_daily]
for probe in ("2025-01-02", "2025-03-17", "2025-06-02", "2026-10-30"):
    i = _cd.index(probe)
    ma50 = sum(_cl[i - 50:i]) / 50
    assert abs(ma50 - NIFTY_REG[probe]["ma50"]) < 1e-9, probe
    assert abs(_cl[i - 1] - NIFTY_REG[probe]["prev_close"]) < 1e-9, probe
log("regime spot-checks pass (2025-01-02, 2025-03-17, 2025-06-02, 2026-10-30);",
    "below50 on 2025-01-02:", below50("2025-01-02"),
    "| first 2025 day with computable ma50:",
    min(d for d in NIFTY_REG if d.startswith("2025") and NIFTY_REG[d]["ma50"] is not None))

# =====================================================================
# 5. ADR + CHAINS (stocks_equity_round8.py verbatim)
# =====================================================================
def adr_map():
    out = {}
    for sym in sorted(os.listdir(SHADOW)):
        p = f"{SHADOW}/{sym}/spot_daily.csv"
        if not os.path.exists(p):
            continue
        daily = []
        with open(p) as f:
            for r in csv.DictReader(f):
                try:
                    daily.append({"date": r["date"][:10], "high": float(r["high"]),
                                  "low": float(r["low"]), "close": float(r["close"])})
                except Exception:
                    pass
        daily.sort(key=lambda x: x["date"])
        idx = {d["date"]: i for i, d in enumerate(daily)}
        for d in daily:
            i = idx[d["date"]]
            if i < 5:
                out[(sym, d["date"])] = None
                continue
            prior = daily[max(0, i - 10):i]
            if len(prior) < 5:
                out[(sym, d["date"])] = None
                continue
            vals = [(x["high"] - x["low"]) / x["close"] * 100 for x in prior if x["close"]]
            out[(sym, d["date"])] = round(sum(vals) / len(vals), 3) if vals else None
    return out

ADR = adr_map()

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

def run_chain(sym, day, cell):
    ctx = DAYCTX.get((sym, day))
    if ctx is None: return []
    candles = ctx["candles"]
    trades, start = [], 0
    while True:
        chosen = NS["pool_pick"](ctx, NS["v4_head"](ctx, start), NS["skor_head"](ctx, start))
        if chosen is None: break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles): break
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        _, tp, sp = cell
        er, ep, et, exit_idx, gross = replay_plain(candles, entry_idx, sign, entry, tp, sp)
        trades.append({"date": day, "stock": sym, "direction": direction, "setup": setup,
                       "round": len(trades) + 1, "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er, "exit_time": et,
                       "exit_price": round(ep, 2), "gross": round(gross, 2),
                       "net": round(gross - COST, 2), "event_status": ctx["event_status"]})
        start = exit_idx
    return trades

# =====================================================================
# 6. F4 (stocks_M2_fix.py build2/collect2 verbatim, refs adapted)
# =====================================================================
_AUDIT = {"trades": 0, "violations": 0}
T_MEAS = "10:00"
def premove(candles, window_end):
    day_open = candles[0]["open"]
    pre = [c for c in candles if c["time"] < window_end]
    if not pre or not day_open:
        return None
    return pre[-1]["close"] / day_open - 1

def pick(sym, day, ctx, start):
    return NS["pool_pick"](ctx, NS["v4_head"](ctx, start), NS["skor_head"](ctx, start))

def build2(sym, day, cfg, TP, SP, pm_override=None):
    ctx = DAYCTX.get((sym, day))
    if ctx is None:
        return []
    if cfg.get("regime") == "below50" and not below50(day):
        return []
    candles = ctx["candles"]
    pm = pm_override if pm_override is not None else premove(candles, T_MEAS)
    if pm is None or abs(pm) < 0.005:
        return []
    hi = cfg.get("band_hi")
    if hi is not None and abs(pm) >= hi / 100.0:
        return []
    move_dir = 1 if pm > 0 else -1
    want = move_dir  # follow
    trades = []
    start = next((i for i, c in enumerate(candles) if c["time"] >= T_MEAS), None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = pick(sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = replay_plain(candles, ei, sign, entry, TP, SP)
        _AUDIT["trades"] += 1
        if candles[ei]["time"] < T_MEAS or candles[idx]["time"] < T_MEAS or ei <= idx:
            _AUDIT["violations"] += 1
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "sig_time": candles[idx]["time"],
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 3), "meas_time": T_MEAS})
        start = xi
    return trades

def collect2(days, cfg, TP, SP, lag=False):
    all_days = sorted({d for (s, d) in DAYCTX})
    prev_of = {d: all_days[i - 1] for i, d in enumerate(all_days) if i > 0}
    out = []
    for sym in SYMBOLS:
        for day in days:
            pm_o = None
            if lag:
                pd = prev_of.get(day)
                pctx = DAYCTX.get((sym, pd)) if pd else None
                if pctx is None:
                    continue
                pm_o = premove(pctx["candles"], T_MEAS)
                if pm_o is None:
                    continue
            out.extend(build2(sym, day, cfg, TP, SP, pm_override=pm_o))
    return out

def wk(d):
    return date.fromisoformat(d).weekday() >= 5

F4_CFG = {"band_hi": 1.0, "regime": "below50"}
EXCL_DIR = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
            ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
            ("HINDCOPPER", "SHORT"), ("OIL", "SHORT"),
            ("IRCTC", "SHORT"), ("HINDALCO", "LONG"),
            ("TATASTEEL", "LONG"), ("NHPC", "SHORT"),
            ("PFC", "SHORT"), ("RECLTD", "SHORT")}
def f4_keep(t):
    return (not wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"
            and t["leg"] != "round2"
            and (t["symbol"], t["dir"]) not in EXCL_DIR)

# =====================================================================
# 7. INV-LONG (round8 chains -> tuning_inv p2_filter -> cond_inv1 -> LONG)
# =====================================================================
def build_inv(days):
    rows = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    p2 = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
          and (r["adr"] or 0) >= 3.0]
    inv1 = [r for r in p2 if cond_inv1(r["date"])]
    lng = [r for r in inv1 if r["direction"] == "LONG"]
    book = [r for r in lng if not wk(r["date"])
            and r["stock"] not in {"BDL", "VEDL", "HINDZINC", "INDUSTOWER",
                                   "KALYANKJIL"}]
    stages = {"chain_rows": len(rows), "p2": len(p2), "inv1_both_dir": len(inv1),
              "long_only": len(lng), "book_after_excl_rf1": len(book)}
    return book, stages

# =====================================================================
# 8. HELPERS
# =====================================================================
def rd(p):
    with open(f"{WS}/{p}") as f:
        return list(csv.DictReader(f))

def month_table(trades, months):
    m = defaultdict(float); c = defaultdict(int)
    for t in trades:
        m[t["date"][:7]] += t["net"]; c[t["date"][:7]] += 1
    return ({k: round(m.get(k, 0.0), 2) for k in months},
            {k: c.get(k, 0) for k in months})

def extop3(trades):
    per = defaultdict(float)
    for t in trades:
        per[t["stock"]] += t["net"]
    top3 = sorted(per.items(), key=lambda kv: -kv[1])[:3]
    return (round(sum(t["net"] for t in trades
                      if t["stock"] not in {k for k, _ in top3}), 2),
            [(k, round(v, 2)) for k, v in top3])

def stats_block(trades, months):
    tot = round(sum(t["net"] for t in trades), 2)
    mt, mc = month_table(trades, months)
    per = defaultdict(float)
    for t in trades:
        per[t["stock"]] += t["net"]
    ex, top3 = extop3(trades)
    chrono = sorted(trades, key=lambda t: (t["date"], t.get("entry_time", "09:15"),
                                            t["stock"], t["comp"]))
    cum = 0.0; peak = 0.0; maxdd = 0.0
    for t in chrono:
        cum += t["net"]; peak = max(peak, cum); maxdd = min(maxdd, cum - peak)
    return {"trades": len(trades), "total": tot,
            "expectancy": round(tot / len(trades), 2) if trades else None,
            "win_pct": round(100.0 * sum(1 for t in trades if t["net"] > 0)
                             / len(trades), 1) if trades else None,
            "months": mt, "month_trades": mc,
            "red_months": [k for k, v in mt.items() if v < 0],
            "worst_month": min(mt, key=mt.get) if mt else None,
            "worst_month_net": mt[min(mt, key=mt.get)] if mt else None,
            "breadth_pos_stocks": sum(1 for v in per.values() if v > 0),
            "per_stock": {k: round(v, 2) for k, v in
                          sorted(per.items(), key=lambda kv: -kv[1])},
            "ex_top3": ex, "top3": top3, "max_drawdown": round(maxdd, 2)}

# =====================================================================
# 9. 2026 CONTROL — (a) SAT-36 dump assembly == plateau
#                    (b) F4 machinery rebuild == frozen F4 sets
#                    (c) INV machinery rebuild == frozen INV set
# =====================================================================
RESULTS = {"control": {}, "run2025": {}}
STATE = {"2026-01": 28536.25, "2026-02": 18419.86, "2026-03": 20584.41,
         "2026-04": 9895.49, "2026-05": 34880.86, "2026-06": 3823.22,
         "2026-07": 6965.93, "2026-08": 666.78, "2026-09": 19562.51,
         "2026-10": 54272.43}
STATE_TOTAL, STATE_TRADES, STATE_EXTOP3 = 197607.74, 663, 72518.25
MONTHS26 = [f"2026-{i:02d}" for i in range(1, 11)]
MONTHS25 = [f"2025-{i:02d}" for i in range(1, 13)]

# (a) dump assembly, transcribed from stocks_engine_sat36_score.py
inv_d = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG",
          "dir": "LONG", "net": float(t["net_rs_provisional_per100"]),
          "entry_time": t["entry_time"]}
         for t in rd("tuning_inv_T1_T125_S050_trades.csv")
         if t["direction"] == "LONG"
         and not wk(t["date"]) and t["stock"] != "BDL"
         and t["stock"] != "VEDL" and t["stock"] != "HINDZINC"
         and t["stock"] != "INDUSTOWER" and t["stock"] != "KALYANKJIL"]
n4_d = [{"date": r["date"], "stock": r["stock"], "comp": "N4-V3",
         "dir": r["direction"], "net": float(r["net"]), "entry_time": r["entry_time"]}
        for r in rd("stocks_engine_sat15_n4_t150s080_trades.csv")
        if not wk(r["date"]) and r["stock"] != "ASTRAL"
        and not (r["stock"] == "TVSMOTOR" and r["direction"] == "LONG")
        and not (r["stock"] == "OIL" and r["direction"] == "LONG")]
p2f_d = [{"date": t["date"], "stock": t["symbol"], "comp": "P2F",
          "dir": t["direction"], "net": float(t["net_rs"]),
          "entry_time": t["entry_time"]}
         for t in rd("stocks_tuning_event_V1_combined_trades.csv")
         if t["leg"] == "P2F" and abs(float(t["reaction_ret_pct"])) >= 2.5
         and not wk(t["date"]) and t["symbol"] != "ASTRAL"
         and t["symbol"] != "HINDUNILVR"
         and not (t["symbol"] == "HINDALCO" and t["direction"] == "LONG")]
f4_d = []
for r in rd("stocks_engine_sat10_f4s095_trades.csv"):
    if wk(r["date"]) or r["setup"] == "setup3_bounce_rejection" \
            or r["leg"] == "round2" or (r["symbol"], r["dir"]) in EXCL_DIR:
        continue
    f4_d.append({"date": r["date"], "stock": r["symbol"], "comp": "F4",
                 "dir": r["dir"], "net": float(r["net"]),
                 "entry_time": r["entry_time"]})
r2_d = [{"date": r["date"], "stock": r["symbol"], "comp": "P2F-R2",
         "dir": r["direction"], "net": float(r["net_rs"]),
         "entry_time": r["entry_time"]}
        for r in rd("stocks_engine_sat13_p2fr2_trades.csv")
        if not (r["symbol"] == "TVSMOTOR" and r["direction"] == "LONG")]
r2low_d = [{"date": r["date"], "stock": r["symbol"], "comp": "R2-LOWBAND",
            "dir": r["direction"], "net": float(r["net_rs"]),
            "entry_time": r["entry_time"]}
           for r in rd("stocks_engine_sat33_r2lowband_trades.csv")]
book26_dumps = inv_d + n4_d + p2f_d + f4_d + r2_d + r2low_d
bt, _ = month_table(book26_dumps, MONTHS26)
ex0, top3_0 = extop3(book26_dumps)
ctrl_a = (bt == STATE and round(sum(t["net"] for t in book26_dumps), 2) == STATE_TOTAL
          and len(book26_dumps) == STATE_TRADES and ex0 == STATE_EXTOP3)
RESULTS["control"]["dump_assembly"] = {
    "pass": ctrl_a, "trades": len(book26_dumps),
    "total": round(sum(t["net"] for t in book26_dumps), 2),
    "months": bt, "ex_top3": ex0,
    "per_comp": {c: (len([t for t in book26_dumps if t["comp"] == c]),
                     round(sum(t["net"] for t in book26_dumps if t["comp"] == c), 2))
                 for c in ("INV-LONG", "N4-V3", "P2F", "F4", "P2F-R2", "R2-LOWBAND")}}
log("CONTROL A (SAT-36 dump assembly == plateau):", ctrl_a,
    RESULTS["control"]["dump_assembly"]["trades"], "tr",
    RESULTS["control"]["dump_assembly"]["total"])

# (b) F4 machinery rebuild over 2026
days26 = sorted({d for (s, d) in DAYCTX if d.startswith("2026")})
a0 = dict(_AUDIT)
raw080 = collect2(days26, F4_CFG, 1.50, 0.80)
aud080 = {"trades": _AUDIT["trades"] - a0["trades"],
          "violations": _AUDIT["violations"] - a0["violations"]}
oc4 = rd("stocks_engine_oc4_f4s080_trades.csv")
key5 = lambda t: (t["date"], t["symbol"], int(t["round"]), float(t["net"]), t["entry_time"])
ctrl_b1 = sorted(key5(t) for t in raw080) == sorted(
    (r["date"], r["symbol"], int(r["round"]), float(r["net"]), r["entry_time"]) for r in oc4)
log("CONTROL B1 (F4 rebuild T150/S080 == oc4 dump per-trade):", ctrl_b1,
    f"rebuild {len(raw080)} vs dump {len(oc4)}; audit {aud080}")
a0 = dict(_AUDIT)
raw095 = collect2(days26, F4_CFG, 1.50, 0.95)
aud095 = {"trades": _AUDIT["trades"] - a0["trades"],
          "violations": _AUDIT["violations"] - a0["violations"]}
f4_mine = [t for t in raw095 if f4_keep(t)]
f4key = lambda t: (t["date"], t["stock"], t["dir"], t["net"], t["entry_time"])
ctrl_b2 = sorted(f4key({"date": t["date"], "stock": t["symbol"], "dir": t["dir"],
                        "net": t["net"], "entry_time": t["entry_time"]}) for t in f4_mine) == \
          sorted(f4key(t) for t in f4_d)
log("CONTROL B2 (F4 filtered S095 rebuild == frozen F4 set):", ctrl_b2,
    f"{len(f4_mine)} tr; audit {aud095}")
RESULTS["control"]["f4_rebuild"] = {"anchor_oc4": ctrl_b1, "anchor_sat10set": ctrl_b2,
                                   "audit080": aud080, "audit095": aud095,
                                   "raw080_trades": len(raw080), "raw095_trades": len(raw095),
                                   "f4_book_trades": len(f4_mine),
                                   "f4_book_net": round(sum(t["net"] for t in f4_mine), 2)}

# (c) INV machinery rebuild over 2026
inv_mine, inv_stages26 = build_inv(days26)
invkey = lambda t: (t["date"], t["stock"], t["entry_time"], t["net"])
ctrl_c = sorted(invkey(t) for t in inv_mine) == sorted(invkey(t) for t in inv_d)
log("CONTROL C (INV-LONG rebuild == frozen INV set):", ctrl_c,
    f"{len(inv_mine)} tr; stages {inv_stages26}")
RESULTS["control"]["inv_rebuild"] = {"pass": ctrl_c, "stages": inv_stages26,
                                     "net": round(sum(t["net"] for t in inv_mine), 2)}
RESULTS["control"]["all_pass"] = bool(ctrl_a and ctrl_b1 and ctrl_b2 and ctrl_c
                                     and aud080["violations"] == 0
                                     and aud095["violations"] == 0)
log("CONTROL ALL PASS:", RESULTS["control"]["all_pass"])
if not RESULTS["control"]["all_pass"]:
    json.dump(RESULTS, open(f"{OUTD}/results.json", "w"), indent=1)
    log("CONTROL FAILED — stopping before 2025 scoring, per task STEP 3(ii).")
    sys.exit(2)

# =====================================================================
# 10. 2025 RUN — F4 + INV-LONG verbatim; event comps NOT RUNNABLE
# =====================================================================
days25 = sorted({d for (s, d) in DAYCTX if d.startswith("2025")})
wknd25 = [d for d in sorted({x["date"] for x in nifty_daily if x["date"].startswith("2025")})
          if wk(d)]
a0 = dict(_AUDIT)
raw25 = collect2(days25, F4_CFG, 1.50, 0.95)
aud25 = {"trades": _AUDIT["trades"] - a0["trades"],
         "violations": _AUDIT["violations"] - a0["violations"]}
f4_25_raw_kept = [t for t in raw25 if f4_keep(t)]
f4_25 = [{"date": t["date"], "stock": t["symbol"], "comp": "F4", "dir": t["dir"],
          "setup": t["setup"], "round": t["round"], "sig_time": t["sig_time"],
          "entry_time": t["entry_time"], "entry": t["entry"],
          "exit_reason": t["exit_reason"], "exit_time": t["exit_time"],
          "exit_price": t["exit"], "net": t["net"], "premove_pct": t["premove_pct"]}
         for t in f4_25_raw_kept]
rf1_f4 = sum(1 for t in raw25 if wk(t["date"]) and t["setup"] != "setup3_bounce_rejection"
             and t["leg"] != "round2" and (t["symbol"], t["dir"]) not in EXCL_DIR)
log(f"2025 F4: raw {len(raw25)} tr -> book {len(f4_25)} tr "
    f"net {round(sum(t['net'] for t in f4_25), 2)}; audit {aud25}; RF-1 dropped {rf1_f4}")

inv_25_raw, inv_stages25 = build_inv(days25)
inv_25 = [{"date": t["date"], "stock": t["stock"], "comp": "INV-LONG", "dir": "LONG",
           "setup": t["setup"], "round": t["round"], "sig_time": "",
           "entry_time": t["entry_time"], "entry": t["entry"],
           "exit_reason": t["exit_reason"], "exit_time": t["exit_time"],
           "exit_price": t["exit_price"], "net": t["net"], "premove_pct": ""}
          for t in inv_25_raw]
log(f"2025 INV-LONG: book {len(inv_25)} tr net {round(sum(t['net'] for t in inv_25), 2)}; "
    f"stages {inv_stages25}")

# timing audit assertions on ALL 2025 trades
viol = []
for t in f4_25:
    if t["sig_time"] < "10:00" or t["entry_time"] <= t["sig_time"] or wk(t["date"]):
        viol.append(("F4", t["date"], t["stock"]))
for t in inv_25:
    if not ("09:35" <= t["entry_time"] <= "15:10") or wk(t["date"]):
        viol.append(("INV", t["date"], t["stock"]))
    if t["exit_time"] < t["entry_time"]:
        viol.append(("INV-exit", t["date"], t["stock"]))
log("2025 timing audit violations:", len(viol), viol[:5])
assert aud25["violations"] == 0 and not viol, "TIMING AUDIT FAILED"

# F4 lag-placebo on 2025 (control colour only; not part of the book)
a0 = dict(_AUDIT)
pbo25 = collect2(days25, F4_CFG, 1.50, 0.95, lag=True)
pbo25k = [t for t in pbo25 if f4_keep(t)]
log(f"2025 F4 lag-placebo: {len(pbo25k)} tr net {round(sum(t['net'] for t in pbo25k), 2)} "
    f"(real {len(f4_25)} tr net {round(sum(t['net'] for t in f4_25), 2)})")

book25 = f4_25 + inv_25
s25 = stats_block(book25, MONTHS25)
s25_f4 = stats_block(f4_25, MONTHS25)
s25_inv = stats_block(inv_25, MONTHS25)
RESULTS["run2025"] = {
    "days": len(days25), "weekend_sessions_in_daily": wknd25,
    "f4": {"stages": {"raw": len(raw25), "book": len(f4_25), "rf1_dropped": rf1_f4},
           "audit": aud25, "stats": s25_f4,
           "placebo_lag": {"trades": len(pbo25k),
                           "net": round(sum(t["net"] for t in pbo25k), 2)}},
    "inv": {"stages": inv_stages25, "stats": s25_inv},
    "book_partial": s25,
    "timing_violations": len(viol)}
log("2025 PARTIAL BOOK (F4+INV):", s25["trades"], "tr, total", s25["total"],
    "| red months:", s25["red_months"], "| breadth", s25["breadth_pos_stocks"],
    "| ex-top3", s25["ex_top3"], "| maxDD", s25["max_drawdown"])

# combined (asymmetric: 2025 = 2 of 6 components only)
comb_total = round(s25["total"] + STATE_TOTAL, 2)
RESULTS["combined"] = {
    "total_2025_partial_plus_2026_full": comb_total,
    "monthly_avg_22mo": round(comb_total / 22, 2),
    "avg_2025_partial_per_month": round(s25["total"] / 12, 2),
    "avg_2026_full_per_month": round(STATE_TOTAL / 10, 2),
    "goal_per_month": 75000}
log("COMBINED (2025 partial + 2026 full):", comb_total, "avg/mo", RESULTS["combined"]["monthly_avg_22mo"])

# worst slices 2025 (observation only — noted, not applied)
slices = defaultdict(float); slicen = defaultdict(int)
for t in book25:
    slices[(t["comp"], t["stock"], t["dir"])] += t["net"]
    slicen[(t["comp"], t["stock"], t["dir"])] += 1
worst = sorted(slices.items(), key=lambda kv: kv[1])[:6]
RESULTS["run2025"]["worst_slices_observed"] = [
    {"comp": k[0], "stock": k[1], "dir": k[2], "trades": slicen[k], "net": round(v, 2)}
    for k, v in worst]

# =====================================================================
# 11. OUTPUTS
# =====================================================================
with open(f"{OUTD}/stocks_engine_2025_validation_trades.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["date", "stock", "comp", "dir", "setup", "round", "sig_time",
                "entry_time", "entry", "exit_reason", "exit_time", "exit_price",
                "net_rs_provisional_per100", "premove_pct"])
    for t in sorted(book25, key=lambda x: (x["date"], x["entry_time"], x["stock"])):
        w.writerow([t["date"], t["stock"], t["comp"], t["dir"], t["setup"], t["round"],
                    t["sig_time"], t["entry_time"], t["entry"], t["exit_reason"],
                    t["exit_time"], t["exit_price"], t["net"], t["premove_pct"]])
json.dump(RESULTS, open(f"{OUTD}/results.json", "w"), indent=1)
log("wrote trades CSV + results.json")
print("\n".join(LOG))
