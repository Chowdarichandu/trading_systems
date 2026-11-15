#!/usr/bin/env python3
"""DIAL — STOCKS Round 2 (frequency test). Spec: dial_stocks_r2_SPEC.md (frozen 2026-11-14).
Reuses dial_stocks_build.py (Round 1) verbatim for data/indicators/exits. Research only.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
Writes dial_stocks_r2_results.json + dial_stocks_r2_trades.csv. Changes no book/ledger/job.
"""
import csv, json, math, os, random, sys
from collections import Counter, defaultdict

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import dial_stocks_build as r1

SEED = 20261115
NAMES = r1.NAMES
NOV_DATES = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
             "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]

ANCHORS = {  # Round 1 published figures (dial_stocks_2026-11-14.md / results JSON)
    ("T", 2025): (4254, -125217.24), ("T", 2026): (4274, -127459.09),
    ("R", 2025): (2438, -68420.73), ("R", 2026): (2465, -165302.21),
    ("COMBINED", 2025): (6692, -193637.97), ("COMBINED", 2026): (6739, -292761.31),
}
NOV_ANCHORS = {"T": (184, -12625.28), "R": (109, -7841.15), "COMBINED": (293, -20466.44)}

# ---------------------------------------------------------------- candidates (Round 1 loop, verbatim + extremity fields)
def stock_candidates(S):
    cands = []
    for date, D in sorted(S["days"].items()):
        if not D["tradable"]:
            continue
        a = D["a"]; n = D["b"] - a
        got = {"T": False, "R": False}
        for li in range(n):
            if got["T"] and got["R"]:
                break
            g = a + li
            if g + 1 < 60:  # warm-up, identical to Round 1
                continue
            if li + 1 >= n:
                continue
            if D["st"][li + 1] > r1.LAST_ENTRY_STAMP:
                continue
            side = comp = None
            if not got["T"] and S["stdir"][g] != 0 and g > 0 and S["stdir"][g - 1] != 0 \
               and S["stdir"][g] != S["stdir"][g - 1]:
                if S["stdir"][g] == 1 and S["c"][g] > D["vwap"][li]:
                    side, comp = 1, "T"
                elif S["stdir"][g] == -1 and S["c"][g] < D["vwap"][li]:
                    side, comp = -1, "T"
            if side is None and not got["R"]:
                r, pb = S["rsi"][g], S["pctb"][g]
                if not (math.isnan(r) or math.isnan(pb) or math.isnan(S["ema"][g]) or math.isnan(S["ema"][g - 6])):
                    slope = (S["ema"][g] - S["ema"][g - 6]) / S["ema"][g - 6]
                    if r <= 30 and pb <= 0.05 and slope > -0.001:
                        side, comp = 1, "R"
                    elif r >= 70 and pb >= 0.95 and slope < 0.001:
                        side, comp = -1, "R"
            if side is None:
                continue
            eli = li + 1
            E = float(D["o"][eli])
            xp = r1.exit_eval(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, side)
            assert eli > li  # timing audit
            cand = dict(sym=S["sym"], date=date, comp=comp, side=side,
                        signal_stamp=D["st"][li], entry_stamp=D["st"][eli],
                        entry=E, exit=float(xp), net=r1.trade_net(E, xp, side),
                        pctb=(float(S["pctb"][g]) if comp == "R" else None),
                        barmove=(side * (float(S["c"][g]) - float(S["o"][g])) / float(S["o"][g])
                                 if comp == "T" else None))
            cands.append(cand)
            got[comp] = True
    return cands

# ---------------------------------------------------------------- R2 selection
def excursion(c):
    if c["comp"] == "R":
        return (0.05 - c["pctb"]) if c["side"] == 1 else (c["pctb"] - 0.95)
    return c["barmove"]

def select_r2(pool):
    by = defaultdict(list)
    for c in pool:
        by[(c["date"], c["comp"])].append(c)
    sel = []
    for key, cs in by.items():
        best = sorted(cs, key=lambda c: (-excursion(c), c["signal_stamp"], c["sym"]))[0]
        best = dict(best); best["excursion"] = excursion(best)
        sel.append(best)
    return sorted(sel, key=lambda c: (c["date"], c["comp"], c["sym"]))

# ---------------------------------------------------------------- frequency-matched placebo
def build_date_universe(stocks):
    """date -> list of (sym, daydict, entry_local_indices) for tradable stock-days."""
    uni = defaultdict(list)
    for S in stocks:
        for date, D in S["days"].items():
            if not D["tradable"]:
                continue
            entries = [li for li, s in enumerate(D["st"]) if "09:20" <= s <= r1.LAST_ENTRY_STAMP]
            if entries:
                uni[date].append((S["sym"], D, entries))
    return uni

def placebo_matched(uni, real_trades, rng):
    """200 draws; each preserves the real book's dates + per-date counts.
    Each placebo trade: random tradable name that date x random entry bar x random side."""
    per_date = Counter(t["date"] for t in real_trades)
    cache = {}
    def one(date):
        sym, D, entries = uni[date][rng.randrange(len(uni[date]))]
        eli = entries[rng.randrange(len(entries))]
        side = 1 if rng.random() < 0.5 else -1
        key = (sym, date, eli, side)
        if key not in cache:
            E = float(D["o"][eli])
            xp = r1.exit_eval(D["o"], D["h"], D["l"], D["c"], eli, D["sq_li"], E, side)
            cache[key] = r1.trade_net(E, xp, side)
        return cache[key]
    draws = []
    dates = sorted(per_date)
    for _ in range(200):
        tot = 0.0
        for d in dates:
            for _ in range(per_date[d]):
                tot += one(d)
        draws.append(tot)
    return draws

# ---------------------------------------------------------------- main
def main():
    stocks = [r1.build_stock(s) for s in NAMES]
    pool = []
    for S in stocks:
        pool.extend(stock_candidates(S))

    # ---- CONTROL 1: anchors (count + total per comp-year, and November)
    control = {"anchors_ok": True, "detail": {}}
    def yr_sel(trades, yr):
        return [t for t in trades if t["date"][:4] == str(yr) and t["date"][5:7] in
                ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")]
    series_pool = {"T": [c for c in pool if c["comp"] == "T"],
                   "R": [c for c in pool if c["comp"] == "R"],
                   "COMBINED": pool}
    for (comp, yr), (cnt, tot) in ANCHORS.items():
        # Round 1's published year totals are sums of rounded monthly nets
        # (its gate_block convention) — reproduce them under that same convention.
        blk0 = r1.gate_block(series_pool[comp], yr)
        got = (blk0["summary"]["trades"], blk0["total"])
        ok = got == (cnt, tot)
        control["detail"][f"{comp}-{yr}"] = dict(expected=(cnt, tot), got=got, ok=ok)
        control["anchors_ok"] = control["anchors_ok"] and ok
    for comp, (cnt, tot) in NOV_ANCHORS.items():
        sel = [t for t in series_pool[comp] if t["date"] in NOV_DATES]
        got = (len(sel), round(sum(t["net"] for t in sel), 2))
        ok = got == (cnt, tot)
        control["detail"][f"NOV-{comp}"] = dict(expected=(cnt, tot), got=got, ok=ok)
        control["anchors_ok"] = control["anchors_ok"] and ok

    # ---- CONTROL 2: row-level identity vs Round 1's published trade file
    r1_rows = set()
    with open(os.path.join(WS, "dial_stocks_trades.csv")) as f:
        for row in csv.DictReader(f):
            r1_rows.add((row["sym"], row["date"], row["comp"], int(row["side"]),
                         row["signal_stamp"], row["entry_stamp"], round(float(row["net"]), 2)))
    pool_rows = set((c["sym"], c["date"], c["comp"], c["side"], c["signal_stamp"],
                     c["entry_stamp"], round(c["net"], 2)) for c in pool)
    control["row_identity_ok"] = (r1_rows == pool_rows)
    control["r1_rows"] = len(r1_rows); control["pool_rows"] = len(pool_rows)
    if not (control["anchors_ok"] and control["row_identity_ok"]):
        print(json.dumps({"CONTROL_FAILED": control}, indent=1))
        sys.exit(2)
    print("CONTROL OK: candidate pool reproduces Round 1 exactly "
          f"(anchors + {len(r1_rows)} published rows identical).")

    # ---- selection
    selected = select_r2(pool)
    series_sel = {"T": [c for c in selected if c["comp"] == "T"],
                  "R": [c for c in selected if c["comp"] == "R"],
                  "COMBINED": selected}

    uni = build_date_universe(stocks)
    rng = random.Random(SEED)
    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only",
               "spec": "dial_stocks_r2_SPEC.md", "control": control, "series": {}}
    for comp in ("T", "R", "COMBINED"):
        results["series"][comp] = {}
        for yr in (2025, 2026):
            blk = r1.gate_block(series_sel[comp], yr)
            real_trades = blk["trades"]
            draws = placebo_matched(uni, real_trades, rng) if real_trades else []
            real = blk["total"]
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
            verdict, fails = r1.pass_verdict(blk, pct, yr)
            results["series"][comp][yr] = dict(
                trades=blk["summary"]["trades"], total=blk["total"], wr=blk["summary"]["wr"],
                months=blk["months"], h1=blk["h1"], h2=blk["h2"], ex_top3=blk["ex_top3"],
                red_months=blk["red_months"], pace=blk["pace"], placebo_pct=pct,
                verdict=verdict, failing_legs=fails,
                placebo_draws_summary=dict(min=round(min(draws), 2),
                                           median=round(sorted(draws)[100], 2),
                                           max=round(max(draws), 2)) if draws else None,
                cand_days=len({t["date"] for t in real_trades}))
            print(comp, yr, "trades", blk["summary"]["trades"], "total", blk["total"],
                  "WR", blk["summary"]["wr"], "pace", blk["pace"], "pct", pct,
                  verdict, fails)

    # ---- November CF (descriptive)
    nov = {}
    for comp in ("T", "R", "COMBINED"):
        sel = [t for t in series_sel[comp] if t["date"] in NOV_DATES]
        by_day = {d: round(sum(t["net"] for t in sel if t["date"] == d), 2) for d in NOV_DATES}
        nov[comp] = dict(trades=len(sel), total=round(sum(t["net"] for t in sel), 2),
                         wr=r1.summarise(sel)["wr"], by_day=by_day,
                         trade_list=[{k: t[k] for k in ("sym", "date", "comp", "side", "signal_stamp",
                                                         "entry_stamp", "entry", "exit", "net")}
                                     for t in sel])
        print("NOV", comp, nov[comp]["trades"], nov[comp]["total"])
    results["november_cf"] = nov
    results["stock_book_nov_actual"] = 7517.94
    results["round1_nov_combined"] = -20466.44

    with open(os.path.join(WS, "dial_stocks_r2_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    with open(os.path.join(WS, "dial_stocks_r2_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sym", "date", "comp", "side", "signal_stamp", "entry_stamp",
                    "entry", "exit", "net", "excursion"])
        for t in selected:
            w.writerow([t["sym"], t["date"], t["comp"], t["side"], t["signal_stamp"],
                        t["entry_stamp"], t["entry"], t["exit"], round(t["net"], 2),
                        round(t["excursion"], 6)])
    print("WROTE dial_stocks_r2_results.json + dial_stocks_r2_trades.csv")

if __name__ == "__main__":
    main()
