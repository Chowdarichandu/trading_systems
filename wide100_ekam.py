#!/usr/bin/env python3
"""WIDE-100 — EKAM-INTRADAY candidates (CAND-T5 / S2): Stage-3
controls on the frozen 25 and Stage-4 wide scoring on 100 names.

Frozen machinery imported verbatim: ekam_intraday_stocks_build
(data, votes, candidates), ekam_intraday_stocks_r2_build
(net_of / year_rows / placebo_pct), ekam_intraday_stocks_r5_build
(selectors / contexts_from). The ONLY changes for the wide run are
the data root (data/wide100) and the symbol list — selection caps
(earliest-5 / earliest-3 per day) bind across all 100 names, which
is the test. Research only; writes only wide100_* outputs.

Modes: control | wide
Basis: equity cash intraday, per 100 shares PROVISIONAL, ₹40/trade.
"""
import csv, json, os, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2
import ekam_intraday_stocks_r5_build as r5

WS = r1.WS
CAND = r5.CAND  # dict(D=3, S=0.0100, C=None) — frozen CAND exit stack
NOV_DATES = r2.NOV_DATES

FROZEN25 = list(r1.NAMES)
stage1 = json.load(open(f"{WS}/wide100_universe_stage1.json"))
NEW75 = [r["sym"] for r in stage1["top75"]]
NAMES100 = FROZEN25 + NEW75

TARGETS = {
    "CAND-T5": {2025: 62164.57, 2026: 63883.60, "nov": 24528.65},
    "S2": {2025: 45300.64, 2026: 72605.30, "nov": 20662.60},
}


def max_drawdown(nets):
    cum = peak = dd = 0.0
    for x in nets:
        cum += x
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return round(dd, 2)


def extra_stats(ctxs, nets):
    """Per-window extras the frozen year_rows does not carry:
    max drawdown (ctx order = chronological) + per-name nets."""
    out = {}
    for label, pred in (
            ("2025", lambda t: t["date"][:4] == "2025" and t["date"] <= "2025-10-31"),
            ("2026", lambda t: t["date"][:4] == "2026" and t["date"] <= "2026-10-31"),
            ("november", lambda t: t["date"] in NOV_DATES)):
        idx = [i for i, t in enumerate(ctxs) if pred(t)]
        sub = [nets[i] for i in idx]
        by_name = {}
        for i in idx:
            by_name[ctxs[i]["sym"]] = by_name.get(ctxs[i]["sym"], 0.0) + nets[i]
        top5 = sorted(by_name.items(), key=lambda kv: -kv[1])[:5]
        tot = sum(sub)
        out[label] = dict(
            max_drawdown=max_drawdown(sub),
            top5_names=[[s, round(v, 2)] for s, v in top5],
            top5_share_pct=(round(100.0 * sum(v for _, v in top5) / tot, 1)
                            if tot > 0 else None),
            names_traded=len(by_name),
            names_positive=sum(1 for v in by_name.values() if v > 0))
    return out


def score(stocks, label):
    by_sym = {S["sym"]: S for S in stocks}
    daymap, pre_cap = r5.collect_day_candidates(stocks)
    res = {}
    for name, sel in (("CAND-T5", r5.sel_s0), ("S2", r5.sel_s2)):
        ctxs = r5.contexts_from(daymap, by_sym, sel)
        nets = [r2.net_of(t, **CAND) for t in ctxs]
        yr = r2.year_rows(ctxs, nets)
        res[name] = dict(ctxs=ctxs, nets=nets, years=yr,
                         extra=extra_stats(ctxs, nets))
        print(f"[{label}] {name}: 2025 {yr[2025]['jan_oct']} | "
              f"2026 {yr[2026]['jan_oct']} | NOV {yr['november_cf']}", flush=True)
    return res, pre_cap, by_sym


def run_control():
    stocks = [r1.build_stock(s) for s in FROZEN25]
    res, _, _ = score(stocks, "CONTROL-25")
    ok = True
    for name in ("CAND-T5", "S2"):
        yr = res[name]["years"]
        for y in (2025, 2026):
            got = round(yr[y]["jan_oct"]["total"], 2)
            if got != TARGETS[name][y]:
                ok = False
                print(f"CONTROL MISS {name} {y}: got {got}, want {TARGETS[name][y]}")
        got_nov = round(yr["november_cf"]["total"], 2)
        if got_nov != TARGETS[name]["nov"]:
            ok = False
            print(f"CONTROL MISS {name} NOV: got {got_nov}, want {TARGETS[name]['nov']}")
    print("EKAM CONTROL:", "PASS — all six totals exact" if ok else "FAIL")
    return 0 if ok else 2


def load_stock_wide(sym):
    path = os.path.join(WS, "data", "wide100", sym, "spot_5m.csv")
    ts, o, h, l, c = [], [], [], [], []
    import numpy as np
    with open(path) as f:
        for r in csv.DictReader(f):
            ts.append(r["timestamp"]); o.append(float(r["open"]))
            h.append(float(r["high"])); l.append(float(r["low"]))
            c.append(float(r["close"]))
    return ts, np.array(o), np.array(h), np.array(l), np.array(c)


def run_wide():
    r1.load_stock = load_stock_wide  # the only machinery patch: data root
    stocks = [r1.build_stock(s) for s in NAMES100]
    res, pre_cap, by_sym = score(stocks, "WIDE-100")
    # timing audit — R5 design: every 37th pre-cap T=5 candidate
    flat = sorted(pre_cap, key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"WIDE TIMING AUDIT: {checked} checked, {mism} mismatches", flush=True)
    out = {"timing_audit": dict(checked=checked, mismatches=mism),
           "pre_cap_candidates": len(pre_cap), "books": {}}
    trades_out = []
    for name in ("CAND-T5", "S2"):
        ctxs, nets, yr = res[name]["ctxs"], res[name]["nets"], res[name]["years"]
        entry = {"years": {}, "extra": res[name]["extra"]}
        for y in (2025, 2026):
            cnt = yr[y]["jan_oct"]["trades"]
            draws = r2.placebo_pct(stocks, y, cnt, CAND["D"], CAND["S"], CAND["C"]) if cnt else []
            pct = round(100.0 * sum(1 for d in draws if d < yr[y]["jan_oct"]["total"]) / len(draws), 1) if draws else None
            yr[y]["placebo_pct"] = pct
            print(f"[WIDE-100] {name} {y}: placebo pct {pct}", flush=True)
            entry["years"][y] = yr[y]
        entry["november_cf"] = yr["november_cf"]
        out["books"][name] = entry
        for t, n in zip(ctxs, nets):
            trades_out.append(dict(book=name, date=t["date"], sym=t["sym"],
                                   side=t["side"], votes=t["votes"],
                                   signal_stamp=t["signal_stamp"],
                                   entry_stamp=t["entry_stamp"],
                                   entry=round(t["E"], 2), net=round(n, 2)))
    json.dump(out, open(f"{WS}/wide100_ekam_results.json", "w"), indent=1)
    with open(f"{WS}/wide100_ekam_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["book", "date", "sym", "side", "votes",
                                          "signal_stamp", "entry_stamp", "entry", "net"])
        w.writeheader()
        w.writerows(sorted(trades_out, key=lambda t: (t["book"], t["date"],
                                                      t["entry_stamp"], t["sym"])))
    print("WROTE wide100_ekam_results.json + wide100_ekam_trades.csv", flush=True)
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "control"
    raise SystemExit(run_control() if mode == "control" else run_wide())
