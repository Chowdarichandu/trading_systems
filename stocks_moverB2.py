#!/usr/bin/env python3
"""MOVER-B2 tuning — families frozen in stocks_moverB2_frozen.md BEFORE
scoring. Equity cash, LONG/SHORT, paper only, real Rs0. Provisional
per 100 shares, net = gross - Rs40/trade. Window Jan-Oct 2026.

Machinery: Line 5 build_batt logic (stocks_tuning_mover.py) with an
added chain-cap parameter. Signal stream = frozen V5 re-entry heads.
Modes: validate | b21 | b22 | b23 | b24a | b24b | b25a | b25b | b26
"""
import csv, json, os, sys
from collections import defaultdict
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
RESULTS_F = f"{BASE}/stocks_moverB2_results.json"

MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]


def build(ns, sym, day, threshold=0.01, window_end="10:15",
          same_dir=False, tp=1.25, sp=0.5, cap=2):
    """Line 5 build_batt + chain-cap parameter. Identical semantics."""
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
    ns = M.get_ns(which)
    chains = []
    for sym in ns["SYMBOLS"]:
        for day in ns["ALL_DAYS"]:
            ts, _ = build(ns, sym, day, **kw)
            if ts:
                chains.append(ts)
    return chains


def months_of(chains):
    out = {}
    for m in MONTHS:
        sel = [c for c in chains if c[0]["date"][:7] == m]
        out[m] = {"chains": len(sel), "trades": sum(len(c) for c in sel),
                  "net": round(sum(t["net"] for c in sel for t in c), 2)}
    return out


def max_dd(chains):
    daily = defaultdict(float)
    for c in chains:
        for t in c:
            daily[t["date"]] += t["net"]
    cum = peak = dd = 0.0
    for d in sorted(daily):
        cum += daily[d]
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return round(dd, 2)


def enrich(chains, total_stocks):
    s = M.summ(chains, total_stocks)
    mo = months_of(chains)
    s["months"] = mo
    s["losing_months"] = [m for m in MONTHS if mo[m]["net"] < 0]
    s["max_dd"] = max_dd(chains)
    return s


def run_config(cfg):
    home = collect("old", **cfg)
    ext = collect("ext", **cfg)
    return home, ext, {"home": enrich(home, 25), "ext": enrich(ext, 25),
                       "pooled": enrich(home + ext, 50)}


def dump(tag, chains):
    flat = [t for c in chains for t in c]
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time",
            "entry", "exit_time", "exit", "exit_reason", "gross", "net",
            "event", "premove_pct"]
    with open(f"{BASE}/moverB2_{tag}_trades.csv", "w", newline="") as f:
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


def fmt(tag, s):
    p = s["pooled"]
    print(f"{tag}: pooled chains={p['chains']} trades={p['trades']} net={p['net']} "
          f"exp/ch={p['exp_per_chain']} JM={p['jan_may']['chain_net']} "
          f"JO={p['jun_oct']['chain_net']} Oct={p['october']['chain_net']} "
          f"breadth={p['breadth']}/50 top3={p['top3_share_pct']}% "
          f"losing={p['losing_months']} maxDD={p['max_dd']} | "
          f"home net={s['home']['net']} br={s['home']['breadth']}/25 | "
          f"ext net={s['ext']['net']} br={s['ext']['breadth']}/25", flush=True)


def gate(pooled):
    return {"net_gt_base": pooled["net"] > 464617.03,
            "both_halves_positive": pooled["jan_may"]["chain_net"] > 0
                                    and pooled["jun_oct"]["chain_net"] > 0,
            "breadth_ge_45": pooled["breadth"] >= 45,
            "max_dd_ok": pooled["max_dd"] >= -25000.0,
            "no_losing_month": not pooled["losing_months"]}


def gate_pass(g):
    return all(g.values())


BASE_CFG = {"threshold": 0.01, "window_end": "10:15", "same_dir": False,
            "tp": 1.25, "sp": 0.5, "cap": 2}

CELLS = {
    "B2-1": {"label": "DIRECT-ONLY (cap 1)", "cfg": {**BASE_CFG, "cap": 1}},
    "B2-2": {"label": "SAME-DIRECTION (cap 2)", "cfg": {**BASE_CFG, "same_dir": True}},
    "B2-3": {"label": "COMBINED (cap 1 + same-direction)",
             "cfg": {**BASE_CFG, "cap": 1, "same_dir": True}},
    "B2-4a": {"label": "MEASUREMENT 10:20", "cfg": {**BASE_CFG, "window_end": "10:20"}},
    "B2-4b": {"label": "MEASUREMENT 10:30", "cfg": {**BASE_CFG, "window_end": "10:30"}},
    "B2-5a": {"label": "THRESHOLD 0.75%", "cfg": {**BASE_CFG, "threshold": 0.0075}},
    "B2-5b": {"label": "THRESHOLD 1.25%", "cfg": {**BASE_CFG, "threshold": 0.0125}},
}
ORDER = ["B2-1", "B2-2", "B2-3", "B2-4a", "B2-4b", "B2-5a", "B2-5b"]


def score_cell(r, key):
    cell = CELLS[key]
    home, ext, s = run_config(cell["cfg"])
    s["config"] = cell["cfg"]
    s["label"] = cell["label"]
    s["gate"] = gate(s["pooled"])
    s["gate_pass"] = gate_pass(s["gate"])
    r[key] = s
    save_results(r)
    dump(key, home + ext)
    fmt(key + " " + cell["label"], s)
    print(f"{key} GATE: {s['gate']} -> {'PASS' if s['gate_pass'] else 'FAIL'}", flush=True)
    return s


def mode_validate():
    r = load_results()
    home, ext, s = run_config(BASE_CFG)
    exp = {
        "home": {"chains": 589, "trades": 941, "net": 169328.31,
                 "jm": 92266.39, "jo": 77061.92, "oct": 36815.02, "breadth": 24},
        "ext": {"chains": 328, "trades": 481, "net": 295288.72,
                "jm": 151540.58, "jo": 143748.14, "oct": 81933.52, "breadth": 25},
        "pooled": {"chains": 917, "trades": 1422, "net": 464617.03,
                   "jm": 243806.97, "jo": 220810.06, "oct": 118748.54, "breadth": 49},
    }
    ok = True
    for part in ("home", "ext", "pooled"):
        got = {"chains": s[part]["chains"], "trades": s[part]["trades"],
               "net": s[part]["net"], "jm": s[part]["jan_may"]["chain_net"],
               "jo": s[part]["jun_oct"]["chain_net"],
               "oct": s[part]["october"]["chain_net"], "breadth": s[part]["breadth"]}
        good = all(abs(got[k] - v) < 0.01 if isinstance(v, float) else got[k] == v
                   for k, v in exp[part].items())
        ok &= good
        print(f"ANCHOR {part}: {got} -> {'PASS' if good else 'FAIL vs ' + str(exp[part])}",
              flush=True)
    dd_ok = abs(s["pooled"]["max_dd"] - (-17471.45)) < 0.01
    ok &= dd_ok
    print(f"ANCHOR pooled maxDD: {s['pooled']['max_dd']} -> "
          f"{'PASS' if dd_ok else 'FAIL vs -17471.45'}", flush=True)
    r["BASE"] = {**s, "config": BASE_CFG, "anchor_pass": bool(ok)}
    save_results(r)
    dump("BASE", home + ext)
    fmt("BASE MOVER-B", s)
    print("VALIDATION ALL PASS:", bool(ok), flush=True)
    return bool(ok)


def mode_b26():
    r = load_results()
    missing = [k for k in ORDER if k not in r]
    if missing:
        print("B2-6 requires B2-1..B2-5 first; missing:", missing, flush=True)
        sys.exit(1)
    best_key, best_net = None, None
    for k in ORDER:  # order = tie-break (lower family first)
        n = r[k]["pooled"]["net"]
        if best_net is None or n > best_net:
            best_key, best_net = k, n
    base_cfg = dict(r[best_key]["config"])
    print(f"B2-6 base = {best_key} (pooled net {best_net}) cfg={base_cfg}", flush=True)
    r["B2-6_BASE"] = {"source_cell": best_key, "source_net": best_net,
                      "source_config": base_cfg}
    save_results(r)
    for key, tp, sp in (("B2-6a", 1.5, 0.5), ("B2-6b", 1.25, 0.65)):
        cfg = {**base_cfg, "tp": tp, "sp": sp}
        home, ext, s = run_config(cfg)
        s["config"] = cfg
        s["label"] = f"EXIT {tp}%/{sp}% on {best_key}"
        s["gate"] = gate(s["pooled"])
        s["gate_pass"] = gate_pass(s["gate"])
        r[key] = s
        save_results(r)
        dump(key, home + ext)
        fmt(key + " " + s["label"], s)
        print(f"{key} GATE: {s['gate']} -> {'PASS' if s['gate_pass'] else 'FAIL'}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
    elif mode in ("b21", "b22", "b23", "b24a", "b24b", "b25a", "b25b"):
        key = {"b21": "B2-1", "b22": "B2-2", "b23": "B2-3", "b24a": "B2-4a",
               "b24b": "B2-4b", "b25a": "B2-5a", "b25b": "B2-5b"}[mode]
        r = load_results()
        if not r.get("BASE", {}).get("anchor_pass"):
            print("Base anchors not validated — run validate first.", flush=True)
            sys.exit(1)
        score_cell(r, key)
    elif mode == "b26":
        mode_b26()
    else:
        print("unknown mode", mode)
        sys.exit(1)
    print("DONE", mode, flush=True)
