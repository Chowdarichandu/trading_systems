#!/usr/bin/env python3
"""LINE B5 — leak audit + honest rebuild of the Morning-Mover.
Workplan frozen in stocks_moverB5_frozen.md BEFORE scoring.
Equity cash, LONG/SHORT, paper only, real Rs0. Provisional
per 100 shares, net = gross - Rs40/trade. Window Jan-Oct 2026.

build_b5 is stocks_moverB2.build copied verbatim, with ONE
added switch: honest=True starts the signal search at the
first bar at/after the measurement time instead of bar 0.
Modes: validate | audit | honest | stack | all
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
RESULTS_F = f"{BASE}/stocks_moverB5_results.json"

MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]


def build_b5(ns, sym, day, threshold=0.01, window_end="10:00",
             same_dir=False, tp=1.25, sp=0.5, cap=2, honest=False):
    """B2 build verbatim + honest start. Identical semantics otherwise."""
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return [], None
    candles = ctx["candles"]
    pm = M.premove(candles, window_end)
    if pm is None or abs(pm) < threshold:
        return [], pm
    move_dir = 1 if pm > 0 else -1
    if honest:
        start = next((i for i, c in enumerate(candles)
                      if c["time"] >= window_end), None)
        if start is None:
            return [], pm
    else:
        start = 0
    trades, first_done = [], False
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


def collect_b5(which, **kw):
    ns = M.get_ns(which)
    chains = []
    for sym in ns["SYMBOLS"]:
        for day in ns["ALL_DAYS"]:
            ts, _ = build_b5(ns, sym, day, **kw)
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
    home = collect_b5("old", **cfg)
    ext = collect_b5("ext", **cfg)
    return home, ext, {"home": enrich(home, 25), "ext": enrich(ext, 25),
                       "pooled": enrich(home + ext, 50)}


def gate5(pooled):
    g = {"jan_may_positive": pooled["jan_may"]["chain_net"] > 0,
         "jun_oct_positive": pooled["jun_oct"]["chain_net"] > 0,
         "breadth_ge_35": pooled["breadth"] >= 35,
         "october_positive": pooled["october"]["chain_net"] > 0}
    g["pass"] = all(g.values())
    return g


def dump(tag, chains, window_end=None):
    flat = [t for c in chains for t in c]
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "entry_time",
            "entry", "exit_time", "exit", "exit_reason", "gross", "net",
            "event", "premove_pct"]
    if window_end is not None:
        cols = cols + ["slice"]
    with open(f"{BASE}/moverB5_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(flat, key=lambda x: (x["date"], x["symbol"], x["round"])):
            row = {c: t.get(c, "") for c in cols}
            if window_end is not None:
                row["slice"] = "pre" if t["entry_time"] < window_end else "post"
            w.writerow(row)


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


# ---------------- Part 1: leak audit ----------------

def slice_block(trades):
    pairs = {(t["date"], t["symbol"]) for t in trades}
    by_sym = defaultdict(float)
    for t in trades:
        by_sym[t["symbol"]] += t["net"]

    def rng(a, b):
        return round(sum(t["net"] for t in trades if a <= t["date"] <= b), 2)

    return {"chains": len(pairs), "trades": len(trades),
            "net": round(sum(t["net"] for t in trades), 2),
            "jan_may": rng("2026-01-01", "2026-05-31"),
            "jun_oct": rng("2026-06-01", "2026-10-28"),
            "october": rng("2026-10-01", "2026-10-28"),
            "breadth": sum(1 for v in by_sym.values() if v > 0),
            "stocks_total": len(by_sym)}


def slice_stats(chains, window_end):
    flat = [t for c in chains for t in c]
    pre = [t for t in flat if t["entry_time"] < window_end]
    post = [t for t in flat if t["entry_time"] >= window_end]
    classes = {"all_pre": {"chains": 0, "net": 0.0},
               "all_post": {"chains": 0, "net": 0.0},
               "mixed": {"chains": 0, "net": 0.0}}
    for c in chains:
        kinds = {"pre" if t["entry_time"] < window_end else "post" for t in c}
        key = ("all_pre" if kinds == {"pre"}
               else "all_post" if kinds == {"post"} else "mixed")
        classes[key]["chains"] += 1
        classes[key]["net"] = round(
            classes[key]["net"] + sum(t["net"] for t in c), 2)
    full = slice_block(flat)
    pre_b, post_b = slice_block(pre), slice_block(post)
    leak = (round(100 * pre_b["net"] / full["net"], 1)
            if full["net"] else None)
    return {"full": full, "pre": pre_b, "post": post_b,
            "classes": classes, "leak_share_pct": leak}


def audit_config(window_end):
    home = collect_b5("old", window_end=window_end)
    ext = collect_b5("ext", window_end=window_end)
    return home, ext, {"home": slice_stats(home, window_end),
                       "ext": slice_stats(ext, window_end),
                       "pooled": slice_stats(home + ext, window_end)}


# ---------------- Modes ----------------

ANCHORS = {
    "A": {"window_end": "10:00",
          "home": {"chains": 424, "trades": 698, "net": 84671.74,
                   "jm": 52884.19, "jo": 31787.55, "oct": 16825.42, "breadth": 16},
          "ext": {"chains": 199, "trades": 300, "net": 164483.29,
                  "jm": 73142.55, "jo": 91340.74, "oct": 39984.55, "breadth": 22},
          "pooled": {"chains": 623, "trades": 998, "net": 249155.03,
                     "jm": 126026.74, "jo": 123128.29, "oct": 56809.97, "breadth": 38}},
    "B": {"window_end": "10:15",
          "home": {"chains": 589, "trades": 941, "net": 169328.31,
                   "jm": 92266.39, "jo": 77061.92, "oct": 36815.02, "breadth": 24},
          "ext": {"chains": 328, "trades": 481, "net": 295288.72,
                  "jm": 151540.58, "jo": 143748.14, "oct": 81933.52, "breadth": 25},
          "pooled": {"chains": 917, "trades": 1422, "net": 464617.03,
                     "jm": 243806.97, "jo": 220810.06, "oct": 118748.54, "breadth": 49},
          "pooled_max_dd": -17471.45},
}


def core_of(s):
    return {"chains": s["chains"], "trades": s["trades"], "net": s["net"],
            "jm": s["jan_may"]["chain_net"], "jo": s["jun_oct"]["chain_net"],
            "oct": s["october"]["chain_net"], "breadth": s["breadth"]}


def mode_validate():
    r = load_results()
    ok = True
    out = {}
    for tag in ("A", "B"):
        we = ANCHORS[tag]["window_end"]
        home, ext, s = run_config({"window_end": we})
        out[tag] = s
        for part in ("home", "ext", "pooled"):
            got, exp = core_of(s[part]), ANCHORS[tag][part]
            good = all(abs(got[k] - v) < 0.01 if isinstance(v, float)
                       else got[k] == v for k, v in exp.items())
            ok &= good
            print(f"ANCHOR {tag}-{part}: {got} -> "
                  f"{'PASS' if good else 'FAIL vs ' + str(exp)}", flush=True)
        fmt(f"LEAKY MOVER-{tag} ({we})", s)
        if tag == "B":
            dd_ok = abs(s["pooled"]["max_dd"] - ANCHORS["B"]["pooled_max_dd"]) < 0.01
            ok &= dd_ok
            print(f"ANCHOR B pooled maxDD: {s['pooled']['max_dd']} -> "
                  f"{'PASS' if dd_ok else 'FAIL vs -17471.45'}", flush=True)
    r["VALIDATE"] = {"pass": bool(ok), "A": out["A"], "B": out["B"]}
    save_results(r)
    print("VALIDATION ALL PASS:", bool(ok), flush=True)
    return bool(ok)


def mode_audit():
    r = load_results()
    if not r.get("VALIDATE", {}).get("pass"):
        print("Validation not passed — run validate first.", flush=True)
        sys.exit(1)
    out = {}
    for tag, we in (("A", "10:00"), ("B", "10:15")):
        home, ext, s = audit_config(we)
        out[tag] = s
        dump(f"AUDIT_{tag}", home + ext, window_end=we)
        for part in ("home", "ext", "pooled"):
            b = s[part]
            print(f"AUDIT {tag} {part}: full net={b['full']['net']} "
                  f"(ch={b['full']['chains']}) | pre net={b['pre']['net']} "
                  f"(ch={b['pre']['chains']}, tr={b['pre']['trades']}) | "
                  f"post net={b['post']['net']} (ch={b['post']['chains']}, "
                  f"tr={b['post']['trades']}) | leak={b['leak_share_pct']}% | "
                  f"classes={b['classes']}", flush=True)
    r["AUDIT"] = out
    save_results(r)


HONEST_TIMES = ["10:00", "10:15", "10:30", "11:30"]


def mode_honest():
    r = load_results()
    if not r.get("VALIDATE", {}).get("pass"):
        print("Validation not passed — run validate first.", flush=True)
        sys.exit(1)
    out = {}
    for we in HONEST_TIMES:
        home, ext, s = run_config({"window_end": we, "honest": True})
        s["gate"] = gate5(s["pooled"])
        out[we] = s
        dump(f"HONEST_{we.replace(':', '')}", home + ext)
        fmt(f"HONEST {we}", s)
        print(f"HONEST {we} GATE: {s['gate']}", flush=True)
    r["HONEST"] = out
    save_results(r)


def mode_stack():
    r = load_results()
    h = r.get("HONEST")
    if not h:
        print("HONEST results missing — run honest first.", flush=True)
        sys.exit(1)
    best_we, best_net = None, None
    for we in HONEST_TIMES:  # frozen order = tie-break (earlier time wins)
        n = h[we]["pooled"]["net"]
        if best_net is None or n > best_net:
            best_we, best_net = we, n
    print(f"STACK base = honest {best_we} (pooled net {best_net})", flush=True)
    cfg = {"window_end": best_we, "honest": True, "same_dir": True,
           "cap": 1, "tp": 1.25, "sp": 0.65}
    home, ext, s = run_config(cfg)
    s["config"] = cfg
    s["gate"] = gate5(s["pooled"])
    r["STACK"] = {"base_window_end": best_we, "base_net": best_net, **s}
    save_results(r)
    dump("STACK", home + ext)
    fmt(f"STACK honest {best_we} same-dir cap1 T125/S065", s)
    print(f"STACK GATE: {s['gate']}", flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
    elif mode == "audit":
        mode_audit()
    elif mode == "honest":
        mode_honest()
    elif mode == "stack":
        mode_stack()
    elif mode == "all":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
        mode_audit()
        mode_honest()
        mode_stack()
    else:
        print("unknown mode", mode)
        sys.exit(1)
    print("DONE", mode, flush=True)
