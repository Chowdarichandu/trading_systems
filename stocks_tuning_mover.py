#!/usr/bin/env python3
"""LINE 5 — Morning-Mover deepening on the EXTENDED universe + pooled 50.
DIAGNOSTICS ONLY — observations on in-sample data; no pass claims, no
rule changes. Spec frozen in stocks_tuning_mover_frozen.md BEFORE
scoring. Equity cash, LONG/SHORT, paper only, real Rs0. Provisional
per 100 shares, net = gross - Rs40/trade. Window Jan-Oct 2026
(Oct = 1-28).

Machinery: signal stream from the frozen V5 re-entry heads (home:
stocks_equity_reentry.py; ext: stocks_equity_reentry_ext.py) loaded
via stocks_tuning_universe.load_reentry_head; chain builder is the
Line 2b parametrized build_batt (threshold / window_end / same_dir /
exit target) with replay_plain + chain_stats from
stocks_tuning_universe.py.

Modes: validate | m1 | m2 | m3 | m4 | m5 | m6 | all
"""
import csv, json, sys, collections, os
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("univ", f"{BASE}/stocks_tuning_universe.py")
U = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["univ"]
spec.loader.exec_module(U)
sys.argv = _argv

COST = 40.0
RESULTS_F = f"{BASE}/stocks_tuning_mover_results.json"

_NS_CACHE = {}
def get_ns(which):
    if which not in _NS_CACHE:
        fname = "stocks_equity_reentry.py" if which == "old" else "stocks_equity_reentry_ext.py"
        _NS_CACHE[which] = U.load_reentry_head(fname)
    return _NS_CACHE[which]

_pick_cache = {}
def pick(ns, sym, day, ctx, start):
    key = (id(ns), sym, day, start)
    if key not in _pick_cache:
        _pick_cache[key] = ns["pool_pick"](ctx, ns["v4_head"](ctx, start),
                                           ns["skor_head"](ctx, start))
    return _pick_cache[key]

def premove(candles, window_end):
    day_open = candles[0]["open"]
    pre = [c for c in candles if c["time"] < window_end]
    if not pre or not day_open:
        return None
    return pre[-1]["close"] / day_open - 1

def build_batt(ns, sym, day, threshold=0.01, window_end="10:00",
               same_dir=False, tp=1.25, sp=0.5):
    """Chain builder identical to Line 2b build_batt, NS-parametrized,
    plus an exit-target parameter (M6). Returns (trades, pm)."""
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return [], None
    candles = ctx["candles"]
    pm = premove(candles, window_end)
    if pm is None or abs(pm) < threshold:
        return [], pm
    move_dir = 1 if pm > 0 else -1
    trades, start, first_done = [], 0, False
    while True:
        if len(trades) >= 2:
            break
        chosen = pick(ns, sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        if not first_done:
            first_done = True
            start = idx + 1
            continue
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if same_dir and sign != move_dir:
            start = idx + 1
            continue
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        er, ep, et, exit_idx, gross = U.replay_plain(
            candles, entry_idx, sign, entry, tp, sp)
        trades.append({"date": day, "symbol": sym, "dir": direction,
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 3)})
        start = exit_idx
    return trades, pm

def collect(which, **kw):
    ns = get_ns(which)
    chains = []
    for sym in ns["SYMBOLS"]:
        for day in ns["ALL_DAYS"]:
            ts, _ = build_batt(ns, sym, day, **kw)
            if ts:
                chains.append(ts)
    return chains

def load_results():
    if os.path.exists(RESULTS_F):
        return json.load(open(RESULTS_F))
    return {}

def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)

def summ(chains, total_stocks):
    s = U.chain_stats(chains, total_stocks)
    flat = [t for c in chains for t in c]
    return {"chains": s["all"]["chains"], "trades": s["all"]["trades"],
            "net": s["all"]["chain_net"],
            "chain_win_pct": s["all"]["chain_win_pct"],
            "exp_per_chain": s["all"]["exp_per_chain"],
            "jan_may": s["jan_may"], "jun_oct": s["jun_oct"],
            "october": s["october"],
            "breadth": s["breadth"]["stocks_positive"],
            "stocks_total": total_stocks,
            "top3_share_pct": s["breadth"]["top3_share_pct"],
            "per_stock": s["breadth"]["per_stock"],
            "best5": s["breadth"]["best5"], "worst5": s["breadth"]["worst5"],
            "direct_leg": U.metrics([t for t in flat if t["leg"] == "direct"]),
            "reentry_leg": U.metrics([t for t in flat if t["leg"] == "round2"])}

def dump_csv(tag, chains):
    flat = [t for c in chains for t in c]
    if not flat:
        return
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time",
            "entry", "exit_time", "exit", "exit_reason", "gross", "net",
            "event", "premove_pct"]
    with open(f"{BASE}/mover_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(flat, key=lambda x: (x["date"], x["symbol"], x["round"])):
            w.writerow({c: t.get(c, "") for c in cols})

def fmt(tag, s):
    print(f"{tag}: chains={s['chains']} trades={s['trades']} net={s['net']} "
          f"win={s['chain_win_pct']} exp/chain={s['exp_per_chain']} | "
          f"JM {s['jan_may']['chain_net']} (ch={s['jan_may']['chains']}) | "
          f"JO {s['jun_oct']['chain_net']} (ch={s['jun_oct']['chains']}) | "
          f"Oct {s['october']['chain_net']} | breadth {s['breadth']}/{s['stocks_total']} "
          f"top3 {s['top3_share_pct']}%", flush=True)

def chk(name, got, exp):
    ok = all(abs(got[k] - v) < 0.01 if isinstance(v, float) else got[k] == v
             for k, v in exp.items())
    print(f"ANCHOR {name}: {got} -> {'PASS' if ok else 'FAIL vs ' + str(exp)}", flush=True)
    return ok

def core(s):
    return {"chains": s["chains"], "trades": s["trades"], "net": s["net"],
            "jm": s["jan_may"]["chain_net"], "jo": s["jun_oct"]["chain_net"],
            "oct": s["october"]["chain_net"], "breadth": s["breadth"]}

_cache_chains = {}
def get_chains(key, which, **kw):
    if key not in _cache_chains:
        _cache_chains[key] = collect(which, **kw)
    return _cache_chains[key]

def mode_validate():
    r = load_results()
    ok = True
    oldA = get_chains("oldA", "old")
    s_oldA = summ(oldA, 25); fmt("HOME MOVER-A", s_oldA)
    ok &= chk("HOME-A", core(s_oldA), {"chains": 424, "trades": 698, "net": 84671.74,
              "jm": 52884.19, "jo": 31787.55, "oct": 16825.42, "breadth": 16})
    extA = get_chains("extA", "ext")
    s_extA = summ(extA, 25); fmt("EXT MOVER-A", s_extA)
    ok &= chk("EXT-A", core(s_extA), {"chains": 199, "trades": 300, "net": 164483.29,
              "jm": 73142.55, "jo": 91340.74, "oct": 39984.55, "breadth": 22})
    s_poolA = summ(oldA + extA, 50); fmt("POOL50 MOVER-A", s_poolA)
    ok &= chk("POOL-A", {**core(s_poolA), "top3": s_poolA["top3_share_pct"]},
              {"chains": 623, "trades": 998, "net": 249155.03, "jm": 126026.74,
               "jo": 123128.29, "oct": 56809.97, "breadth": 38, "top3": 34.1})
    oldB = get_chains("oldB", "old", window_end="10:15")
    s_oldB = summ(oldB, 25); fmt("HOME MOVER-B(10:15)", s_oldB)
    ok &= chk("HOME-B", core(s_oldB), {"chains": 589, "trades": 941, "net": 169328.31,
              "jm": 92266.39, "jo": 77061.92, "oct": 36815.02, "breadth": 24})
    oldSD = get_chains("oldSD", "old", same_dir=True)
    s_oldSD = summ(oldSD, 25); fmt("HOME SAME-DIR", s_oldSD)
    ok &= chk("HOME-SD", core(s_oldSD), {"chains": 385, "trades": 639, "net": 92923.38,
              "jm": 58622.78, "jo": 34300.60, "oct": 16885.05, "breadth": 18})
    dn = [c for c in oldA if c[0]["premove_pct"] < 0]
    s_dn = summ(dn, 25); fmt("HOME MOVER-DOWN partition", s_dn)
    ok &= chk("HOME-DOWN", core(s_dn), {"chains": 221, "net": 58812.88,
              "jm": 30199.64, "jo": 28613.24, "oct": 14421.94, "breadth": 19})
    r["VALIDATE"] = {"pass": bool(ok), "homeA": s_oldA, "extA": s_extA,
                     "poolA": s_poolA, "homeB": s_oldB, "homeSD": s_oldSD,
                     "homeDown": s_dn}
    save_results(r)
    dump_csv("A_old", oldA); dump_csv("A_ext", extA)
    print("VALIDATION ALL PASS:", ok, flush=True)
    return ok

def mode_m1():
    r = load_results()
    extB = get_chains("extB", "ext", window_end="10:15")
    s_extB = summ(extB, 25); fmt("M1 EXT MOVER-B(10:15)", s_extB)
    oldB = get_chains("oldB", "old", window_end="10:15")
    s_poolB = summ(oldB + extB, 50); fmt("M1 POOL50 MOVER-B(10:15)", s_poolB)
    r["M1"] = {"extB": s_extB, "poolB": s_poolB,
               "homeB_ref": r.get("VALIDATE", {}).get("homeB"),
               "extA_ref": r.get("VALIDATE", {}).get("extA"),
               "poolA_ref": r.get("VALIDATE", {}).get("poolA")}
    save_results(r)
    dump_csv("M1_extB", extB); dump_csv("M1_poolB", oldB + extB)

def mode_m2():
    r = load_results()
    out = {}
    for thr, tag in ((0.0075, "T075"), (0.01, "T100"), (0.0125, "T125"), (0.015, "T150")):
        key = "extA" if thr == 0.01 else f"extM2{tag}"
        ch = get_chains(key, "ext", threshold=thr)
        s = summ(ch, 25); fmt(f"M2 EXT thr={thr:.2%}", s)
        out[tag] = s
        if thr != 0.01:
            dump_csv(f"M2_{tag}", ch)
    r["M2"] = out
    save_results(r)

def mode_m3():
    r = load_results()
    extSD = get_chains("extSD", "ext", same_dir=True)
    s = summ(extSD, 25); fmt("M3 EXT SAME-DIR", s)
    r["M3"] = {"ext_same_dir": s, "extA_ref": r.get("VALIDATE", {}).get("extA"),
               "homeSD_ref": r.get("VALIDATE", {}).get("homeSD")}
    save_results(r)
    dump_csv("M3_extSD", extSD)

def mode_m4():
    r = load_results()
    oldA = get_chains("oldA", "old"); extA = get_chains("extA", "ext")
    pool = oldA + extA
    dn = [c for c in pool if c[0]["premove_pct"] < 0]
    up = [c for c in pool if c[0]["premove_pct"] > 0]
    s_dn = summ(dn, 50); fmt("M4 POOL50 MOVER-DOWN only", s_dn)
    s_up = summ(up, 50); fmt("M4 POOL50 MOVER-UP only (context)", s_up)
    tot = r.get("VALIDATE", {}).get("poolA", {}).get("net")
    if tot:
        s_dn = {**s_dn, "share_of_pool_net_pct": round(100 * s_dn["net"] / tot, 1)}
        s_up = {**s_up, "share_of_pool_net_pct": round(100 * s_up["net"] / tot, 1)}
    r["M4"] = {"mover_down": s_dn, "mover_up_context": s_up}
    save_results(r)
    dump_csv("M4_poolDown", dn)

def mode_m5():
    r = load_results()
    oldA = get_chains("oldA", "old"); extA = get_chains("extA", "ext")
    pool = oldA + extA
    months = {}
    for c in pool:
        m = c[0]["date"][:7]
        d = months.setdefault(m, {"chains": 0, "trades": 0, "net": 0.0})
        d["chains"] += 1; d["trades"] += len(c)
        d["net"] += sum(t["net"] for t in c)
    cum = 0.0
    for m in sorted(months):
        months[m]["net"] = round(months[m]["net"], 2)
        cum += months[m]["net"]
        months[m]["cum_net"] = round(cum, 2)
    total = round(cum, 2)
    ranked = sorted(months.items(), key=lambda kv: kv[1]["net"], reverse=True)
    worst = min(months.items(), key=lambda kv: kv[1]["net"])
    top2 = ranked[:2]
    top2_net = round(sum(v["net"] for _, v in top2), 2)
    r["M5"] = {"months": months, "total": total,
               "worst_month": [worst[0], worst[1]["net"]],
               "top2_months": [[m, v["net"]] for m, v in top2],
               "top2_net": top2_net,
               "top2_share_pct": round(100 * top2_net / total, 1) if total > 0 else None}
    save_results(r)
    for m in sorted(months):
        d = months[m]
        print(f"M5 {m}: chains={d['chains']} trades={d['trades']} net={d['net']} cum={d['cum_net']}", flush=True)
    print(f"M5 worst={worst[0]} {worst[1]['net']} | top2={r['M5']['top2_months']} "
          f"share={r['M5']['top2_share_pct']}%", flush=True)

def mode_m6():
    r = load_results()
    oldT10 = get_chains("oldT10", "old", tp=1.0)
    extT10 = get_chains("extT10", "ext", tp=1.0)
    s_t10 = summ(oldT10 + extT10, 50); fmt("M6 POOL50 MOVER-A @T10", s_t10)
    s_old10 = summ(oldT10, 25); fmt("M6 HOME @T10 (context)", s_old10)
    s_ext10 = summ(extT10, 25); fmt("M6 EXT @T10 (context)", s_ext10)
    r["M6"] = {"pool_T10": s_t10, "home_T10_context": s_old10,
               "ext_T10_context": s_ext10,
               "pool_T125_ref": r.get("VALIDATE", {}).get("poolA")}
    save_results(r)
    dump_csv("M6_poolT10", oldT10 + extT10)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True); sys.exit(1)
    elif mode == "m1": mode_m1()
    elif mode == "m2": mode_m2()
    elif mode == "m3": mode_m3()
    elif mode == "m4": mode_m4()
    elif mode == "m5": mode_m5()
    elif mode == "m6": mode_m6()
    elif mode == "all":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True); sys.exit(1)
        mode_m1(); mode_m2(); mode_m3(); mode_m4(); mode_m5(); mode_m6()
    else:
        print("unknown mode", mode); sys.exit(1)
    print("DONE", mode, flush=True)
