#!/usr/bin/env python3
"""MOVER-A -> A2 TUNING. Spec frozen in stocks_moverA2_frozen.md
BEFORE scoring. Equity cash intraday, LONG/SHORT, paper only, real
Rs0. Provisional per 100 shares, net = gross - Rs40/trade. Window
Jan-Oct 2026 (Oct 1-28).

Machinery: identical to Line 5 (stocks_tuning_mover.py) — signal
stream from the frozen V5 re-entry heads via
stocks_tuning_universe.load_reentry_head, replay_plain +
chain_stats from stocks_tuning_universe.py. build2 is Line 5's
build_batt copied verbatim plus two frozen A2 knobs:
  cap   — chain cap (base 2; A2-1/A2-3 use 1)
  flank — A2-6 asymmetric rule (mover-UP days: same-direction only)
Modes: validate | part1 (A2-1..A2-4) | part2 (A2-5, A2-6) | all
"""
import csv, json, sys, os
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("mover", f"{BASE}/stocks_tuning_mover.py")
M = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["mover"]
spec.loader.exec_module(M)
sys.argv = _argv

U = M.U
COST = 40.0
RESULTS_F = f"{BASE}/stocks_moverA2_results.json"
BASE_NET = 249155.03

def build2(ns, sym, day, threshold=0.01, window_end="10:00",
           same_dir=False, tp=1.25, sp=0.5, cap=2, flank=False):
    """Line 5 build_batt + cap + flank. Returns (trades, pm)."""
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return [], None
    candles = ctx["candles"]
    pm = M.premove(candles, window_end)
    if pm is None or abs(pm) < threshold:
        return [], pm
    move_dir = 1 if pm > 0 else -1
    trades, start, first_done = [], 0, False
    while True:
        if len(trades) >= cap:
            break
        chosen = M.pick(ns, sym, day, ctx, start)
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
        if flank and pm > 0 and sign != move_dir:
            start = idx + 1  # A2-6: mover-UP day, opposite signal consumed
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

_chain_cache = {}
def collect2(which, ckey, **kw):
    if ckey not in _chain_cache:
        ns = M.get_ns(which)
        chains = []
        for sym in ns["SYMBOLS"]:
            for day in ns["ALL_DAYS"]:
                ts, _ = build2(ns, sym, day, **kw)
                if ts:
                    chains.append(ts)
        _chain_cache[ckey] = chains
    return _chain_cache[ckey]

MONTHS = [f"2026-{m:02d}" for m in range(1, 11)]

def month_table(chains):
    months = {m: {"chains": 0, "trades": 0, "net": 0.0} for m in MONTHS}
    for c in chains:
        d = months[c[0]["date"][:7]]
        d["chains"] += 1
        d["trades"] += len(c)
        d["net"] += sum(t["net"] for t in c)
    for m in MONTHS:
        months[m]["net"] = round(months[m]["net"], 2)
    losing = [m for m in MONTHS if months[m]["net"] < 0]
    return months, losing

def summ2(chains, total_stocks):
    s = M.summ(chains, total_stocks)
    months, losing = month_table(chains)
    s["months"] = months
    s["losing_months"] = losing
    s["losing_months_count"] = len(losing)
    return s

def gate(s):
    legs = {"net_beats_base": s["net"] > BASE_NET,
            "jan_may_pos": s["jan_may"]["chain_net"] > 0,
            "jun_oct_pos": s["jun_oct"]["chain_net"] > 0,
            "breadth_ge35": s["breadth"] >= 35,
            "losing_months_le3": s["losing_months_count"] <= 3,
            "october_pos": s["october"]["chain_net"] > 0}
    legs["PASS"] = all(legs.values())
    return legs

def fam_summary(ckey, **kw):
    home = collect2("old", ckey + "_home", **kw)
    ext = collect2("ext", ckey + "_ext", **kw)
    return {"kwargs": {k: v for k, v in kw.items()},
            "home": summ2(home, 25), "ext": summ2(ext, 25),
            "pooled": summ2(home + ext, 50),
            "_chains": (home, ext)}

def public(fs):
    return {k: v for k, v in fs.items() if k != "_chains"}

def fmt(tag, s):
    print(f"{tag}: chains={s['chains']} trades={s['trades']} net={s['net']} "
          f"win={s['chain_win_pct']} exp/chain={s['exp_per_chain']} | "
          f"JM {s['jan_may']['chain_net']} | JO {s['jun_oct']['chain_net']} | "
          f"Oct {s['october']['chain_net']} | breadth {s['breadth']}/{s['stocks_total']} "
          f"top3 {s['top3_share_pct']}% | losing months {s['losing_months']}",
          flush=True)

def dump_csv(tag, chains):
    flat = [t for c in chains for t in c]
    if not flat:
        return
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time",
            "entry", "exit_time", "exit", "exit_reason", "gross", "net",
            "event", "premove_pct"]
    with open(f"{BASE}/moverA2_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(flat, key=lambda x: (x["date"], x["symbol"], x["round"])):
            w.writerow({c: t.get(c, "") for c in cols})

def load_results():
    if os.path.exists(RESULTS_F):
        return json.load(open(RESULTS_F))
    return {}

def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)

def run_family(r, fid, ckey, **kw):
    fs = fam_summary(ckey, **kw)
    g = gate(fs["pooled"])
    fs["gate"] = g
    r[fid] = public(fs)
    save_results(r)
    fmt(f"{fid} POOLED", fs["pooled"])
    fmt(f"{fid} home", fs["home"])
    fmt(f"{fid} ext", fs["ext"])
    print(f"{fid} GATE: {g}", flush=True)
    home, ext = fs["_chains"]
    dump_csv(fid, home + ext)
    return fs

# ---------------- validation ----------------
def mode_validate():
    r = load_results()
    ok = True
    fs = fam_summary("base")
    exp_pool = {"chains": 623, "trades": 998, "net": 249155.03,
                "jm": 126026.74, "jo": 123128.29, "oct": 56809.97,
                "breadth": 38, "top3": 34.1}
    exp_home = {"chains": 424, "trades": 698, "net": 84671.74,
                "jm": 52884.19, "jo": 31787.55, "oct": 16825.42, "breadth": 16}
    exp_ext = {"chains": 199, "trades": 300, "net": 164483.29,
               "jm": 73142.55, "jo": 91340.74, "oct": 39984.55, "breadth": 22}
    for name, s, exp in (("HOME", fs["home"], exp_home),
                         ("EXT", fs["ext"], exp_ext),
                         ("POOLED", fs["pooled"], exp_pool)):
        got = {"chains": s["chains"], "trades": s["trades"], "net": s["net"],
               "jm": s["jan_may"]["chain_net"], "jo": s["jun_oct"]["chain_net"],
               "oct": s["october"]["chain_net"], "breadth": s["breadth"]}
        if "top3" in exp:
            got["top3"] = s["top3_share_pct"]
        good = all(abs(got[k] - v) < 0.01 if isinstance(v, float) else got[k] == v
                   for k, v in exp.items())
        ok &= good
        print(f"ANCHOR {name}: {got} -> {'PASS' if good else 'FAIL vs ' + str(exp)}",
              flush=True)
    # leg anchors at home
    dl, rl = fs["home"]["direct_leg"], fs["home"]["reentry_leg"]
    leg_ok = (dl["trades"] == 424 and abs(dl["net"] - 93575.31) < 0.01
              and rl["trades"] == 274 and abs(rl["net"] - (-8903.57)) < 0.01)
    ok &= leg_ok
    print(f"ANCHOR HOME LEGS: direct {dl['trades']}/{dl['net']} "
          f"reentry {rl['trades']}/{rl['net']} -> {'PASS' if leg_ok else 'FAIL'}",
          flush=True)
    # losing-months anchor (pooled base = Jan, Feb, May)
    lm = fs["pooled"]["losing_months"]
    lm_ok = lm == ["2026-01", "2026-02", "2026-05"]
    ok &= lm_ok
    print(f"ANCHOR POOLED LOSING MONTHS: {lm} -> {'PASS' if lm_ok else 'FAIL'}",
          flush=True)
    # field-by-field diff vs published Line 5 dumps
    keys = ["date", "symbol", "dir", "leg", "round", "entry_time", "entry",
            "exit_time", "exit", "exit_reason", "gross", "net"]
    home, ext = fs["_chains"]
    for label, chains, fname in (("HOME", home, "mover_A_old_trades.csv"),
                                 ("EXT", ext, "mover_A_ext_trades.csv")):
        mine = sorted(tuple(str(t[k]) for k in keys) for c in chains for t in c)
        ref = []
        with open(f"{BASE}/{fname}") as f:
            for row in csv.DictReader(f):
                ref.append(tuple(str(row[k]) for k in keys))
        same = sorted(ref) == mine
        ok &= same
        print(f"DUMP DIFF {label} vs {fname}: {len(mine)} rows -> "
              f"{'IDENTICAL' if same else 'MISMATCH'}", flush=True)
    r["VALIDATE"] = {"pass": bool(ok), "base": public(fs)}
    save_results(r)
    print("VALIDATION ALL PASS:", ok, flush=True)
    return ok

# ---------------- families ----------------
FAM14 = [("A2-1", "a21", dict(cap=1)),
         ("A2-2", "a22", dict(same_dir=True)),
         ("A2-3", "a23", dict(cap=1, same_dir=True)),
         ("A2-4a", "a24a", dict(window_end="10:05")),
         ("A2-4b", "a24b", dict(window_end="10:10"))]

def mode_part1():
    r = load_results()
    for fid, ckey, kw in FAM14:
        run_family(r, fid, ckey, **kw)
    print("PART1 DONE", flush=True)

def best_of_14(r):
    cands = []
    for fid, _, _ in FAM14:
        s = r[fid]["pooled"]
        cands.append((s["net"], s["breadth"], -FAM14.index((fid, _, _)) if False else 0, fid))
    # rank: net desc, breadth desc, family order asc
    order = {fid: i for i, (fid, _, _) in enumerate(FAM14)}
    ranked = sorted(((r[fid]["pooled"]["net"], r[fid]["pooled"]["breadth"],
                      -order[fid], fid) for fid, _, _ in FAM14), reverse=True)
    return ranked[0][3], ranked

def mode_part2():
    r = load_results()
    best_fid, ranked = best_of_14(r)
    best_kw = dict(r[best_fid]["kwargs"])
    # JSON may have stringified nothing (kwargs are plain) — window_end stays str
    r["A2-5_BASIS"] = {"best_family": best_fid, "best_kwargs": best_kw,
                       "ranking": [[f, n, b] for n, b, _, f in ranked]}
    save_results(r)
    print(f"A2-5 basis: best of A2-1..4 = {best_fid} kwargs={best_kw}", flush=True)
    kw_a = dict(best_kw); kw_a.update(tp=1.5, sp=0.5)
    run_family(r, "A2-5a", "a25a", **kw_a)
    kw_b = dict(best_kw); kw_b.update(tp=1.25, sp=0.65)
    run_family(r, "A2-5b", "a25b", **kw_b)
    run_family(r, "A2-6", "a26", flank=True)
    print("PART2 DONE", flush=True)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True); sys.exit(1)
    elif mode == "part1":
        mode_part1()
    elif mode == "part2":
        mode_part2()
    elif mode == "all":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True); sys.exit(1)
        mode_part1(); mode_part2()
    else:
        print("unknown mode", mode); sys.exit(1)
    print("DONE", mode, flush=True)
