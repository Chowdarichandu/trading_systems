#!/usr/bin/env python3
"""SECTOR-CAP RETEST — EKAM intraday (CAND-T5 / S2) on the capped
enlarged universe: frozen 25 + the 12 capped additions (7 surviving
original picks + 5 cap replacements: AMBUJACEM, BHEL, MAXHEALTH,
TMPV, ASIANPAINT), with the owner's Rs3,000 entry-price cap applied
as an entry gate to ALL names: a day-candidate whose entry price
(the open of its entry bar — the exact E the frozen contexts carry)
exceeds Rs3,000 is not eligible for selection that day.

Frozen machinery imported verbatim (same route as sector_ekam.py):
ekam_intraday_stocks_build / _r2_build / _r5_build. Control first:
the 25-name run on the default stores must reproduce the published
totals exactly or the script stops. The uncapped run on the same 37
names is scored beside the capped run purely to count the entries
the cap blocked. Research only.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade."""
import csv, json, os, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2
import ekam_intraday_stocks_r5_build as r5

WS = r1.WS
CAND = r5.CAND
NOV_DATES = r2.NOV_DATES
CAP = 3000.0
FROZEN25 = list(r1.NAMES)
ADD_CAP = ["SBILIFE", "ICICIBANK", "SBIN", "RELIANCE", "INFY",
           "BHARTIARTL", "SUNPHARMA", "AMBUJACEM", "BHEL", "MAXHEALTH",
           "TMPV", "ASIANPAINT"]
NAMES = FROZEN25 + ADD_CAP
TARGETS = {"CAND-T5": {2025: 62164.57, 2026: 63883.60, "nov": 24528.65},
           "S2": {2025: 45300.64, 2026: 72605.30, "nov": 20662.60}}


def max_drawdown(nets):
    cum = peak = dd = 0.0
    for x in nets:
        cum += x
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return round(dd, 2)


def window_stats(ctxs, nets, pred):
    idx = [i for i, t in enumerate(ctxs) if pred(t)]
    sub = [nets[i] for i in idx]
    if not sub:
        return dict(trades=0, net=0.0, wr=None, ex_top3=0.0, max_drawdown=0.0)
    wins = sum(1 for x in sub if x > 0)
    top3 = sum(sorted(sub, reverse=True)[:3])
    return dict(trades=len(sub), net=round(sum(sub), 2),
                wr=round(100.0 * wins / len(sub), 2),
                ex_top3=round(sum(sub) - top3, 2),
                max_drawdown=max_drawdown(sub))


def added_stats(ctxs, nets, pred):
    idx = [i for i, t in enumerate(ctxs)
           if pred(t) and ctxs[i]["sym"] in ADD_CAP]
    sub = [nets[i] for i in idx]
    names = sorted({ctxs[i]["sym"] for i in idx})
    by_name = {}
    for i in idx:
        by_name[ctxs[i]["sym"]] = round(by_name.get(ctxs[i]["sym"], 0.0)
                                        + nets[i], 2)
    return dict(trades=len(sub), net=round(sum(sub), 2),
                names_traded=len(names), names=names, by_name=by_name)


def year_pred(y):
    return lambda t: t["date"][:4] == str(y) and t["date"] <= f"{y}-10-31"


def score_from_daymap(daymap, by_sym, label):
    res = {}
    for name, sel in (("CAND-T5", r5.sel_s0), ("S2", r5.sel_s2)):
        ctxs = r5.contexts_from(daymap, by_sym, sel)
        nets = [r2.net_of(t, **CAND) for t in ctxs]
        yr = r2.year_rows(ctxs, nets)
        book = {"years": {}, "november": {}}
        for y in (2025, 2026):
            ws = window_stats(ctxs, nets, year_pred(y))
            ws["ex_top3"] = yr[y]["ex_top3"]
            book["years"][y] = dict(stats=ws,
                                    added=added_stats(ctxs, nets,
                                                      year_pred(y)))
        nov_pred = lambda t: t["date"] in NOV_DATES
        book["november"] = dict(stats=window_stats(ctxs, nets, nov_pred),
                                added=added_stats(ctxs, nets, nov_pred))
        book["ctxs"] = ctxs
        book["nets"] = nets
        res[name] = book
        print(f"[{label}] {name}: 2025 {book['years'][2025]['stats']} | "
              f"2026 {book['years'][2026]['stats']} | "
              f"NOV {book['november']['stats']}", flush=True)
    return res


def load_stock_wide(sym):
    import numpy as np
    path = os.path.join(WS, "data", "wide100", sym, "spot_5m.csv")
    ts, o, h, l, c = [], [], [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            ts.append(r["timestamp"]); o.append(float(r["open"]))
            h.append(float(r["high"])); l.append(float(r["low"]))
            c.append(float(r["close"]))
    return ts, np.array(o), np.array(h), np.array(l), np.array(c)


def entry_price(cd, by_sym):
    """The exact E contexts_from would carry for this candidate."""
    Dd = by_sym[cd["sym"]]["days"][cd["date"]]
    return float(Dd["o"][cd["entry_li"]])


def blocked_block(unc, capd, y=None):
    """Entries the cap blocked: trades in the UNCAPPED run (same 37
    names) whose entry price exceeds the cap, per window."""
    out = {}
    for name in ("CAND-T5", "S2"):
        ctxs = unc[name]["ctxs"]
        if y is None:
            pred = lambda t: t["date"] in NOV_DATES
        else:
            pred = year_pred(y)
        sel = [t for t in ctxs if pred(t) and t["E"] > CAP]
        by_name = {}
        for t in sel:
            by_name[t["sym"]] = by_name.get(t["sym"], 0) + 1
        out[name] = dict(entries_blocked=len(sel),
                         by_name=by_name,
                         dates=sorted({t["date"] for t in sel}))
    return out


def main():
    # ---- control: frozen 25, default stores, published targets
    stocks25 = [r1.build_stock(s) for s in FROZEN25]
    by25 = {S["sym"]: S for S in stocks25}
    daymap25, _ = r5.collect_day_candidates(stocks25)
    ctl = score_from_daymap(daymap25, by25, "CONTROL-25")
    ok = True
    for name in ("CAND-T5", "S2"):
        for y in (2025, 2026):
            got = ctl[name]["years"][y]["stats"]["net"]
            if got != TARGETS[name][y]:
                ok = False
                print(f"CONTROL MISS {name} {y}: got {got}, "
                      f"want {TARGETS[name][y]}")
        got = ctl[name]["november"]["stats"]["net"]
        if got != TARGETS[name]["nov"]:
            ok = False
            print(f"CONTROL MISS {name} NOV: got {got}, "
                  f"want {TARGETS[name]['nov']}")
    print("EKAM CONTROL:", "PASS — all six totals exact" if ok else "FAIL")
    if not ok:
        return 2

    # ---- enlarged 37 from the wide100 stores
    r1.load_stock = load_stock_wide
    stocks37 = [r1.build_stock(s) for s in NAMES]
    by37 = {S["sym"]: S for S in stocks37}
    daymap37, _ = r5.collect_day_candidates(stocks37)

    unc = score_from_daymap(daymap37, by37, "ENLARGED-37-UNCAPPED")

    # ---- the cap gate: candidates with entry price > Rs3,000 are
    # not eligible for selection (all names, incumbents included)
    gated = {}
    n_cand = n_disq = 0
    disq_by_sym = {}
    for date, cands in daymap37.items():
        keep = []
        for cd in cands:
            n_cand += 1
            if entry_price(cd, by37) > CAP:
                n_disq += 1
                disq_by_sym[cd["sym"]] = disq_by_sym.get(cd["sym"], 0) + 1
            else:
                keep.append(cd)
        gated[date] = keep
    print(f"CAP GATE: {n_disq} of {n_cand} candidate-days disqualified "
          f"(entry price > Rs{CAP:.0f}); by name {disq_by_sym}", flush=True)
    capd = score_from_daymap(gated, by37, "ENLARGED-37-CAPPED")

    out = {"cap": CAP, "additions": ADD_CAP,
           "candidate_days_total": n_cand,
           "candidate_days_disqualified": n_disq,
           "disqualified_by_sym": disq_by_sym,
           "control25": {}, "enlarged37_uncapped": {},
           "enlarged37_capped": {}, "blocked": {}, "trades": []}
    for tag, res in (("control25", ctl), ("enlarged37_uncapped", unc),
                     ("enlarged37_capped", capd)):
        for name in ("CAND-T5", "S2"):
            b = res[name]
            out[tag][name] = {"years": b["years"], "november": b["november"]}
    for y in (2025, 2026):
        out["blocked"][str(y)] = blocked_block(unc, capd, y)
    out["blocked"]["november"] = blocked_block(unc, capd, None)
    for name in ("CAND-T5", "S2"):
        b = capd[name]
        for t, n in zip(b["ctxs"], b["nets"]):
            out["trades"].append(dict(
                book=f"EKAM-{name}", run="enlarged37_capped",
                date=t["date"], sym=t["sym"], side=t["side"],
                entry=round(t["E"], 2), net=round(n, 2),
                added=t["sym"] in ADD_CAP))
    json.dump(out, open(f"{WS}/sector_cap_ekam_results.json", "w"), indent=1)
    print("WROTE sector_cap_ekam_results.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
