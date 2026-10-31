#!/usr/bin/env python3
"""MOVER-B4 — controls + peak extension for the B3 candidate.
Families frozen in stocks_moverB4_frozen.md BEFORE scoring.
Equity cash, LONG/SHORT, paper only, real Rs0. Provisional per
100 shares, net = gross - Rs40/trade. Window Jan-Oct 2026.

Machinery: stocks_moverB2.py build/collect/enrich reused verbatim.
Modes: validate | c1 | c2 | c3 | c4
"""
import json, os, sys
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("b2", f"{BASE}/stocks_moverB2.py")
B2 = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["b2"]
spec.loader.exec_module(B2)
sys.argv = _argv
M = B2.M
U = B2.U
COST = 40.0

RESULTS_F = f"{BASE}/stocks_moverB4_results.json"

B3_CFG = {"threshold": 0.01, "window_end": "11:30", "same_dir": True,
          "tp": 1.25, "sp": 0.65, "cap": 1}
B3_NET = 1623905.15


def load_results():
    if os.path.exists(RESULTS_F):
        return json.load(open(RESULTS_F))
    return {}


def save_results(r):
    json.dump(r, open(RESULTS_F, "w"), indent=1)


def gate_bline(pooled, bar_net):
    return {"net_gt_bar": pooled["net"] > bar_net,
            "both_halves_positive": pooled["jan_may"]["chain_net"] > 0
                                    and pooled["jun_oct"]["chain_net"] > 0,
            "breadth_ge_47": pooled["breadth"] >= 47,
            "max_dd_ok": pooled["max_dd"] >= -25000.0,
            "no_losing_month": not pooled["losing_months"]}


def require_base(r):
    if not r.get("BASE", {}).get("anchor_pass"):
        print("Base anchor not validated — run validate first.", flush=True)
        sys.exit(1)


def mode_validate():
    r = load_results()
    home, ext, s = B2.run_config(B3_CFG)
    p = s["pooled"]
    exp = {"chains": 1694, "trades": 1694, "net": 1623905.15,
           "jm": 951573.84, "jo": 672331.31, "oct": 190471.72,
           "breadth": 49, "exp": 958.62, "dd": -11557.03}
    got = {"chains": p["chains"], "trades": p["trades"], "net": p["net"],
           "jm": p["jan_may"]["chain_net"], "jo": p["jun_oct"]["chain_net"],
           "oct": p["october"]["chain_net"], "breadth": p["breadth"],
           "exp": p["exp_per_chain"], "dd": p["max_dd"]}
    ok = all(abs(got[k] - v) < 0.01 for k, v in exp.items()) \
        and not p["losing_months"] \
        and abs(s["home"]["net"] - 489399.84) < 0.01 \
        and abs(s["ext"]["net"] - 1134505.31) < 0.01 \
        and s["home"]["breadth"] == 24 and s["ext"]["breadth"] == 25
    print(f"ANCHOR B3 candidate: {got} losing={p['losing_months']} "
          f"home={s['home']['net']} ext={s['ext']['net']} -> "
          f"{'PASS' if ok else 'FAIL'}", flush=True)
    r["BASE"] = {**s, "config": B3_CFG, "anchor_pass": bool(ok)}
    save_results(r)
    B2.dump("B4_BASE", home + ext)
    B2.fmt("BASE B3 candidate (11:30 comb S065)", s)
    print("VALIDATION:", bool(ok), flush=True)
    return bool(ok)


def mode_c1():
    r = load_results()
    require_base(r)
    for we in ("12:00", "12:30", "13:00"):
        cfg = {**B3_CFG, "window_end": we}
        home, ext, s = B2.run_config(cfg)
        s["config"] = cfg
        s["gate_vs_B3"] = gate_bline(s["pooled"], B3_NET)
        s["gate_pass_vs_B3"] = all(s["gate_vs_B3"].values())
        key = "C1_" + we.replace(":", "")
        r[key] = s
        save_results(r)
        B2.dump("B4_" + key, home + ext)
        B2.fmt(key + f" MEASUREMENT {we}", s)
        print(f"{key} GATE vs B3: {s['gate_vs_B3']} -> "
              f"{'PASS' if s['gate_pass_vs_B3'] else 'FAIL'}", flush=True)


# ---------------- C2 fixed-time control ----------------

def control_collect(which):
    """Qualifying stock-days (pre-move 11:30, |pm|>=1%) and the
    fixed-time control trade on each. Returns (chains, qual_set,
    n_qual, n_no_bar)."""
    ns = M.get_ns(which)
    chains, qual, n_no_bar = [], set(), 0
    for sym in ns["SYMBOLS"]:
        for day in ns["ALL_DAYS"]:
            ctx = ns["DAYCTX"].get((sym, day))
            if ctx is None:
                continue
            candles = ctx["candles"]
            pm = M.premove(candles, "11:30")
            if pm is None or abs(pm) < 0.01:
                continue
            qual.add((sym, day))
            idxs = [i for i, c in enumerate(candles) if c["time"] == "11:35"]
            if not idxs:
                n_no_bar += 1
                continue
            ei = idxs[0]
            entry = float(candles[ei]["open"])
            sign = 1 if pm > 0 else -1
            er, ep, et, exit_idx, gross = U.replay_plain(
                candles, ei, sign, entry, 1.25, 0.65)
            chains.append([{"date": day, "symbol": sym,
                            "dir": "LONG" if sign == 1 else "SHORT",
                            "setup": "FIXED1135", "leg": "direct", "round": 1,
                            "entry_time": candles[ei]["time"],
                            "entry": round(entry, 2), "exit_reason": er,
                            "exit_time": et, "exit": round(ep, 2),
                            "gross": round(gross, 2),
                            "net": round(gross - COST, 2),
                            "event": ctx["event_status"],
                            "premove_pct": round(100 * pm, 3)}])
    return chains, qual, len(qual), n_no_bar


def mode_c2():
    r = load_results()
    require_base(r)
    cand_home = B2.collect("old", **B3_CFG)
    cand_ext = B2.collect("ext", **B3_CFG)
    cand = {"old": cand_home, "ext": cand_ext}
    ctrl, out = {}, {}
    tot_qual = tot_ctrl_net = tot_cand_net = 0
    for which in ("old", "ext"):
        chains, qual, n_qual, n_no_bar = control_collect(which)
        ctrl[which] = chains
        traded = {(c[0]["symbol"], c[0]["date"]) for c in cand[which]}
        assert traded <= qual, f"candidate traded a non-qualifying day in {which}"
        ctrl_by_day = {(c[0]["symbol"], c[0]["date"]): c[0]["net"] for c in chains}
        restr_net = round(sum(ctrl_by_day[k] for k in traded
                              if k in ctrl_by_day), 2)
        cand_net = round(sum(t["net"] for c in cand[which] for t in c), 2)
        ctrl_net = round(sum(t["net"] for c in chains for t in c), 2)
        out[which] = {"n_qualifying_days": n_qual,
                      "n_qual_no_1135_bar": n_no_bar,
                      "control_trades": len(chains),
                      "control_net": ctrl_net,
                      "candidate_chains": len(cand[which]),
                      "candidate_net": cand_net,
                      "control_exp_per_qual_day": round(ctrl_net / n_qual, 2),
                      "candidate_exp_per_qual_day": round(cand_net / n_qual, 2),
                      "control_net_on_candidate_days": restr_net,
                      "control_exp_on_candidate_days":
                          round(restr_net / len(traded), 2) if traded else 0.0,
                      "candidate_exp_per_chain":
                          round(cand_net / len(cand[which]), 2) if cand[which] else 0.0,
                      "capture_pct": round(100 * ctrl_net / cand_net, 1)
                      if cand_net else None}
        tot_qual += n_qual
        tot_ctrl_net += ctrl_net
        tot_cand_net += cand_net
        print(f"C2 {which}: qual={n_qual} ctrl_trades={len(chains)} "
              f"ctrl_net={ctrl_net} cand_chains={len(cand[which])} "
              f"cand_net={cand_net} capture={out[which]['capture_pct']}% "
              f"ctrl_on_cand_days={restr_net}", flush=True)
    pooled_ctrl = B2.enrich(ctrl["old"] + ctrl["ext"], 50)
    out["pooled_control"] = pooled_ctrl
    out["pooled_compare"] = {
        "n_qualifying_days": tot_qual,
        "control_net": round(tot_ctrl_net, 2),
        "candidate_net": round(tot_cand_net, 2),
        "capture_pct": round(100 * tot_ctrl_net / tot_cand_net, 1),
        "control_exp_per_qual_day": round(tot_ctrl_net / tot_qual, 2),
        "candidate_exp_per_qual_day": round(tot_cand_net / tot_qual, 2)}
    print(f"C2 POOLED: {out['pooled_compare']}", flush=True)
    B2.fmt("C2 CONTROL pooled", {"pooled": pooled_ctrl,
                                 "home": B2.enrich(ctrl["old"], 25),
                                 "ext": B2.enrich(ctrl["ext"], 25)})
    r["C2"] = out
    save_results(r)
    B2.dump("B4_C2", ctrl["old"] + ctrl["ext"])


# ---------------- C3 placebo ----------------

def placebo_build(ns, sym, day, ymove):
    """B3 machinery with the measurement replaced by yesterday's
    move: discard first signal; trade next signal agreeing with
    yesterday's move direction; cap 1; T125/S065. Mirrors
    B2.build() semantics exactly."""
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    candles = ctx["candles"]
    move_dir = 1 if ymove > 0 else -1
    trades, start, first_done = [], 0, False
    while True:
        if len(trades) >= 1:
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
        if sign != move_dir:
            start = idx + 1
            continue
        entry_idx = idx + 1
        entry = float(candles[entry_idx]["open"])
        er, ep, et, exit_idx, gross = U.replay_plain(
            candles, entry_idx, sign, entry, 1.25, 0.65)
        trades.append({"date": day, "symbol": sym, "dir": direction,
                       "setup": setup, "leg": "direct", "round": 1,
                       "entry_time": candles[entry_idx]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * ymove, 3)})
        start = exit_idx
    return trades


def placebo_collect(which):
    ns = M.get_ns(which)
    days = sorted(ns["ALL_DAYS"])
    chains, n_qual = [], 0
    for sym in ns["SYMBOLS"]:
        closes = {}
        for d in days:
            ctx = ns["DAYCTX"].get((sym, d))
            if ctx is not None and ctx["candles"]:
                closes[d] = ctx["candles"][-1]["close"]
        for k in range(2, len(days)):
            d, d1, d2 = days[k], days[k - 1], days[k - 2]
            if d1 not in closes or d2 not in closes or not closes[d2]:
                continue
            ymove = closes[d1] / closes[d2] - 1
            if abs(ymove) < 0.01:
                continue
            n_qual += 1
            ts = placebo_build(ns, sym, d, ymove)
            if ts:
                chains.append(ts)
    return chains, n_qual


def mode_c3():
    r = load_results()
    require_base(r)
    out = {}
    tot_qual = tot_net = 0
    all_chains = {}
    for which in ("old", "ext"):
        chains, n_qual = placebo_collect(which)
        all_chains[which] = chains
        s = B2.enrich(chains, 25)
        out[which] = {"summary": s, "n_qualifying_days": n_qual,
                      "coverage_pct": round(100 * len(chains) / n_qual, 1)
                      if n_qual else None,
                      "exp_per_qual_day": round(s["net"] / n_qual, 2)
                      if n_qual else None}
        tot_qual += n_qual
        tot_net += s["net"]
        print(f"C3 {which}: qual={n_qual} chains={len(chains)} "
              f"net={s['net']} exp/ch={s['exp_per_chain']} "
              f"JM={s['jan_may']['chain_net']} JO={s['jun_oct']['chain_net']} "
              f"Oct={s['october']['chain_net']} breadth={s['breadth']}/25",
              flush=True)
    pooled = B2.enrich(all_chains["old"] + all_chains["ext"], 50)
    out["pooled"] = {"summary": pooled, "n_qualifying_days": tot_qual,
                     "exp_per_qual_day": round(tot_net / tot_qual, 2),
                     "vs_candidate_net_pct": round(100 * tot_net / B3_NET, 1)}
    print(f"C3 POOLED: qual={tot_qual} chains={pooled['chains']} "
          f"net={pooled['net']} = {out['pooled']['vs_candidate_net_pct']}% "
          f"of candidate {B3_NET}", flush=True)
    r["C3"] = out
    save_results(r)
    B2.dump("B4_C3", all_chains["old"] + all_chains["ext"])


# ---------------- C4 decomposition ----------------

def mode_c4():
    r = load_results()
    require_base(r)
    cand = B2.collect("old", **B3_CFG) + B2.collect("ext", **B3_CFG)
    flat = [t for c in cand for t in c]
    buckets = {"a_before_1230": [t for t in flat if t["entry_time"] < "12:30"],
               "b_1230_1400": [t for t in flat
                               if "12:30" <= t["entry_time"] < "14:00"],
               "c_after_1400": [t for t in flat if t["entry_time"] >= "14:00"]}
    out = {}
    tot = round(sum(t["net"] for t in flat), 2)
    for k, ts in buckets.items():
        net = round(sum(t["net"] for t in ts), 2)
        wins = sum(1 for t in ts if t["net"] > 0)
        out[k] = {"chains": len(ts), "net": net,
                  "exp_per_chain": round(net / len(ts), 2) if ts else 0.0,
                  "win_pct": round(100 * wins / len(ts), 1) if ts else 0.0,
                  "share_of_net_pct": round(100 * net / tot, 1) if tot else None}
        print(f"C4 {k}: chains={len(ts)} net={net} "
              f"exp={out[k]['exp_per_chain']} win={out[k]['win_pct']}% "
              f"share={out[k]['share_of_net_pct']}%", flush=True)
    out["total"] = {"chains": len(flat), "net": tot}
    r["C4"] = out
    save_results(r)


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if mode == "validate":
        if not mode_validate():
            print("VALIDATION FAILED — aborting.", flush=True)
            sys.exit(1)
    elif mode == "c1":
        mode_c1()
    elif mode == "c2":
        mode_c2()
    elif mode == "c3":
        mode_c3()
    elif mode == "c4":
        mode_c4()
    else:
        print("unknown mode", mode)
        sys.exit(1)
    print("DONE", mode, flush=True)
