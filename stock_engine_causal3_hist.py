#!/usr/bin/env python3
"""CAUSAL VARIANTS GATE — LEG 3: full-history cross-check on the
25-watchlist universe (data/full_hist), Jan-Oct 2026 AND Jan-Oct
2025. Causal variants (F4-C / INV-LONG-C / INV-ABOVE-C, from
stock_engine_causal3_gate.py) vs their frozen twins, side by side:
trades / net / win rate / ex-top-3 (per stock), month tables,
halves (Jan-May vs Jun-Oct), placebo (same signals, entry shifted
one candle later, exits replayed with the component's own TP/SP),
breadth (stocks net-positive), and an independent re-sum of the
written trade CSVs.

PRE-REGISTERED LEG-3 FAIL RULE: a variant FAILS if it collapses vs
its frozen twin in BOTH years, where collapse in a year = twin net
> 0 AND (causal net < 0 OR causal net < 25% of twin net).

Paper only, real money Rs0. Basis: provisional per 100 shares,
Rs40/trade. Outputs: stock_engine_causal3_hist_summary.json +
stock_engine_causal3_hist_<comp>_<year>.csv per set.
"""
import csv, json, sys, time
from collections import defaultdict

WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import sarvasetu_top3_build as V1
from stock_engine_causal3_gate import (run_chain_causal,
                                       collect2_causal,
                                       apply_law_mapped)

CELL = ("PLAIN", 1.25, 0.5)
INV_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}


def inv_long_rows(g, days, chain_fn):
    """validation build_inv's filters over chains from chain_fn."""
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = chain_fn(sym, day)
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    p2 = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
          and (r["adr"] or 0) >= 3.0]
    inv1 = [r for r in p2 if g["cond_inv1"](r["date"])]
    lng = [r for r in inv1 if r["direction"] == "LONG"]
    return [r for r in lng if not g["wk"](r["date"])
            and r["stock"] not in INV_EXCL]


def inv_above_rows(g, days, chain_fn):
    """logger build_inv_above's filter over chains from chain_fn
    (keeps full chain-row fields, incl. entry, for the placebo)."""
    rows = []
    for sym in g["SYMBOLS"]:
        for day in days:
            rs = chain_fn(sym, day)
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    pop = [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
           and (r["adr"] or 0) >= 3.0]
    return [r for r in pop if g["g1"](r["date"])
            and r["direction"] == "LONG" and not g["wk"](r["date"])
            and r["stock"] not in L.BASE_EXCL
            and r["stock"] not in L.V2_INV_LAW]


def uniform_chain(comp, r):
    return {"comp": comp, "date": r["date"], "stock": r["stock"],
            "dir": r["direction"], "entry_time": r["entry_time"],
            "entry": r["entry"], "exit": r["exit_price"],
            "exit_time": r["exit_time"], "exit_reason": r["exit_reason"],
            "net": r["net"], "setup": r["setup"], "round": r["round"]}


def uniform_f4(comp, t):
    return {"comp": comp, "date": t["date"], "stock": t["symbol"],
            "dir": t["dir"], "entry_time": t["entry_time"],
            "entry": t["entry"], "exit": t["exit"],
            "exit_time": t["exit_time"], "exit_reason": t["exit_reason"],
            "net": t["net"], "setup": t["setup"],
            "round": t.get("round", 1)}


def placebo_net(g, rows, tp, sp):
    """Same signals, entry one candle after the trade's entry
    candle, exits replayed with the component's TP/SP."""
    tot, n, skipped = 0.0, 0, 0
    for t in rows:
        ctx = g["DAYCTX"].get((t["stock"], t["date"]))
        if ctx is None:
            skipped += 1
            continue
        candles = ctx["candles"]
        idx = next((i for i, c in enumerate(candles)
                    if c["time"] == t["entry_time"]), None)
        if idx is None or idx + 1 >= len(candles):
            skipped += 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        sign = 1 if t["dir"] == "LONG" else -1
        _er, _ep, _et, _xi, gross = g["replay_plain"](candles, ei, sign,
                                                      entry, tp, sp)
        tot += gross - 40.0
        n += 1
    return {"trades": n, "net": round(tot, 2), "skipped": skipped}


def stats_block(g, rows, tp, sp):
    a = V1.agg(rows)
    ex3, top3 = V1.extop3(rows)
    months = {}
    bym = defaultdict(list)
    for t in rows:
        bym[t["date"][:7]].append(t)
    for m in sorted(bym):
        months[m] = {"trades": len(bym[m]),
                     "net": round(sum(t["net"] for t in bym[m]), 2)}
    h1 = [t for t in rows if t["date"][5:7] <= "05"]
    h2 = [t for t in rows if t["date"][5:7] >= "06"]
    per_stock = defaultdict(float)
    for t in rows:
        per_stock[t["stock"]] += t["net"]
    return {**a, "ex_top3": ex3, "top3_stocks": top3,
            "months": months,
            "h1_jan_may": {"trades": len(h1),
                           "net": round(sum(t["net"] for t in h1), 2)},
            "h2_jun_oct": {"trades": len(h2),
                           "net": round(sum(t["net"] for t in h2), 2)},
            "breadth_stocks_positive": sum(1 for v in per_stock.values()
                                           if v > 0),
            "breadth_stocks_total": len(per_stock),
            "placebo_shifted_entry": placebo_net(g, rows, tp, sp)}


def main():
    t0 = time.time()
    print("loading 25-universe machinery (full_hist)...", flush=True)
    g = L.load_machinery(L.FULLHIST, "2026-10-28")
    labels = L.regime_labels(g)
    days_by_year = {
        "2025": [d for d in g["ALL_DAYS"]
                 if d.startswith("2025") and d <= "2025-10-31"],
        "2026": [d for d in g["ALL_DAYS"]
                 if d.startswith("2026") and d <= "2026-10-31"],
    }
    print({y: (len(ds), ds[0], ds[-1]) for y, ds in days_by_year.items()},
          flush=True)

    frozen_chain = lambda s, d: g["run_chain"](s, d, CELL)
    causal_chain = lambda s, d: run_chain_causal(g, s, d, CELL)

    out = {"years": {}}
    fields = ["date", "comp", "stock", "dir", "entry_time", "entry",
              "exit", "exit_time", "exit_reason", "net", "setup",
              "round"]
    for year, days in days_by_year.items():
        yres = {}
        # F4 (frozen vs causal)
        f4f_raw = g["collect2"](days, g["F4_CFG"], 1.50, 0.95)
        f4f = [uniform_f4("F4", t) for t in f4f_raw if g["f4_keep"](t)]
        f4c_raw = collect2_causal(g, days, g["F4_CFG"], 1.50, 0.95)
        f4c = [uniform_f4("F4-C", t) for t in f4c_raw if g["f4_keep"](t)]
        # INV-LONG
        ilf = [uniform_chain("INV-LONG", r)
               for r in inv_long_rows(g, days, frozen_chain)]
        ilc = [uniform_chain("INV-LONG-C", r)
               for r in inv_long_rows(g, days, causal_chain)]
        # cross-check frozen INV-LONG against build_inv itself
        book_inv, _st = g["build_inv"](days)
        assert len(book_inv) == len(ilf) and \
            abs(sum(t["net"] for t in book_inv)
                - sum(t["net"] for t in ilf)) < 0.01, "INV-LONG xcheck"
        # INV-ABOVE
        iaf = [uniform_chain("INV-ABOVE", r)
               for r in inv_above_rows(g, days, frozen_chain)]
        iac = [uniform_chain("INV-ABOVE-C", r)
               for r in inv_above_rows(g, days, causal_chain)]
        book_ia = L.build_inv_above(g, days)
        assert len(book_ia) == len(iaf) and \
            abs(sum(t["net"] for t in book_ia)
                - sum(t["net"] for t in iaf)) < 0.01, "INV-ABOVE xcheck"
        # v2 law (causal sets via name mapping)
        sets = {}
        for name, rows, causal in (
                ("F4", f4f, False), ("F4-C", f4c, True),
                ("INV-LONG", ilf, False), ("INV-LONG-C", ilc, True),
                ("INV-ABOVE", iaf, False), ("INV-ABOVE-C", iac, True)):
            rows = (apply_law_mapped(rows, labels) if causal
                    else L.apply_law(rows, labels))
            tp, sp = (1.50, 0.95) if name.startswith("F4") else (1.25, 0.5)
            sets[name] = {"rows": rows, "tp": tp, "sp": sp}
        for name, s in sets.items():
            fn = f"{WS}/stock_engine_causal3_hist_{name}_{year}.csv"
            with open(fn, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=fields)
                w.writeheader()
                for t in sorted(s["rows"],
                                key=lambda t: (t["date"], t["stock"])):
                    w.writerow({k: t.get(k) for k in fields})
            # independent re-sum from the written CSV
            back = list(csv.DictReader(open(fn)))
            resum = round(sum(float(r["net"]) for r in back), 2)
            direct = round(sum(t["net"] for t in s["rows"]), 2)
            assert resum == direct and len(back) == len(s["rows"]), \
                f"re-sum mismatch {name} {year}"
            yres[name] = stats_block(g, s["rows"], s["tp"], s["sp"])
            print(f"{year} {name}: {yres[name]['trades']} tr "
                  f"net {yres[name]['net']:+.2f} WR {yres[name]['win_rate']} "
                  f"ex3 {yres[name]['ex_top3']:+.2f} "
                  f"placebo {yres[name]['placebo_shifted_entry']['net']:+.2f}",
                  flush=True)
        out["years"][year] = yres

    verdicts = {}
    for vc, fc in (("F4-C", "F4"), ("INV-LONG-C", "INV-LONG"),
                   ("INV-ABOVE-C", "INV-ABOVE")):
        collapse_years = []
        for year in ("2025", "2026"):
            twin = out["years"][year][fc]["net"]
            caus = out["years"][year][vc]["net"]
            collapse = twin > 0 and (caus < 0 or caus < 0.25 * twin)
            collapse_years.append(collapse)
        verdicts[vc] = {"collapse_2025": collapse_years[0],
                        "collapse_2026": collapse_years[1],
                        "leg3_pass": not all(collapse_years)}
        print(f"LEG3 {vc}: collapse 2025={collapse_years[0]} "
              f"2026={collapse_years[1]} -> PASS "
              f"{verdicts[vc]['leg3_pass']}", flush=True)
    out["leg3_verdicts"] = verdicts
    out["elapsed_secs"] = round(time.time() - t0, 1)
    with open(f"{WS}/stock_engine_causal3_hist_summary.json", "w") as f:
        json.dump(out, f, indent=1, default=str)
    print(f"DONE leg 3 in {out['elapsed_secs']}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
