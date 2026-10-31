#!/usr/bin/env python3
"""LINE 2b — robustness battery on the frozen v2 candidate
(morning-mover second signal). DIAGNOSTIC ONLY — no pass may be
claimed from this battery. Spec: stocks_tuning_vline_frozen.md
Line 2b section (frozen BEFORE scoring). Equity cash intraday,
LONG/SHORT, paper only, real Rs0. Per 100 shares provisional,
Rs40/trade flat unless a cell states another cost (R6).

Chain mechanics replicate stocks_tuning_vline.py build_chain
mode 'U5b' for qualifying days exactly: signals from the frozen
V5 re-entry stream (pool_pick over v4_head/skor_head), first
signal of the day discarded, subsequent signals traded at T125
(target +1.25% / stop -0.5%, replay_plain), entry = next bar's
open, next search starts at the previous exit bar (or signal
bar + 1 after a discard/block), chain cap 2 trades.

Modes: validate | all
"""
import csv, importlib.util, json, sys
from collections import defaultdict

OUT = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("vline", f"{OUT}/stocks_tuning_vline.py")
V = importlib.util.module_from_spec(spec)
_sysargv = sys.argv
sys.argv = ["vline2b"]
spec.loader.exec_module(V)
sys.argv = _sysargv

NS = V._load_reentry()
COST = 40.0
RESULTS_F = f"{OUT}/stocks_tuning_vline2b_results.json"

_pick_cache = {}
def pick(sym, day, ctx, start):
    key = (sym, day, start)
    if key not in _pick_cache:
        _pick_cache[key] = NS["pool_pick"](ctx, NS["v4_head"](ctx, start),
                                           NS["skor_head"](ctx, start))
    return _pick_cache[key]

def premove(candles, window_end):
    day_open = candles[0]["open"]
    pre = [c for c in candles if c["time"] < window_end]
    if not pre or not day_open:
        return None
    return pre[-1]["close"] / day_open - 1

def build_batt(sym, day, threshold=0.01, window_end="10:00",
               dirmode=0, same_dir=False):
    """Returns (trades, premove_signed). Non-qualifying day -> ([], pm)."""
    ctx = NS["DAYCTX"].get((sym, day))
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
        chosen = pick(sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        if not first_done:
            first_done = True
            start = idx + 1  # discard first signal entirely (no trade, no cost)
            continue
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if dirmode != 0 and sign != dirmode:
            start = idx + 1  # blocked direction: consumed, no entry/cost/cap
            continue
        if same_dir and sign != move_dir:
            start = idx + 1  # R5a: only signals aligned with the pre-move
            continue
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        er, ep, et, exit_idx, gross = V.replay_plain(
            candles, entry_idx, sign, entry, 1.25, 0.5)
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

def collect(**kw):
    chains = []
    for sym in NS["SYMBOLS"]:
        for day in NS["ALL_DAYS"]:
            ts, _ = build_batt(sym, day, **kw)
            if ts:
                chains.append(ts)
    return chains

def half_of(date):
    return "jan_may" if date <= "2026-05-31" else "jun_oct"

def block_summary(chains):
    s = V.chain_stats(chains)
    out = {"chains": s["all"]["chains"], "trades": s["all"]["trades"],
           "net": s["all"]["chain_net"], "chain_win_pct": s["all"]["chain_win_pct"],
           "exp_per_chain": s["all"]["exp_per_chain"],
           "jan_may": s["jan_may"], "jun_oct": s["jun_oct"],
           "october": s["october"],
           "breadth": s["breadth"]["stocks_positive"],
           "top3_share_pct": s["breadth"]["top3_share_pct"],
           "per_stock": s["breadth"]["per_stock"],
           "best5": s["breadth"]["best5"], "worst5": s["breadth"]["worst5"]}
    flat = [t for c in chains for t in c]
    direct = [t for t in flat if t["leg"] == "direct"]
    reent = [t for t in flat if t["leg"] == "round2"]
    out["direct_leg"] = V.metrics(direct)
    out["reentry_leg"] = V.metrics(reent)
    out["long"] = V.metrics([t for t in flat if t["dir"] == "LONG"])
    out["short"] = V.metrics([t for t in flat if t["dir"] == "SHORT"])
    return out

def save_chains_csv(fid, chains):
    flat = [t for c in chains for t in c]
    if not flat:
        return
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time",
            "entry", "exit_time", "exit", "exit_reason", "gross", "net",
            "event", "premove_pct"]
    with open(f"{OUT}/vline2b_{fid}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(flat, key=lambda x: (x["date"], x["symbol"], x["round"])):
            w.writerow({c: t.get(c, "") for c in cols})

def fmt(tag, s):
    print(f"{tag}: chains={s['chains']} trades={s['trades']} net={s['net']} "
          f"win={s['chain_win_pct']} exp/chain={s['exp_per_chain']} | "
          f"JM {s['jan_may']['chain_net']} (ch={s['jan_may']['chains']}) | "
          f"JO {s['jun_oct']['chain_net']} (ch={s['jun_oct']['chains']}) | "
          f"Oct {s['october']['chain_net']} | breadth {s['breadth']}/25",
          flush=True)

def do_validate(results):
    chains = collect()
    s = block_summary(chains)
    exp = {"chains": 424, "trades": 698, "net": 84671.74,
           "jm": 52884.19, "jm_ch": 272, "jo": 31787.55, "jo_ch": 152,
           "oct": 16825.42, "win": 55.0, "breadth": 16,
           "direct_n": 424, "direct_net": 93575.31,
           "reent_n": 274, "reent_net": -8903.57}
    got = {"chains": s["chains"], "trades": s["trades"], "net": s["net"],
           "jm": s["jan_may"]["chain_net"], "jm_ch": s["jan_may"]["chains"],
           "jo": s["jun_oct"]["chain_net"], "jo_ch": s["jun_oct"]["chains"],
           "oct": s["october"]["chain_net"], "win": s["chain_win_pct"],
           "breadth": s["breadth"],
           "direct_n": s["direct_leg"]["trades"],
           "direct_net": s["direct_leg"]["net"],
           "reent_n": s["reentry_leg"]["trades"],
           "reent_net": s["reentry_leg"]["net"]}
    ok = all(abs(got[k] - exp[k]) < 0.01 if isinstance(exp[k], float)
             else got[k] == exp[k] for k in exp)
    print(f"VALIDATE frozen config: {got} -> {'PASS' if ok else 'FAIL'}",
          flush=True)
    results["VALIDATE"] = {"pass": ok, "got": got, "expected": exp}
    results["FROZEN"] = s
    json.dump(results, open(RESULTS_F, "w"), indent=1)
    save_chains_csv("FROZEN", chains)
    return chains, s, ok

def do_battery(results, frozen_chains, frozen_sum):
    # ---- R1 threshold neighbourhood
    r1 = {}
    for thr, tag in ((0.0075, "T075"), (0.0125, "T125"), (0.0150, "T150")):
        ch = collect(threshold=thr)
        s = block_summary(ch)
        r1[tag] = s
        fmt(f"R1-{tag} (thr {thr:.2%})", s)
        save_chains_csv(f"R1-{tag}", ch)
    r1["T100_frozen"] = frozen_sum
    results["R1"] = r1

    # ---- R2 direction split
    ch_long = collect(dirmode=1)
    s_long = block_summary(ch_long)
    fmt("R2-LONGONLY", s_long)
    save_chains_csv("R2-LONG", ch_long)
    ch_short = collect(dirmode=-1)
    s_short = block_summary(ch_short)
    fmt("R2-SHORTONLY", s_short)
    save_chains_csv("R2-SHORT", ch_short)
    up = [c for c in frozen_chains if c[0]["premove_pct"] > 0]
    dn = [c for c in frozen_chains if c[0]["premove_pct"] < 0]
    results["R2"] = {"long_only": s_long, "short_only": s_short,
                     "frozen_trade_level_long": frozen_sum["long"],
                     "frozen_trade_level_short": frozen_sum["short"],
                     "mover_up": block_summary(up),
                     "mover_down": block_summary(dn)}
    fmt("R2-MOVERUP", results["R2"]["mover_up"])
    fmt("R2-MOVERDOWN", results["R2"]["mover_down"])

    # ---- R3 concentration on frozen chains
    per_stock = frozen_sum["per_stock"]
    ranked = sorted(per_stock.items(), key=lambda kv: kv[1], reverse=True)
    top3 = [k for k, _ in ranked[:3]]
    top3_net = round(sum(per_stock[k] for k in top3), 2)
    total = frozen_sum["net"]
    excl = {"total": round(total - top3_net, 2)}
    for half in ("jan_may", "jun_oct"):
        hsum = 0.0
        for c in frozen_chains:
            if half_of(c[0]["date"]) == half and c[0]["symbol"] not in top3:
                hsum += sum(t["net"] for t in c)
        excl[half] = round(hsum, 2)
    winsor = round(sum(min(v, 2000.0) for v in per_stock.values()), 2)
    months = {}
    for c in frozen_chains:
        m = c[0]["date"][:7]
        d = months.setdefault(m, {"chains": 0, "trades": 0, "net": 0.0})
        d["chains"] += 1
        d["trades"] += len(c)
        d["net"] += sum(t["net"] for t in c)
    cum = 0.0
    for m in sorted(months):
        months[m]["net"] = round(months[m]["net"], 2)
        cum += months[m]["net"]
        months[m]["cum_net"] = round(cum, 2)
    worst_month = min(months.items(), key=lambda kv: kv[1]["net"])
    results["R3"] = {"per_stock_ranked": [(k, v) for k, v in ranked],
                     "top3": top3, "top3_net": top3_net,
                     "top3_share_pct": round(100 * top3_net / total, 1),
                     "excluding_top3": excl,
                     "winsorised_2000_total": winsor,
                     "months": months,
                     "worst_month": [worst_month[0], worst_month[1]["net"]]}
    print(f"R3: top3 {top3} net {top3_net} ({results['R3']['top3_share_pct']}%) | "
          f"excl-top3 total {excl['total']} JM {excl['jan_may']} JO {excl['jun_oct']} | "
          f"winsorised {winsor} | worst month {worst_month[0]} {worst_month[1]['net']}",
          flush=True)

    # ---- R4 time neighbourhood
    r4 = {"10:00_frozen": frozen_sum}
    for we, tag in (("09:45", "W0945"), ("10:15", "W1015")):
        ch = collect(window_end=we)
        s = block_summary(ch)
        r4[tag] = s
        fmt(f"R4-{tag} (window < {we})", s)
        save_chains_csv(f"R4-{tag}", ch)
    results["R4"] = r4

    # ---- R5 same-direction variant (frozen base = ANY direction)
    ch_sd = collect(same_dir=True)
    s_sd = block_summary(ch_sd)
    results["R5"] = {"frozen_definition": "ANY direction (engine build_chain "
                     "applies no direction filter after the discard)",
                     "same_direction": s_sd, "any_direction_frozen": frozen_sum}
    fmt("R5a-SAMEDIR", s_sd)
    save_chains_csv("R5a-SAMEDIR", ch_sd)

    # ---- R6 cost sensitivity on the frozen rule
    flat = [t for c in frozen_chains for t in c]
    def at(cost, subset):
        g = sum(t["gross"] for t in subset)
        return round(g - cost * len(subset), 2)
    jm = [t for t in flat if t["date"] <= "2026-05-31"]
    jo = [t for t in flat if t["date"] >= "2026-06-01"]
    oc = [t for t in flat if t["date"] >= "2026-10-01"]
    gross_all = sum(t["gross"] for t in flat)
    results["R6"] = {
        "trades": len(flat),
        "at_25": {"total": at(25.0, flat), "jan_may": at(25.0, jm),
                  "jun_oct": at(25.0, jo), "october": at(25.0, oc)},
        "at_40_frozen": {"total": at(40.0, flat), "jan_may": at(40.0, jm),
                         "jun_oct": at(40.0, jo), "october": at(40.0, oc)},
        "at_60": {"total": at(60.0, flat), "jan_may": at(60.0, jm),
                  "jun_oct": at(60.0, jo), "october": at(60.0, oc)},
        "breakeven_cost": round(gross_all / len(flat), 2),
        "breakeven_jm": round(sum(t["gross"] for t in jm) / len(jm), 2),
        "breakeven_jo": round(sum(t["gross"] for t in jo) / len(jo), 2)}
    print(f"R6: at25 {results['R6']['at_25']} | at60 {results['R6']['at_60']} | "
          f"breakeven {results['R6']['breakeven_cost']} "
          f"(JM {results['R6']['breakeven_jm']} / JO {results['R6']['breakeven_jo']})",
          flush=True)
    json.dump(results, open(RESULTS_F, "w"), indent=1)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    results = {}
    chains, s, ok = do_validate(results)
    if not ok:
        print("VALIDATION FAILED — battery aborted.", flush=True)
        sys.exit(1)
    if mode == "all":
        do_battery(results, chains, s)
    print("DONE", flush=True)
