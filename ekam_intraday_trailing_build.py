#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · TRAILING-STOP VARIANT.
Spec: ekam_intraday_trailing_SPEC.md (frozen 2026-11-16, before scoring).
Reuses the frozen machinery verbatim: ekam_intraday_stocks_build.py (R1: data,
votes, candidates), ekam_intraday_stocks_r2_build.py (R2: exit stack, summaries),
ekam_intraday_stocks_r5_build.py (R5: selection + contexts). Entries are NOT
rebuilt any other way. Research only — changes no book/ledger/job/live file.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
Data: local stores only (data/sarvaritu_fwd/<SYM>/spot_5m.csv). No network fetch.
"""
import csv, json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2
import ekam_intraday_stocks_r5_build as r5

WS = r1.WS
DECAY_D, HARD_S = 3, 0.0100            # frozen candidate exit params (C=None)
GRID_A = (0.0050, 0.0075, 0.0100)      # activation gain
GRID_TD = (0.0040, 0.0050, 0.0075)     # trail distance
NOV_DATES = r2.NOV_DATES

# published control targets (task-frozen, to the paisa)
TARGETS = {
    "Cand-1": dict(t2025=62164.57, t2026=63883.60, nov=24528.65),
    "Cand-2": dict(t2025=45300.64, t2026=72605.30, nov=20662.60),
}

# ---------------------------------------------------------------- trailing exit
def exit_trail(o, h, l, c, entry_li, sq_li, E, side, own_votes, A, TD):
    """Frozen X2 stack (D=3, S=1.00%, C=None) + trailing stop per SPEC.
    A=None disables the trail (pure frozen replica, reason-annotated).
    Returns (exit_price, exit_li, reason)."""
    D, S = DECAY_D, HARD_S
    if side == 1:
        stp = E * (1.0 - S)
        peak = None
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            armed = (A is not None and peak is not None and peak >= E * (1.0 + A))
            if armed:
                trail = peak * (1.0 - TD)
                if oj <= trail: return oj, j, "trail_gap"
                if lj <= trail: return trail, j, "trail"
            else:
                if oj <= stp: return oj, j, "gap_stop"
                if lj <= stp: return stp, j, "stop"
            v = own_votes[j]
            if v is not None and not (isinstance(v, float) and math.isnan(v)) and v <= D:
                return c[j], j, "decay"
            peak = hj if peak is None else max(peak, hj)
        return c[sq_li], sq_li, "squareoff"
    else:
        stp = E * (1.0 + S)
        trough = None
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            armed = (A is not None and trough is not None and trough <= E * (1.0 - A))
            if armed:
                trail = trough * (1.0 + TD)
                if oj >= trail: return oj, j, "trail_gap"
                if hj >= trail: return trail, j, "trail"
            else:
                if oj >= stp: return oj, j, "gap_stop"
                if hj >= stp: return stp, j, "stop"
            v = own_votes[j]
            if v is not None and not (isinstance(v, float) and math.isnan(v)) and v <= D:
                return c[j], j, "decay"
            trough = lj if trough is None else min(trough, lj)
        return c[sq_li], sq_li, "squareoff"

def run_ctx(ctx, A, TD):
    xp, xli, reason = exit_trail(ctx["o"], ctx["h"], ctx["l"], ctx["c"],
                                 ctx["entry_li"], ctx["sq_li"], ctx["E"],
                                 ctx["side"], ctx["own"], A, TD)
    return xp, xli, reason, r1.trade_net(ctx["E"], xp, ctx["side"])

def worst(ctxs, nets, lo, hi):
    sel = [nets[i] for i, t in enumerate(ctxs) if lo <= t["date"] <= hi]
    return round(min(sel), 2) if sel else None

def summarise(ctxs, nets):
    yr = r2.year_rows(ctxs, nets)
    out = {}
    for y in (2025, 2026):
        out[y] = dict(jan_jun=yr[y]["jan_jun"], jul_oct=yr[y]["jul_oct"],
                      jan_oct=yr[y]["jan_oct"], ex_top3=yr[y]["ex_top3"],
                      worst=worst(ctxs, nets, f"{y}-01-01", f"{y}-10-31"))
    nov_nets = [nets[i] for i, t in enumerate(ctxs) if t["date"] in NOV_DATES]
    out["november"] = dict(yr["november_cf"],
                           worst=round(min(nov_nets), 2) if nov_nets else None)
    return out

def main():
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}
    daymap, _pre = r5.collect_day_candidates(stocks)
    cand_ctxs = {
        "Cand-1": r5.contexts_from(daymap, by_sym, r5.sel_s0),
        "Cand-2": r5.contexts_from(daymap, by_sym, r5.sel_s2),
    }

    # ================= CONTROL GATE (score nothing until this passes) ==========
    control = {}
    for name, ctxs in cand_ctxs.items():
        nets_frozen = [r2.net_of(t, D=DECAY_D, S=HARD_S, C=None) for t in ctxs]
        yr = r2.year_rows(ctxs, nets_frozen)
        got = dict(t2025=yr[2025]["jan_oct"]["total"], t2026=yr[2026]["jan_oct"]["total"],
                   nov=yr["november_cf"]["total"])
        tgt = TARGETS[name]
        if got != tgt:
            print(f"CONTROL MISMATCH — {name}: got {got}, target {tgt}. RUN STOPPED; nothing scored.")
            return
        # replica (trail disabled) must match net_of trade-by-trade
        bad = 0
        for t, nf in zip(ctxs, nets_frozen):
            _xp, _xli, _rs, nr = run_ctx(t, None, None)
            if round(nr, 2) != round(nf, 2): bad += 1
        if bad:
            print(f"REPLICA MISMATCH — {name}: {bad} trades differ from net_of. RUN STOPPED.")
            return
        control[name] = summarise(ctxs, nets_frozen)
        print(f"CONTROL OK — {name}: 2025 {got['t2025']:+.2f} | 2026 {got['t2026']:+.2f} | "
              f"NOV {got['nov']:+.2f}; replica matches net_of on all {len(ctxs)} trades.")

    # ================= GRID ====================================================
    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_trailing_SPEC.md (frozen 2026-11-16)",
               "control_reproduced": True,
               "candidates": {}}
    trade_rows = []

    def emit(name, variant, ctxs, scored):
        for t, (xp, xli, reason, net) in zip(ctxs, scored):
            st = by_sym[t["sym"]]["days"][t["date"]]["st"]
            trade_rows.append([name, variant, t["date"], t["sym"],
                               "LONG" if t["side"] == 1 else "SHORT", t["votes"],
                               t["signal_stamp"], t["entry_stamp"], round(t["E"], 2),
                               st[xli], round(float(xp), 2), reason, round(net, 2)])

    for name, ctxs in cand_ctxs.items():
        entry = {"control": control[name], "grid": {}}
        scored_ctl = [run_ctx(t, None, None) for t in ctxs]
        emit(name, "CONTROL", ctxs, scored_ctl)
        for A in GRID_A:
            for TD in GRID_TD:
                scored = [run_ctx(t, A, TD) for t in ctxs]
                nets = [s[3] for s in scored]
                lab = f"A{A*100:.2f}/TD{TD*100:.2f}"
                entry["grid"][lab] = summarise(ctxs, nets)
                emit(name, lab, ctxs, scored)
        results["candidates"][name] = entry
        c = control[name]
        print(f"{name}: control 2025 {c[2025]['jan_oct']} | 2026 {c[2026]['jan_oct']} | NOV {c['november']}")
        for lab, g in entry["grid"].items():
            print(f"  {lab}: 2025 {g[2025]['jan_oct']['total']:+.2f} (exp {g[2025]['jan_oct']['expectancy']}) | "
                  f"2026 {g[2026]['jan_oct']['total']:+.2f} (exp {g[2026]['jan_oct']['expectancy']}) | "
                  f"NOV {g['november']['total']:+.2f}")

    with open(os.path.join(WS, "ekam_intraday_trailing_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(WS, "ekam_intraday_trailing_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate", "variant", "date", "sym", "side", "votes", "signal_stamp",
                    "entry_stamp", "entry_price", "exit_stamp", "exit_price", "exit_reason", "net_inr"])
        for r in sorted(trade_rows, key=lambda x: (x[0], x[1], x[2], x[6], x[3])):
            w.writerow(r)
    print("WROTE ekam_intraday_trailing_results.json + ekam_intraday_trailing_trades.csv")

if __name__ == "__main__":
    main()
