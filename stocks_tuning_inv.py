#!/usr/bin/env python3
"""INV family tuning loop — engine. Spec: stocks_tuning_inv_frozen.md
(frozen before scoring). EQUITY CASH intraday, LONG/SHORT, paper only.
Provisional per 100 shares; net = gross - Rs40/trade.
Machinery: Round 8's run_chain/pools/ADR exec'd verbatim; regime maps
copied verbatim from Round 9. Chains are rebuilt per exit cell and
cached (full uncapped chain rows with adr + day-gap attached); all
pool/condition/direction/cap filters are row operations on the cache.
Usage: python3 stocks_tuning_inv.py [validate|build|T1|T2|T3|T4|T5|T6]
"""
import csv, json, collections, os, sys, bisect

BASE = "/home/hatch/workspace/trading"
COST = 40.0
CACHE = f"{BASE}/tuning_inv_cache"
os.makedirs(CACHE, exist_ok=True)
RESULTS_F = f"{BASE}/stocks_tuning_inv_results.json"
REPORT_F = f"{BASE}/stocks_tuning_inv_report.md"

# ---- Round 8 machinery (exec verbatim; its main() is __main__-guarded)
NS8 = {}
exec(compile(open(f"{BASE}/stocks_equity_round8.py").read(), "round8", "exec"), NS8)
run_chain = NS8["run_chain"]; pools8 = NS8["pools"]
SYMBOLS = NS8["SYMBOLS"]; ALL_DAYS = NS8["ALL_DAYS"]; ADR = NS8["ADR"]
DAYCTX = NS8["DAYCTX"]; v4_head = NS8["v4_head"]; skor_head = NS8["skor_head"]
pool_pick = NS8["pool_pick"]

# ---- regime maps (Round 9, verbatim logic) ----
def load_daily(sym):
    p = f"{BASE}/data/progressive/{sym}/spot_daily.csv"
    rows = []
    with open(p) as f:
        for r in csv.DictReader(f):
            try:
                rows.append({"date": r["date"][:10], "high": float(r["high"]),
                             "low": float(r["low"]), "close": float(r["close"])})
            except Exception:
                pass
    rows.sort(key=lambda x: x["date"])
    return rows

def regime_maps(sym):
    daily = load_daily(sym)
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

print("building regime maps...")
NIFTY_REG = regime_maps("NIFTY")
STOCK_REG = {sym: regime_maps(sym) for sym in SYMBOLS}

# ---- conditions (row -> True means the trade is TAKEN under the variant) ----
def g1(row):  # Round 9 verbatim: above-trend keep
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["ma50"] is not None and r["prev_close"] > r["ma50"])

def g2(row):  # Round 9 verbatim
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["ma20"] is not None and r["prev_close"] > r["ma20"])

def cond_inv1(row):
    return not g1(row)

def cond_n20(row):
    return not g2(row)

def cond_dbl(row):
    if not cond_inv1(row):
        return False
    r = STOCK_REG[row["stock"]].get(row["date"])
    return bool(r and r["ma20"] is not None and r["prev_close"] <= r["ma20"])

def cond_band(row):
    r = NIFTY_REG.get(row["date"])
    if not r or r["ma50"] is None:
        return False
    return r["prev_close"] <= r["ma50"] and (r["ma50"] - r["prev_close"]) / r["ma50"] <= 0.03

CONDS = {"INV1": cond_inv1, "N20": cond_n20, "DBL": cond_dbl, "BAND": cond_band}

# ---- trailing-exit replay (frozen mechanics, see spec T2) ----
def replay_trail(candles, entry_idx, sign, entry, act_pct, trail_pct):
    stop = entry * (1 - sign * 0.5 / 100)
    act_px = entry * (1 + sign * act_pct / 100)
    armed = False
    extreme = entry
    for j in range(entry_idx, len(candles)):
        c = candles[j]
        if sign == 1:
            if c["low"] <= stop:
                er = "trail_stop" if armed else "stop"
                return er, stop, c["time"], j, 100.0 * sign * (stop - entry)
        else:
            if c["high"] >= stop:
                er = "trail_stop" if armed else "stop"
                return er, stop, c["time"], j, 100.0 * sign * (stop - entry)
        if c["time"] == "15:10":
            return "square_off", c["close"], c["time"], j, 100.0 * sign * (c["close"] - entry)
        if sign == 1:
            if c["high"] > extreme:
                extreme = c["high"]
            if extreme >= act_px:
                armed = True
                ns = extreme * (1 - trail_pct / 100)
                if ns > stop:
                    stop = ns
        else:
            if c["low"] < extreme:
                extreme = c["low"]
            if extreme <= act_px:
                armed = True
                ns = extreme * (1 + trail_pct / 100)
                if ns < stop:
                    stop = ns
    c = candles[-1]
    return "square_off", c["close"], c["time"], len(candles) - 1, 100.0 * sign * (c["close"] - entry)

def run_chain_trail(sym, day, act_pct, trail_pct):
    ctx = DAYCTX.get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    trades, start = [], 0
    while True:
        chosen = pool_pick(ctx, v4_head(ctx, start), skor_head(ctx, start))
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        er, ep, et, exit_idx, gross = replay_trail(candles, entry_idx, sign, entry, act_pct, trail_pct)
        trades.append({"date": day, "stock": sym, "direction": direction, "setup": setup,
                       "round": len(trades) + 1, "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er, "exit_time": et,
                       "exit_price": round(ep, 2), "gross": round(gross, 2),
                       "net": round(gross - COST, 2), "event_status": ctx["event_status"]})
        start = exit_idx
    return trades

# ---- chain cache ----
PLAIN_CELLS = [(t, s) for t in (1.0, 1.25, 1.5, 1.75, 2.0) for s in (0.5, 0.65, 0.8)]
TRAIL_CELLS = {"TRA": (0.75, 0.4), "TRB": (1.0, 0.5)}

def plain_label(tp, sp):
    return f"T{int(round(tp*100)):03d}_S{int(round(sp*100)):03d}"

def attach(rows, sym, day):
    ctx = DAYCTX.get((sym, day))
    gap = None
    if ctx is not None and ctx["pdc"]:
        gap = round((ctx["day_open"] - ctx["pdc"]) / ctx["pdc"] * 100, 3)
    for r in rows:
        r["adr"] = ADR.get((sym, day))
        r["gap_pct"] = gap
    return rows

def build_cell(label):
    path = f"{CACHE}/{label}.json"
    if os.path.exists(path):
        return json.load(open(path))
    rows = []
    if label in TRAIL_CELLS:
        act, tr = TRAIL_CELLS[label]
        for sym in SYMBOLS:
            for day in ALL_DAYS:
                rows.extend(attach(run_chain_trail(sym, day, act, tr), sym, day))
    else:
        tp = int(label[1:4]) / 100.0; sp = int(label[6:9]) / 100.0
        for sym in SYMBOLS:
            for day in ALL_DAYS:
                rows.extend(attach(run_chain(sym, day, ("PLAIN", tp, sp)), sym, day))
    json.dump(rows, open(path, "w"))
    print(f"built {label}: {len(rows)} chain rows")
    return rows

# ---- scoring helpers ----
def p2_filter(rows, cap=2, cutoff="10:30"):
    return [r for r in rows if r["round"] <= cap and r["entry_time"] < cutoff
            and (r["adr"] or 0) >= 3.0]

def breadth(rows):
    per = collections.defaultdict(float)
    cnt = collections.defaultdict(int)
    for r in rows:
        per[r["stock"]] += r["net"]; cnt[r["stock"]] += 1
    vals = {s: round(per.get(s, 0.0), 2) for s in SYMBOLS}
    pos = sorted([v for v in vals.values() if v > 0], reverse=True)
    tot = sum(vals.values())
    top3 = round(100.0 * sum(pos[:3]) / tot, 1) if tot > 0 and pos else None
    return {"pos_stocks": len(pos), "top3_share_pct": top3,
            "per_stock_net": vals, "per_stock_n": {s: cnt.get(s, 0) for s in SYMBOLS}}

def summarize(rows):
    n = len(rows)
    if n == 0:
        return {"trades": 0, "win_pct": None, "gross_exp": None, "net_exp": None,
                "net_total": 0.0, "gross_total": 0.0}
    g = sum(r["gross"] for r in rows); nt = sum(r["net"] for r in rows)
    wins = sum(1 for r in rows if r["net"] > 0)
    return {"trades": n, "win_pct": round(100.0 * wins / n, 1),
            "gross_exp": round(g / n, 2), "net_exp": round(nt / n, 2),
            "net_total": round(nt, 2), "gross_total": round(g, 2)}

def block(rows):
    """Full scoring block: halves + October + breadth + pass gate."""
    jm = [r for r in rows if r["date"] < "2026-06-01"]
    jo = [r for r in rows if r["date"] >= "2026-06-01"]
    oc = [r for r in rows if r["date"] >= "2026-10-01"]
    b = breadth(rows)
    s_all, s_jm, s_jo = summarize(rows), summarize(jm), summarize(jo)
    passed = (s_jm["net_total"] > 0 and s_jo["net_total"] > 0
              and b["pos_stocks"] >= 10 and (s_all["net_exp"] or 0) > 0)
    return {"all": s_all, "jan_may": s_jm, "jun_oct": s_jo, "october": summarize(oc),
            "breadth": b, "pass_gate": passed}

def load_results():
    if os.path.exists(RESULTS_F):
        return json.load(open(RESULTS_F))
    return {"basis": "provisional per 100 shares, net = gross - Rs40/trade",
            "validation": {}, "families": {}}

def save_results(res):
    json.dump(res, open(RESULTS_F, "w"), indent=1)

def report_append(text):
    with open(REPORT_F, "a") as f:
        f.write(text)

def fmt(b):
    a, jm, jo, oc = b["all"], b["jan_may"], b["jun_oct"], b["october"]
    br = b["breadth"]
    return (f"n={a['trades']} win={a['win_pct']}% gExp=₹{a['gross_exp']} netExp=₹{a['net_exp']} "
            f"| JM net=₹{jm['net_total']} (n={jm['trades']}) | JO net=₹{jo['net_total']} (n={jo['trades']}) "
            f"| total=₹{a['net_total']} | Oct=₹{oc['net_total']} (n={oc['trades']}) "
            f"| breadth {br['pos_stocks']}/25, top3 {br['top3_share_pct']}% | PASS={b['pass_gate']}")

def dump_trades(rows, label):
    path = f"{BASE}/tuning_inv_{label}_trades.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "stock", "direction", "setup", "round", "entry_time", "entry",
                    "exit_reason", "exit_time", "exit_price", "gross_rs_provisional_per100",
                    "net_rs_provisional_per100", "event_status", "adr_pct", "day_gap_pct"])
        for r in sorted(rows, key=lambda r: (r["date"], r["stock"], r["round"])):
            w.writerow([r["date"], r["stock"], r["direction"], r["setup"], r["round"],
                        r["entry_time"], r["entry"], r["exit_reason"], r["exit_time"],
                        r["exit_price"], r["gross"], r["net"], r["event_status"],
                        r["adr"], r["gap_pct"]])
    return path

# ================= VALIDATION =================
def do_validate():
    res = load_results()
    ch125 = build_cell("T125_S050")
    ch100 = build_cell("T100_S050")
    p2_125 = p2_filter(ch125); p2_100 = p2_filter(ch100)
    checks = {}
    def chk(name, rows, exp_n, exp_net, exp_jm, exp_jo):
        s = block(rows)
        ok = (s["all"]["trades"] == exp_n and abs(s["all"]["net_total"] - exp_net) < 0.01
              and abs(s["jan_may"]["net_total"] - exp_jm) < 0.01
              and abs(s["jun_oct"]["net_total"] - exp_jo) < 0.01)
        checks[name] = {"got_n": s["all"]["trades"], "exp_n": exp_n,
                        "got_net": s["all"]["net_total"], "exp_net": exp_net,
                        "got_jm": s["jan_may"]["net_total"], "exp_jm": exp_jm,
                        "got_jo": s["jun_oct"]["net_total"], "exp_jo": exp_jo, "pass": ok}
        print(f"VALIDATION {name}: n {s['all']['trades']} vs {exp_n}, net {s['all']['net_total']} vs {exp_net}, "
              f"JM {s['jan_may']['net_total']} vs {exp_jm}, JO {s['jun_oct']['net_total']} vs {exp_jo} -> {'PASS' if ok else 'FAIL'}")
        return s
    s_pool = summarize(p2_125)
    ok_pool = (s_pool["trades"] == 918 and abs(s_pool["net_total"] - 10657.81) < 0.01)
    checks["P2_T125"] = {"got_n": s_pool["trades"], "exp_n": 918,
                         "got_net": s_pool["net_total"], "exp_net": 10657.81, "pass": ok_pool}
    print(f"VALIDATION P2_T125: n {s_pool['trades']} vs 918, net {s_pool['net_total']} vs 10657.81 -> {'PASS' if ok_pool else 'FAIL'}")
    chk("INV1_T125", [r for r in p2_125 if cond_inv1(r)], 694, 22964.30, 7255.01, 15709.29)
    chk("INV1_T10", [r for r in p2_100 if cond_inv1(r)], 721, 19232.08, -517.74, 19749.82)
    chk("INV2cond_T125", [r for r in p2_125 if cond_n20(r)], 563, 48437.14, 24913.18, 23523.96)
    res["validation"] = checks
    res["validation_all_pass"] = all(c["pass"] for c in checks.values())
    save_results(res)
    if not os.path.exists(REPORT_F):
        report_append(
            "# Stocks EQUITY — INV family tuning loop — report\n\n"
            "**EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders. Real money ₹0.**\n"
            "**All figures provisional per 100 shares, net = gross − ₹40/trade. "
            "Window Jan–Oct 2026 (Oct = 1–28).**\n"
            "Spec: `stocks_tuning_inv_frozen.md` (frozen before scoring). "
            "This loop produces v2 CANDIDATES only — the November INV1 shadow "
            "(`stocks_p2inv_november_shadow_spec.md`) is untouched.\n\n")
    v = "PASS" if res["validation_all_pass"] else "FAIL"
    report_append(f"## Validation gate — {v}\n\n"
                  f"Rebuilt machinery vs published Round 8/9/10 figures: "
                  f"P2@T125 (918, +₹10,657.81), INV1@T125 (694, +₹22,964.30; halves "
                  f"+₹7,255.01 / +₹15,709.29), INV1@T10 (721, +₹19,232.08; halves "
                  f"−₹517.74 / +₹19,749.82), INV2-condition@T125 (563, +₹48,437.14; halves "
                  f"+₹24,913.18 / +₹23,523.96). Gate result: **{v}** "
                  f"(detail in `stocks_tuning_inv_results.json`).\n\n")
    print("VALIDATION ALL PASS:", res["validation_all_pass"])
    return res["validation_all_pass"]

def do_build():
    for tp, sp in PLAIN_CELLS:
        build_cell(plain_label(tp, sp))
    for label in TRAIL_CELLS:
        build_cell(label)
    print("all chains built/cached")

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        do_validate()
    elif cmd == "build":
        do_build()
    else:
        print(f"family step {cmd} is in stocks_tuning_inv_families.py")
