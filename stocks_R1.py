#!/usr/bin/env python3
"""LINE R1 — THE HONEST MOVER NEIGHBOURHOOD.
Workplan frozen in stocks_R1_frozen.md BEFORE scoring.
Controls-first: leak audit + placebo in the SAME run as
first scoring. Equity cash, LONG/SHORT, paper only, real
Rs0. Provisional per 100 shares, net = gross - Rs40/trade.
Window Jan-Oct 2026. Pooled 50 primary.

Machinery: stocks_moverB5.build_b5 (validated honest switch)
+ stocks_tuning_mover.pick / premove. R1 builders below copy
build_b5's trade loop with the discard removed (R1-A/B) or
with no signal stream at all (R1-C).
Modes: validate | cells | placebo | all
"""
import csv, json, os, sys
import importlib.util

BASE = "/home/hatch/workspace/trading"

def _load(name, fname):
    spec = importlib.util.spec_from_file_location(name, f"{BASE}/{fname}")
    mod = importlib.util.module_from_spec(spec)
    _argv = sys.argv
    sys.argv = [name]
    spec.loader.exec_module(mod)
    sys.argv = _argv
    return mod

B5 = _load("moverB5", "stocks_moverB5.py")
M = B5.M
U = M.U
COST = 40.0
RESULTS_F = f"{BASE}/stocks_R1_results.json"
MEAS = ["10:00", "10:15"]
CELLS = ["A", "B", "C1", "C2"]


# ---------------- R1 builders ----------------

def _honest_start(candles, window_end):
    return next((i for i, c in enumerate(candles)
                 if c["time"] >= window_end), None)


def _mk_trade(day, sym, direction, setup, leg, rnd, candles, entry_idx,
              er, ep, et, gross, pm, event_status):
    return {"date": day, "symbol": sym, "dir": direction,
            "setup": setup, "leg": leg, "round": rnd,
            "entry_time": candles[entry_idx]["time"],
            "entry": round(float(candles[entry_idx]["open"]), 2),
            "exit_reason": er, "exit_time": et, "exit": round(ep, 2),
            "gross": round(gross, 2), "net": round(gross - COST, 2),
            "event": event_status, "premove_pct": round(100 * pm, 3)}


def build_first(ns, sym, day, window_end="10:00", same_dir=False,
                qual_pm=None):
    """R1-A / R1-B: trade the FIRST signal at/after measurement.
    qual_pm overrides today's pre-move (placebo: yesterday's)."""
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    pm = M.premove(candles, window_end) if qual_pm is None else qual_pm
    if pm is None or abs(pm) < 0.01:
        return []
    move_dir = 1 if pm > 0 else -1
    start = _honest_start(candles, window_end)
    if start is None:
        return []
    trades = []
    while len(trades) < 2:
        chosen = M.pick(ns, sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        direction = "LONG" if dirc == "CE" else "SHORT"
        sign = 1 if direction == "LONG" else -1
        if same_dir and sign != move_dir:
            start = idx + 1
            continue
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        er, ep, et, exit_idx, gross = U.replay_plain(
            candles, entry_idx, sign, entry, 1.25, 0.5)
        trades.append(_mk_trade(
            day, sym, direction, setup,
            "direct" if not trades else "round2", len(trades) + 1,
            candles, entry_idx, er, ep, et, gross, pm,
            ctx["event_status"]))
        start = exit_idx
    return trades


def _plus5(window_end):
    h, m = int(window_end[:2]), int(window_end[3:5]) + 5
    return f"{h:02d}:{m:02d}"


def build_fixed(ns, sym, day, window_end="10:00", tp=0.5, sp=0.5,
                qual_pm=None):
    """R1-C: one fixed-time entry at measurement+5, pre-move dir."""
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    pm = M.premove(candles, window_end) if qual_pm is None else qual_pm
    if pm is None or abs(pm) < 0.01:
        return []
    sign = 1 if pm > 0 else -1
    entry_idx = next((i for i, c in enumerate(candles)
                      if c["time"] >= _plus5(window_end)), None)
    if entry_idx is None:
        return []
    entry = float(candles[entry_idx]["open"])
    er, ep, et, exit_idx, gross = U.replay_plain(
        candles, entry_idx, sign, entry, tp, sp)
    return [_mk_trade(day, sym, "LONG" if sign == 1 else "SHORT",
                      "FIXED", "direct", 1, candles, entry_idx,
                      er, ep, et, gross, pm, ctx["event_status"])]


def yesterday_pm(ns, sym, day, window_end):
    days = ns["ALL_DAYS"]
    i = days.index(day)
    if i == 0:
        return None
    ctx_y = ns["DAYCTX"].get((sym, days[i - 1]))
    if ctx_y is None:
        return None
    return M.premove(ctx_y["candles"], window_end)


def collect_r1(which, cell, window_end, placebo=False):
    ns = M.get_ns(which)
    chains = []
    for sym in ns["SYMBOLS"]:
        for day in ns["ALL_DAYS"]:
            qp = yesterday_pm(ns, sym, day, window_end) if placebo else None
            if cell == "A":
                ts = build_first(ns, sym, day, window_end, False, qp)
            elif cell == "B":
                ts = build_first(ns, sym, day, window_end, True, qp)
            elif cell == "C1":
                ts = build_fixed(ns, sym, day, window_end, 0.5, 0.5, qp)
            elif cell == "C2":
                ts = build_fixed(ns, sym, day, window_end, 1.0, 0.5, qp)
            else:
                raise ValueError(cell)
            if ts:
                chains.append(ts)
    return chains


# ---------------- stats / audit ----------------

def enrich(chains, total_stocks):
    return B5.enrich(chains, total_stocks)


def exp_trade(chains):
    flat = [t for c in chains for t in c]
    if not flat:
        return 0.0
    return round(sum(t["net"] for t in flat) / len(flat), 2)


def leak_audit(chains, window_end):
    flat = [t for c in chains for t in c]
    bad = [t for t in flat if t["entry_time"] < window_end]
    return {"trades_checked": len(flat), "violations": len(bad),
            "min_entry_time": min((t["entry_time"] for t in flat),
                                  default=None),
            "clean": not bad}


def run_cell(cell, window_end, placebo=False):
    home = collect_r1("old", cell, window_end, placebo)
    ext = collect_r1("ext", cell, window_end, placebo)
    out = {"home": enrich(home, 25), "ext": enrich(ext, 25),
           "pooled": enrich(home + ext, 50)}
    out["pooled"]["exp_per_trade"] = exp_trade(home + ext)
    out["audit"] = {"home": leak_audit(home, window_end),
                    "ext": leak_audit(ext, window_end),
                    "pooled": leak_audit(home + ext, window_end)}
    return home, ext, out


def dump(tag, chains):
    flat = [t for c in chains for t in c]
    cols = ["date", "symbol", "dir", "setup", "leg", "round",
            "entry_time", "entry", "exit_time", "exit",
            "exit_reason", "gross", "net", "event", "premove_pct"]
    with open(f"{BASE}/moverR1_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(flat, key=lambda x: (x["date"], x["symbol"],
                                             x["round"])):
            w.writerow({c: t.get(c, "") for c in cols})


def load_results():
    if os.path.exists(RESULTS_F):
        return json.load(open(RESULTS_F))
    return {}


def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)


def fmt(tag, s):
    p, a = s["pooled"], s["audit"]["pooled"]
    print(f"{tag}: pooled chains={p['chains']} trades={p['trades']} "
          f"net={p['net']} exp/ch={p['exp_per_chain']} "
          f"exp/tr={p['exp_per_trade']} JM={p['jan_may']['chain_net']} "
          f"JO={p['jun_oct']['chain_net']} Oct={p['october']['chain_net']} "
          f"breadth={p['breadth']}/50 | home={s['home']['net']} "
          f"ext={s['ext']['net']} | AUDIT checked={a['trades_checked']} "
          f"viol={a['violations']} min_entry={a['min_entry_time']} "
          f"clean={a['clean']}", flush=True)


# ---------------- modes ----------------

ANCH = {"10:00": {"chains": 614, "trades": 946, "net": -117200.13},
        "10:15": {"chains": 894, "trades": 1299, "net": -167156.86}}


def mode_validate():
    r = load_results()
    ok = True
    out = {}
    for we in MEAS:
        home, ext, s = B5.run_config({"window_end": we, "honest": True})
        got = {"chains": s["pooled"]["chains"],
               "trades": s["pooled"]["trades"], "net": s["pooled"]["net"]}
        good = all(abs(got[k] - v) < 0.01 if isinstance(v, float)
                   else got[k] == v for k, v in ANCH[we].items())
        ok &= good
        out[we] = s
        print(f"ANCHOR honest second-signal {we}: {got} -> "
              f"{'PASS' if good else 'FAIL vs ' + str(ANCH[we])}",
              flush=True)
    r["VALIDATE"] = {"pass": bool(ok), "honest_D": out}
    save_results(r)
    print("VALIDATION ALL PASS:", bool(ok), flush=True)
    return bool(ok)


def _cell_gate(s, placebo_net=None, is_best=False):
    p = s["pooled"]
    g = {"jan_may_positive": p["jan_may"]["chain_net"] > 0,
         "jun_oct_positive": p["jun_oct"]["chain_net"] > 0,
         "breadth_ge_35": p["breadth"] >= 35,
         "october_positive": p["october"]["chain_net"] > 0,
         "leak_audit_clean": s["audit"]["pooled"]["clean"]
                             and s["audit"]["home"]["clean"]
                             and s["audit"]["ext"]["clean"]}
    if is_best:
        g["placebo_beaten"] = (placebo_net is not None
                               and placebo_net < p["net"])
    g["pass"] = all(g.values())
    return g


def mode_cells():
    r = load_results()
    if not r.get("VALIDATE", {}).get("pass"):
        print("Validation not passed — run validate first.", flush=True)
        sys.exit(1)
    out = {}
    for cell in CELLS:
        for we in MEAS:
            home, ext, s = run_cell(cell, we)
            out[f"{cell}@{we}"] = s
            dump(f"{cell}_{we.replace(':', '')}", home + ext)
            fmt(f"R1-{cell} @{we}", s)
    r["CELLS"] = out
    save_results(r)
    best_key, best_net = None, None
    for cell in CELLS:
        for we in MEAS:
            n = out[f"{cell}@{we}"]["pooled"]["net"]
            if best_net is None or n > best_net:
                best_key, best_net = f"{cell}@{we}", n
    r["BEST"] = {"key": best_key, "net": best_net}
    save_results(r)
    print(f"BEST CELL: {best_key} pooled net {best_net}", flush=True)


def mode_placebo():
    r = load_results()
    best = r.get("BEST")
    if not best:
        print("CELLS missing — run cells first.", flush=True)
        sys.exit(1)
    cell, we = best["key"].split("@")
    home, ext, s = run_cell(cell, we, placebo=True)
    tag = f"PLACEBO_{cell}_{we.replace(':', '')}"
    dump(tag, home + ext)
    fmt(f"PLACEBO of R1-{cell} @{we} (yesterday-qualified)", s)
    r["PLACEBO"] = {"of": best["key"], **s}
    gates = {}
    for key, cs in r["CELLS"].items():
        is_best = key == best["key"]
        gates[key] = _cell_gate(
            cs, placebo_net=s["pooled"]["net"] if is_best else None,
            is_best=is_best)
        print(f"GATE {key}: {gates[key]}", flush=True)
    r["GATES"] = gates
    save_results(r)
    passed = [k for k, g in gates.items() if g["pass"]]
    print("CELLS PASSING FULL GATE:", passed, flush=True)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
    elif mode == "cells":
        mode_cells()
    elif mode == "placebo":
        mode_placebo()
    elif mode == "all":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
        mode_cells()
        mode_placebo()
    else:
        print("unknown mode", mode)
        sys.exit(1)
    print("DONE", mode, flush=True)
