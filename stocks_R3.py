#!/usr/bin/env python3
"""LINE R3 — INV-LONG / INV1 transfer test to the new 25 + pooled-50 read.
Spec: stocks_R3_frozen.md (frozen before scoring). Rules VERBATIM from
stocks_tuning_inv_frozen.md / stocks_inv_v2_candidate_spec.md — no
re-tuning on the new universe.
Machinery: Line 4's transfer pattern (stocks_tuning_universe.py) —
regime maps, cond_inv1, p2_filter, build_cell, block copied verbatim;
home run uses stocks_equity_round8.py, ext run uses
stocks_equity_round8_ext.py (path/symbol-substituted frozen Round 8).
Modes: all (validate_home -> ext_inv -> pool50, stops if gate fails).
Equity cash, LONG/SHORT, paper only, real Rs0. Provisional per 100
shares, net = gross - Rs40/trade. Window Jan-Oct 2026 (Oct = 1-28).
"""
import csv, json, collections, os, sys

BASE = "/home/hatch/workspace/trading"
COST = 40.0
OLD_SYMS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR", "OBEROIRLTY",
            "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK", "NHPC", "PFC", "IRCTC", "WIPRO",
            "NATIONALUM", "VEDL", "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL",
            "ASTRAL", "BDL", "OIL", "HINDUNILVR"]
EXT_SYMS = ["RELIANCE", "TCS", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "LT",
            "AXISBANK", "KOTAKBANK", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA",
            "TITAN", "M&M", "ULTRACEMCO", "NESTLEIND", "POWERGRID", "ONGC", "COALINDIA",
            "JSWSTEEL", "GRASIM", "CIPLA", "DRREDDY", "EICHERMOT"]

# ================= machinery (copied verbatim from stocks_tuning_universe.py) =================
def load_daily(data_dir, sym):
    p = f"{BASE}/data/{data_dir}/{sym}/spot_daily.csv"
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

def regime_maps(data_dir, sym):
    daily = load_daily(data_dir, sym)
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

NIFTY_REG = None

def g1(row):
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["ma50"] is not None and r["prev_close"] > r["ma50"])

def cond_inv1(row):
    return not g1(row)

def attach(ns, rows, sym, day):
    ctx = ns["DAYCTX"].get((sym, day))
    gap = None
    if ctx is not None and ctx["pdc"]:
        gap = round((ctx["day_open"] - ctx["pdc"]) / ctx["pdc"] * 100, 3)
    for r in rows:
        r["adr"] = ns["ADR"].get((sym, day))
        r["gap_pct"] = gap
    return rows

def build_cell(ns, cache_dir, label):
    os.makedirs(cache_dir, exist_ok=True)
    path = f"{cache_dir}/{label}.json"
    if os.path.exists(path):
        return json.load(open(path))
    tp = int(label[1:4]) / 100.0; sp = int(label[6:9]) / 100.0
    rows = []
    for sym in ns["SYMBOLS"]:
        for day in ns["ALL_DAYS"]:
            rows.extend(attach(ns, ns["run_chain"](sym, day, ("PLAIN", tp, sp)), sym, day))
    json.dump(rows, open(path, "w"))
    print(f"built {label}: {len(rows)} chain rows", flush=True)
    return rows

def p2_filter(rows, cap=2, cutoff="10:30"):
    return [r for r in rows if r["round"] <= cap and r["entry_time"] < cutoff
            and (r["adr"] or 0) >= 3.0]

def breadth(rows, symbols):
    per = collections.defaultdict(float)
    cnt = collections.defaultdict(int)
    for r in rows:
        per[r["stock"]] += r["net"]; cnt[r["stock"]] += 1
    vals = {s: round(per.get(s, 0.0), 2) for s in symbols}
    pos = sorted([v for v in vals.values() if v > 0], reverse=True)
    tot = sum(vals.values())
    top3 = round(100.0 * sum(pos[:3]) / tot, 1) if tot > 0 and pos else None
    return {"pos_stocks": len(pos), "top3_share_pct": top3,
            "per_stock_net": vals, "per_stock_n": {s: cnt.get(s, 0) for s in symbols}}

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

def block(rows, symbols):
    jm = [r for r in rows if r["date"] < "2026-06-01"]
    jo = [r for r in rows if r["date"] >= "2026-06-01"]
    oc = [r for r in rows if r["date"] >= "2026-10-01"]
    b = breadth(rows, symbols)
    s_all, s_jm, s_jo = summarize(rows), summarize(jm), summarize(jo)
    passed = (s_jm["net_total"] > 0 and s_jo["net_total"] > 0
              and b["pos_stocks"] >= 10 and (s_all["net_exp"] or 0) > 0)
    return {"all": s_all, "jan_may": s_jm, "jun_oct": s_jo, "october": summarize(oc),
            "breadth": b, "pass_gate": passed}

def fmt(b, denom):
    a, jm, jo, oc = b["all"], b["jan_may"], b["jun_oct"], b["october"]
    br = b["breadth"]
    return (f"n={a['trades']} win={a['win_pct']}% netExp=Rs{a['net_exp']} "
            f"| JM net=Rs{jm['net_total']} (n={jm['trades']}) | JO net=Rs{jo['net_total']} (n={jo['trades']}) "
            f"| total=Rs{a['net_total']} | Oct=Rs{oc['net_total']} (n={oc['trades']}) "
            f"| breadth {br['pos_stocks']}/{denom}, top3 {br['top3_share_pct']}% | PASS={b['pass_gate']}")

def transfers(b, denom_breadth_min=10):
    """R3 frozen transfer standard: both halves > 0 AND breadth >= 10/25."""
    return (b["jan_may"]["net_total"] > 0 and b["jun_oct"]["net_total"] > 0
            and b["breadth"]["pos_stocks"] >= denom_breadth_min)

def exec_round8(fname):
    ns = {}
    exec(compile(open(f"{BASE}/{fname}").read(), fname, "exec"), ns)
    return ns

def setup_regime(data_dir):
    global NIFTY_REG
    print("building regime maps...", flush=True)
    NIFTY_REG = regime_maps(data_dir, "NIFTY")

def dump_trade_csv(rows, path):
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

# ================= steps =================
def step_validate_home(out):
    ns = exec_round8("stocks_equity_round8.py")
    setup_regime("progressive")
    ch = build_cell(ns, f"{BASE}/R3_cache_home", "T125_S050")
    p2 = p2_filter(ch)
    inv1 = [r for r in p2 if cond_inv1(r)]
    inv_long = [r for r in inv1 if r["direction"] == "LONG"]
    b1, bl = block(inv1, OLD_SYMS), block(inv_long, OLD_SYMS)
    def chk(name, b, n, net, jm, jo):
        ok = (b["all"]["trades"] == n and abs(b["all"]["net_total"] - net) < 0.01
              and abs(b["jan_may"]["net_total"] - jm) < 0.01
              and abs(b["jun_oct"]["net_total"] - jo) < 0.01)
        print(f"ANCHOR {name}: n {b['all']['trades']} vs {n}, net {b['all']['net_total']} vs {net}, "
              f"JM {b['jan_may']['net_total']} vs {jm}, JO {b['jun_oct']['net_total']} vs {jo} "
              f"-> {'PASS' if ok else 'FAIL'}", flush=True)
        return ok
    ok = chk("INV1 home", b1, 694, 22964.30, 7255.01, 15709.29)
    ok &= chk("INV-LONG home", bl, 249, 24185.73, 14751.12, 9434.61)
    ok_oct = abs(bl["october"]["net_total"] - 7691.08) < 0.01
    ok_br = (bl["breadth"]["pos_stocks"] == 12
             and abs(bl["breadth"]["top3_share_pct"] - 116.2) < 0.05)
    print(f"ANCHOR INV-LONG home Oct {bl['october']['net_total']} vs 7691.08 -> {'PASS' if ok_oct else 'FAIL'}")
    print(f"ANCHOR INV-LONG home breadth {bl['breadth']['pos_stocks']} vs 12, top3 "
          f"{bl['breadth']['top3_share_pct']} vs 116.2 -> {'PASS' if ok_br else 'FAIL'}")
    ok = ok and ok_oct and ok_br
    print("VALIDATION HOME ALL PASS:", ok, flush=True)
    out["home"] = {"inv1": b1, "inv_long": bl, "anchor_pass": bool(ok),
                   "inv_long_rows": inv_long}
    return ok

def step_ext(out):
    ns = exec_round8("stocks_equity_round8_ext.py")
    setup_regime("progressive_ext")
    ch = build_cell(ns, f"{BASE}/R3_cache_ext", "T125_S050")
    p2 = p2_filter(ch)
    inv1 = [r for r in p2 if cond_inv1(r)]
    inv_long = [r for r in inv1 if r["direction"] == "LONG"]
    b1, bl = block(inv1, EXT_SYMS), block(inv_long, EXT_SYMS)
    print("EXT P2 pool:", fmt(block(p2, EXT_SYMS), 25), flush=True)
    print("EXT INV1 (both dir):", fmt(b1, 25), "| TRANSFERS(std) =", transfers(b1), flush=True)
    print("EXT INV-LONG (RULE UNDER TEST):", fmt(bl, 25), "| TRANSFERS(std) =", transfers(bl), flush=True)
    out["ext"] = {"p2_pool": block(p2, EXT_SYMS), "inv1": b1, "inv_long": bl,
                  "inv_long_transfers": bool(transfers(bl)),
                  "inv1_transfers": bool(transfers(b1)),
                  "inv1_rows": inv1, "inv_long_rows": inv_long}
    dump_trade_csv(inv1, f"{BASE}/R3_ext_inv1_trades.csv")
    dump_trade_csv(inv_long, f"{BASE}/R3_ext_inv_long_trades.csv")

def step_pool50(out):
    rows = out["home"]["inv_long_rows"] + out["ext"]["inv_long_rows"]
    allsyms = OLD_SYMS + EXT_SYMS
    b = block(rows, allsyms)
    print("POOL50 INV-LONG:", fmt(b, 50), flush=True)
    per = b["breadth"]["per_stock_net"]
    tv, gl = per.get("TVSMOTOR", 0.0), per.get("GLENMARK", 0.0)
    tot = b["all"]["net_total"]
    share = round(100.0 * (tv + gl) / tot, 1) if tot > 0 else None
    top5 = sorted(per.items(), key=lambda kv: -kv[1])[:5]
    print(f"  TVSMOTOR Rs{tv} + GLENMARK Rs{gl} = Rs{round(tv + gl, 2)} "
          f"= {share}% of pooled net (home-alone share was ~97%)")
    print("  top5 per-stock:", top5)
    out["pool50_inv_long"] = {"block": b, "tvsmotor_net": tv, "glenmark_net": gl,
                              "tv_gl_share_pct": share, "top5": top5}
    dump_trade_csv(rows, f"{BASE}/R3_pool50_inv_long_trades.csv")

if __name__ == "__main__":
    out = {"basis": "provisional per 100 shares, net = gross - Rs40/trade",
           "spec": "stocks_R3_frozen.md"}
    if not step_validate_home(out):
        out["stopped"] = "home anchor gate FAILED — ext not scored"
        json.dump(out, open(f"{BASE}/stocks_R3_results.json", "w"), indent=1)
        print("GATE FAILED — stopping per frozen spec.")
        sys.exit(1)
    step_ext(out)
    step_pool50(out)
    json.dump(out, open(f"{BASE}/stocks_R3_results.json", "w"), indent=1)
    print("DONE")
