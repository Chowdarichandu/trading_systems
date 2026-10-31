#!/usr/bin/env python3
"""LINE 4 — Universe Expansion Transfer Test scorer.
Frozen rules VERBATIM (no rule modified):
  (a) DBL-LONG  — machinery copied from stocks_tuning_inv.py (regime maps,
      cond_dbl, p2_filter, build_cell, block) with data-path/cache parameters.
  (b) MORNING-MOVER SECOND SIGNAL — build_chain/replay_plain copied verbatim
      from stocks_tuning_vline.py (mode U5b, cap 2); candidate = premoved
      chains; chain_stats copied with the breadth denominator parametrized.
Modes:
  validate_dbl    ORIGINAL machinery + ORIGINAL universe -> must reproduce
                  Line 1/1b anchors to the paisa before any transfer number
                  is trusted. Also writes universe_old_dbl.json (rows for pooling).
  validate_vline  ORIGINAL vline build_chain + ORIGINAL reentry -> Morning-
                  Mover anchor. Writes universe_old_mm.json (chains for pooling).
  ext_dbl         round8_ext machinery (path/symbol-substituted copies) on the
                  NEW 25. Writes universe_ext_dbl.json + trades CSV.
  ext_vline       reentry_ext + copied build_chain on the NEW 25.
                  Writes universe_ext_mm.json + trades CSV.
  pool50          old + ext rows/chains pooled; P2F pooled from trade CSVs.
Equity cash, LONG/SHORT, paper only, real Rs0. Provisional per 100 shares,
net = gross - Rs40/trade. Window Jan-Oct 2026 (Oct = 1-28).
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

# ================= DBL machinery (from stocks_tuning_inv.py) =================
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

NIFTY_REG = None; STOCK_REG = None

def g1(row):
    r = NIFTY_REG.get(row["date"])
    return bool(r and r["ma50"] is not None and r["prev_close"] > r["ma50"])

def cond_inv1(row):
    return not g1(row)

def cond_dbl(row):
    if not cond_inv1(row):
        return False
    r = STOCK_REG[row["stock"]].get(row["date"])
    return bool(r and r["ma20"] is not None and r["prev_close"] <= r["ma20"])

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

def fmt(b):
    a, jm, jo, oc = b["all"], b["jan_may"], b["jun_oct"], b["october"]
    br = b["breadth"]
    return (f"n={a['trades']} win={a['win_pct']}% netExp=Rs{a['net_exp']} "
            f"| JM net=Rs{jm['net_total']} (n={jm['trades']}) | JO net=Rs{jo['net_total']} (n={jo['trades']}) "
            f"| total=Rs{a['net_total']} | Oct=Rs{oc['net_total']} (n={oc['trades']}) "
            f"| breadth {br['pos_stocks']}, top3 {br['top3_share_pct']}% | PASS={b['pass_gate']}")

def exec_round8(fname):
    ns = {}
    exec(compile(open(f"{BASE}/{fname}").read(), fname, "exec"), ns)
    return ns

def setup_regime(data_dir, symbols):
    global NIFTY_REG, STOCK_REG
    print("building regime maps...", flush=True)
    NIFTY_REG = regime_maps(data_dir, "NIFTY")
    STOCK_REG = {sym: regime_maps(data_dir, sym) for sym in symbols}

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

# ================= validate_dbl =================
def mode_validate_dbl():
    ns = exec_round8("stocks_equity_round8.py")
    setup_regime("progressive", OLD_SYMS)
    cache = f"{BASE}/tuning_universe_cache_val"
    ch = build_cell(ns, cache, "T125_S050")
    p2 = p2_filter(ch)
    inv1 = [r for r in p2 if cond_inv1(r)]
    dbl = [r for r in p2 if cond_dbl(r)]
    dbl_long = [r for r in dbl if r["direction"] == "LONG"]
    out = {"inv1": block(inv1, OLD_SYMS), "dbl_both": block(dbl, OLD_SYMS),
           "dbl_long": block(dbl_long, OLD_SYMS), "dbl_long_rows": dbl_long}
    def chk(name, b, n, net, jm, jo):
        ok = (b["all"]["trades"] == n and abs(b["all"]["net_total"] - net) < 0.01
              and abs(b["jan_may"]["net_total"] - jm) < 0.01
              and abs(b["jun_oct"]["net_total"] - jo) < 0.01)
        print(f"ANCHOR {name}: n {b['all']['trades']} vs {n}, net {b['all']['net_total']} vs {net}, "
              f"JM {b['jan_may']['net_total']} vs {jm}, JO {b['jun_oct']['net_total']} vs {jo} "
              f"-> {'PASS' if ok else 'FAIL'}", flush=True)
        return ok
    ok = chk("INV1", out["inv1"], 694, 22964.30, 7255.01, 15709.29)
    ok &= chk("DBL both-dir", out["dbl_both"], 390, 16548.78, 7861.57, 8687.21)
    ok &= chk("DBL-LONG", out["dbl_long"], 133, 24327.37, 15426.61, 8900.76)
    b = out["dbl_long"]
    ok_oct = abs(b["october"]["net_total"] - 7957.95) < 0.01
    ok_br = b["breadth"]["pos_stocks"] == 10 and abs(b["breadth"]["top3_share_pct"] - 129.0) < 0.05
    print(f"ANCHOR DBL-LONG Oct {b['october']['net_total']} vs 7957.95 -> {'PASS' if ok_oct else 'FAIL'}")
    print(f"ANCHOR DBL-LONG breadth {b['breadth']['pos_stocks']} vs 10, top3 {b['breadth']['top3_share_pct']} vs 129.0 "
          f"-> {'PASS' if ok_br else 'FAIL'}")
    ok = ok and ok_oct and ok_br
    print("VALIDATION DBL ALL PASS:", ok, flush=True)
    json.dump(out, open(f"{BASE}/universe_old_dbl.json", "w"), indent=1)
    dump_trade_csv(dbl_long, f"{BASE}/universe_old_dbl_long_trades.csv")
    return ok

# ================= ext_dbl =================
def mode_ext_dbl():
    ns = exec_round8("stocks_equity_round8_ext.py")
    setup_regime("progressive_ext", EXT_SYMS)
    cache = f"{BASE}/tuning_universe_cache_ext"
    ch = build_cell(ns, cache, "T125_S050")
    p2 = p2_filter(ch)
    inv1 = [r for r in p2 if cond_inv1(r)]
    dbl = [r for r in p2 if cond_dbl(r)]
    dbl_long = [r for r in dbl if r["direction"] == "LONG"]
    out = {"p2_pool": summarize(p2), "inv1": block(inv1, EXT_SYMS),
           "dbl_both": block(dbl, EXT_SYMS), "dbl_long": block(dbl_long, EXT_SYMS),
           "dbl_long_rows": dbl_long}
    print("EXT P2 pool:", fmt({"all": out["p2_pool"], "jan_may": summarize([r for r in p2 if r['date'] < '2026-06-01']),
                              "jun_oct": summarize([r for r in p2 if r['date'] >= '2026-06-01']),
                              "october": summarize([r for r in p2 if r['date'] >= '2026-10-01']),
                              "breadth": breadth(p2, EXT_SYMS), "pass_gate": False}))
    print("EXT INV1 (context):", fmt(out["inv1"]))
    print("EXT DBL both-dir (context):", fmt(out["dbl_both"]))
    print("EXT DBL-LONG (RULE UNDER TEST):", fmt(out["dbl_long"]))
    json.dump(out, open(f"{BASE}/universe_ext_dbl.json", "w"), indent=1)
    dump_trade_csv(dbl_long, f"{BASE}/universe_ext_dbl_long_trades.csv")

# ================= V-line (verbatim copies from stocks_tuning_vline.py) =================
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
            start = idx + 1
            continue
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if mode == "gate":
            tp, sp, leg = 1.25, 0.5, "gate"
        elif mode == "U5a":
            tp, sp, leg = (0.5, 0.35, "probe") if not trades else (1.25, 0.5, "round2")
        else:
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

def metrics(ts):
    if not ts: return {"trades": 0, "net": 0.0, "win_pct": 0.0, "exp": 0.0, "gross_exp": 0.0,
                       "gross": 0.0}
    net = sum(t["net"] for t in ts); wins = sum(1 for t in ts if t["net"] > 0)
    return {"trades": len(ts), "net": round(net, 2), "win_pct": round(100 * wins / len(ts), 1),
            "exp": round(net / len(ts), 2), "gross_exp": round(net / len(ts) + COST, 2),
            "gross": round(net + COST * len(ts), 2)}

def chain_stats(chains, total_stocks=25):
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
    by_stock = collections.defaultdict(float); by_stock_n = collections.defaultdict(int)
    for c in chains:
        if c:
            by_stock[c[0]["symbol"]] += sum(t["net"] for t in c); by_stock_n[c[0]["symbol"]] += 1
    sm = sorted(((round(v, 2), k, by_stock_n[k]) for k, v in by_stock.items()), reverse=True)
    tot = s["all"]["chain_net"]
    s["breadth"] = {"stocks_positive": sum(1 for x in sm if x[0] > 0), "stocks_total": total_stocks,
                    "top3_share_pct": round(100 * sum(x[0] for x in sm[:3]) / tot, 1) if tot > 0 else None,
                    "best5": sm[:5], "worst5": sm[-5:],
                    "per_stock": {k: round(v, 2) for k, v in by_stock.items()}}
    s["pass"] = (s["jan_may"]["chain_net"] > 0 and s["jun_oct"]["chain_net"] > 0
                 and s["breadth"]["stocks_positive"] >= 10)
    return s

def load_reentry_head(fname):
    src = open(f"{BASE}/{fname}").read()
    head = src.split("# ---------- score both modes")[0]
    NS = {}
    exec(compile(head, fname + "_head", "exec"), NS)
    return NS

def mm_chains(NS):
    premoved_chains = []
    for sym in NS["SYMBOLS"]:
        for day in NS["ALL_DAYS"]:
            ts, pm = build_chain(NS, sym, day, "U5b", cap=2)
            if ts and pm:
                premoved_chains.append(ts)
    return premoved_chains

def dump_mm_csv(chains, path):
    flat = [t for c in chains for t in c]
    with open(path, "w", newline="") as f:
        cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time", "entry",
                "exit_time", "exit", "exit_reason", "gross", "net", "event", "premoved"]
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for t in sorted(flat, key=lambda x: (x["date"], x["symbol"], x["round"])):
            w.writerow({c: t.get(c, "") for c in cols})

def mode_validate_vline():
    NS = load_reentry_head("stocks_equity_reentry.py")
    chains = mm_chains(NS)
    s = chain_stats(chains, 25)
    a = s["all"]
    ok = (a["chains"] == 424 and a["trades"] == 698 and abs(a["chain_net"] - 84671.74) < 0.01
          and abs(s["jan_may"]["chain_net"] - 52884.19) < 0.01
          and abs(s["jun_oct"]["chain_net"] - 31787.55) < 0.01
          and abs(s["october"]["chain_net"] - 16825.42) < 0.01
          and s["breadth"]["stocks_positive"] == 16)
    print(f"ANCHOR MORNING-MOVER: chains {a['chains']} vs 424, trades {a['trades']} vs 698, "
          f"net {a['chain_net']} vs 84671.74, JM {s['jan_may']['chain_net']} vs 52884.19, "
          f"JO {s['jun_oct']['chain_net']} vs 31787.55, Oct {s['october']['chain_net']} vs 16825.42, "
          f"breadth {s['breadth']['stocks_positive']} vs 16 -> {'PASS' if ok else 'FAIL'}", flush=True)
    json.dump({"stats": s, "chains": chains}, open(f"{BASE}/universe_old_mm.json", "w"), indent=1)
    dump_mm_csv(chains, f"{BASE}/universe_old_morningmover_trades.csv")
    return ok

def mode_ext_vline():
    NS = load_reentry_head("stocks_equity_reentry_ext.py")
    chains = mm_chains(NS)
    s = chain_stats(chains, 25)
    a = s["all"]
    print(f"EXT MORNING-MOVER (RULE UNDER TEST): chains={a['chains']} trades={a['trades']} "
          f"chainNet=Rs{a['chain_net']} exp/chain=Rs{a['exp_per_chain']} chainWin={a['chain_win_pct']} | "
          f"JM Rs{s['jan_may']['chain_net']} (chains={s['jan_may']['chains']}) | "
          f"JO Rs{s['jun_oct']['chain_net']} (chains={s['jun_oct']['chains']}) | "
          f"Oct Rs{s['october']['chain_net']} | breadth {s['breadth']['stocks_positive']}/25 "
          f"top3 {s['breadth']['top3_share_pct']}% | PASS={s['pass']}", flush=True)
    print(f"  legs: direct+round2 split — withR2 Rs{s['with_round2']['chain_net']} (n={s['with_round2']['chains']}), "
          f"single-trade chains Rs{s['probe_only']['chain_net']} (n={s['probe_only']['chains']})")
    json.dump({"stats": s, "chains": chains}, open(f"{BASE}/universe_ext_mm.json", "w"), indent=1)
    dump_mm_csv(chains, f"{BASE}/universe_ext_morningmover_trades.csv")

# ================= pool50 =================
def p2f_pool():
    def load(path, symcol, netcol):
        rows = []
        if not os.path.exists(path): return rows
        with open(path) as f:
            for r in csv.DictReader(f):
                rows.append({"stock": r[symcol], "date": r["date"], "net": float(r[netcol])})
        return rows
    old = load(f"{BASE}/stock_profiles_P2_ungated_T125_trades.csv", "symbol", "net_rs")
    ext = load(f"{BASE}/universe_ext_profiles_P2_ungated_T125_trades.csv", "symbol", "net_rs")
    return old, ext

def rows_block(rows, symbols):
    return block([{**r, "gross": r["net"] + COST} for r in rows], symbols)

def mode_pool50():
    old_dbl = json.load(open(f"{BASE}/universe_old_dbl.json"))["dbl_long_rows"]
    ext_dbl = json.load(open(f"{BASE}/universe_ext_dbl.json"))["dbl_long_rows"]
    allsyms = OLD_SYMS + EXT_SYMS
    b = block(old_dbl + ext_dbl, allsyms)
    print("POOL50 DBL-LONG:", fmt(b))
    top = sorted(b["breadth"]["per_stock_net"].items(), key=lambda kv: -kv[1])[:5]
    print("  top5 per-stock:", top)
    old_mm = json.load(open(f"{BASE}/universe_old_mm.json"))["chains"]
    ext_mm = json.load(open(f"{BASE}/universe_ext_mm.json"))["chains"]
    s = chain_stats(old_mm + ext_mm, 50)
    a = s["all"]
    print(f"POOL50 MORNING-MOVER: chains={a['chains']} trades={a['trades']} chainNet=Rs{a['chain_net']} "
          f"| JM Rs{s['jan_may']['chain_net']} | JO Rs{s['jun_oct']['chain_net']} | Oct Rs{s['october']['chain_net']} "
          f"| breadth {s['breadth']['stocks_positive']}/50 top3 {s['breadth']['top3_share_pct']}%")
    print("  top5 per-stock:", s["breadth"]["best5"])
    old_p, ext_p = p2f_pool()
    if old_p or ext_p:
        bp = rows_block(old_p + ext_p, allsyms)
        print(f"POOL50 P2F: old {len(old_p)} trades, ext {len(ext_p)} trades")
        print("POOL50 P2F block:", fmt(bp))
        topp = sorted(bp["breadth"]["per_stock_net"].items(), key=lambda kv: -kv[1])[:5]
        print("  top5 per-stock:", topp)
        bo = rows_block(old_p, OLD_SYMS); print("  (old alone):", fmt(bo))
    else:
        print("POOL50 P2F: trade CSVs not found — run profiles first.")
    json.dump({"dbl_long_pool": b}, open(f"{BASE}/universe_pool50_dbl.json", "w"), indent=1)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "validate_dbl": mode_validate_dbl()
    elif mode == "validate_vline": mode_validate_vline()
    elif mode == "ext_dbl": mode_ext_dbl()
    elif mode == "ext_vline": mode_ext_vline()
    elif mode == "pool50": mode_pool50()
    else: print("unknown mode", mode)
