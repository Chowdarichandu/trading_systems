#!/usr/bin/env python3
"""EKAM-INTRADAY — STOCKS · ROUND 2: tune the vote-decay exit.
Spec: ekam_intraday_stocks_r2_SPEC.md (frozen 2026-11-14, before scoring).
Reuses ekam_intraday_stocks_build.py (R1) for data, indicators, votes, candidate
selection, timing audit and the placebo universe design. Research only.
Writes ekam_intraday_stocks_r2_results.json. Changes no book/ledger/job.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only.
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ekam_intraday_stocks_build as r1

WS = r1.WS
COST = r1.COST
SEED = 20261114
NOV_DATES = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05", "2026-11-06",
             "2026-11-09", "2026-11-11", "2026-11-12", "2026-11-13"]
BASE = dict(D=2, S=0.0075, C=None)

# ---------------------------------------------------------------- parameterised X2 exit
def exit_x2p(o, h, l, c, entry_li, sq_li, E, side, own_votes, D, S, C):
    """R2-spec order per bar: gap fills at open -> stop in range (stop-first) ->
    cap in range -> decay test at close (own votes <= D). Square-off at 15:10 close."""
    if side == 1:
        stp = E * (1.0 - S); tgt = E * (1.0 + C) if C is not None else None
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj <= stp: return oj
            if tgt is not None and oj >= tgt: return oj
            if lj <= stp: return stp
            if tgt is not None and hj >= tgt: return tgt
            v = own_votes[j]
            if v is not None and not (isinstance(v, float) and math.isnan(v)) and v <= D:
                return c[j]
    else:
        stp = E * (1.0 + S); tgt = E * (1.0 - C) if C is not None else None
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj >= stp: return oj
            if tgt is not None and oj <= tgt: return oj
            if hj >= stp: return stp
            if tgt is not None and lj <= tgt: return tgt
            v = own_votes[j]
            if v is not None and not (isinstance(v, float) and math.isnan(v)) and v <= D:
                return c[j]
    return c[sq_li]

def net_of(ctx, D, S, C):
    xp = exit_x2p(ctx["o"], ctx["h"], ctx["l"], ctx["c"], ctx["entry_li"], ctx["sq_li"],
                  ctx["E"], ctx["side"], ctx["own"], D, S, C)
    return r1.trade_net(ctx["E"], xp, ctx["side"])

# ---------------------------------------------------------------- trade contexts
def build_contexts(stocks, by_sym, T):
    """Post-cap trade contexts for threshold T (entries identical to R1)."""
    all_dates = sorted({d for S in stocks for d in S["days"]})
    ctxs, pre_cap = [], []
    for date in all_dates:
        cands = []
        for S in stocks:
            cd = r1.day_candidates(S, date, T)
            if cd: cands.append(cd)
        pre_cap.extend(cands)
        cands.sort(key=lambda x: (x["signal_stamp"], x["sym"]))
        for cd in cands[:r1.DAY_CAP]:
            S = by_sym[cd["sym"]]; Dd = S["days"][cd["date"]]
            eli = cd["entry_li"]; E = float(Dd["o"][eli])
            assert cd["entry_stamp"] > cd["signal_stamp"]  # timing audit
            ctxs.append(dict(sym=cd["sym"], date=cd["date"], side=cd["side"],
                             votes=cd["votes"], signal_stamp=cd["signal_stamp"],
                             entry_stamp=cd["entry_stamp"], E=E, entry_li=eli,
                             sq_li=Dd["sq_li"], o=Dd["o"], h=Dd["h"], l=Dd["l"], c=Dd["c"],
                             own=(Dd["LV"] if cd["side"] == 1 else Dd["SV"])))
    return ctxs, pre_cap

# ---------------------------------------------------------------- summaries
def block(nets):
    tot = sum(nets); n = len(nets)
    wins = sum(1 for x in nets if x > 0)
    return dict(trades=n, total=round(tot, 2),
                wr=round(100.0 * wins / n, 2) if n else None,
                expectancy=round(tot / n, 2) if n else None)

def year_rows(ctxs, nets):
    """nets aligned with ctxs -> per-year window blocks + months + extras."""
    out = {}
    for yr in (2025, 2026):
        idx = [i for i, t in enumerate(ctxs) if t["date"][:4] == str(yr)]
        def sel(lo, hi):
            return [nets[i] for i in idx if lo <= ctxs[i]["date"] <= hi]
        full = sel(f"{yr}-01-01", f"{yr}-10-31")
        months = {}
        for m in range(1, 11):
            mn = [nets[i] for i in idx if ctxs[i]["date"][5:7] == f"{m:02d}"]
            months[f"{yr}-{m:02d}"] = dict(trades=len(mn), total=round(sum(mn), 2))
        top3 = sum(sorted(full, reverse=True)[:3]) if full else 0.0
        out[yr] = dict(jan_jun=block(sel(f"{yr}-01-01", f"{yr}-06-30")),
                       jul_oct=block(sel(f"{yr}-07-01", f"{yr}-10-31")),
                       jan_oct=block(full),
                       months=months,
                       ex_top3=round(sum(full) - top3, 2) if full else None)
    nov = [nets[i] for i, t in enumerate(ctxs) if t["date"] in NOV_DATES]
    out["november_cf"] = block(nov)
    return out

def slim(yrows):
    """Drop months/ex_top3 for non-candidate rows."""
    out = {}
    for yr in (2025, 2026):
        out[yr] = {k: yrows[yr][k] for k in ("jan_jun", "jul_oct", "jan_oct")}
    out["november_cf"] = yrows["november_cf"]
    return out

# ---------------------------------------------------------------- placebo (candidate exit stack)
def placebo_pct(stocks, year, count, D, Sf, C):
    universe = []
    for St in stocks:
        for date, Dd in St["days"].items():
            if date[:4] == str(year) and "01" <= date[5:7] <= "10" and Dd["tradable"]:
                entries = [li for li, s in enumerate(Dd["st"]) if "09:20" <= s <= "15:10"]
                if entries: universe.append((St, Dd, entries))
    rng = random.Random(SEED)
    cache = {}
    def one():
        St, Dd, entries = universe[rng.randrange(len(universe))]
        eli = entries[rng.randrange(len(entries))]
        side = 1 if rng.random() < 0.5 else -1
        key = (St["sym"], Dd["a"], eli, side, D, Sf, C)
        if key not in cache:
            E = float(Dd["o"][eli])
            own = Dd["LV"] if side == 1 else Dd["SV"]
            xp = exit_x2p(Dd["o"], Dd["h"], Dd["l"], Dd["c"], eli, Dd["sq_li"], E, side, own, D, Sf, C)
            cache[key] = r1.trade_net(E, xp, side)
        return cache[key]
    draws = [sum(one() for _ in range(count)) for _ in range(200)]
    return draws

# ---------------------------------------------------------------- selection (frozen rule)
def pick_winner(setting_rows):
    """setting_rows: list of dicts with keys label, full25, full26, is_base.
    Eligible = both years > 0 (else all); winner by (sum, then min, then base)."""
    elig = [r for r in setting_rows if r["full25"] > 0 and r["full26"] > 0] or setting_rows
    return max(elig, key=lambda r: (r["full25"] + r["full26"],
                                    min(r["full25"], r["full26"]), r["is_base"]))

# ---------------------------------------------------------------- main
def main():
    with open(os.path.join(WS, "ekam_intraday_stocks_results.json")) as f:
        r1res = json.load(f)
    stocks = [r1.build_stock(s) for s in r1.NAMES]
    by_sym = {S["sym"]: S for S in stocks}

    ctxs, pre = {}, {}
    for T in (4, 5):
        ctxs[T], pre[T] = build_contexts(stocks, by_sym, T)

    # ---- CONTROL: base params must reproduce R1's published X2 lines exactly
    control = {}
    for T in (4, 5):
        nets = [net_of(t, **BASE) for t in ctxs[T]]
        yr = year_rows(ctxs[T], nets)
        ok = True
        for y in (2025, 2026):
            pub = r1res["rows"][f"T{T}-X2"][str(y)]
            for w in ("jan_jun", "jul_oct", "jan_oct"):
                got = {k: yr[y][w][k] for k in ("trades", "total", "wr")}
                if got != pub[w]: ok = False
        pub_nov = r1res["rows"][f"T{T}-X2"]["november_cf"]
        got_nov = {k: yr["november_cf"][k] for k in ("trades", "total", "wr")}
        if got_nov != {k: pub_nov[k] for k in ("trades", "total", "wr")}: ok = False
        control[f"T{T}-X2"] = dict(reproduced=ok,
                                   full={y: yr[y]["jan_oct"] for y in (2025, 2026)},
                                   november_cf=yr["november_cf"])
        if not ok:
            print("CONTROL MISMATCH", f"T{T}-X2"); print(json.dumps(yr, indent=1)); return
    print("CONTROL OK — T4-X2 and T5-X2 reproduced exactly (all windows + November).")

    # ---- timing audit (R1 sample design on pre-cap candidates)
    flat = sorted(pre[4] + pre[5], key=lambda x: (x["date"], x["signal_stamp"], x["sym"]))
    sample = [(by_sym[cd["sym"]], cd["date"], cd["signal_li"])
              for i, cd in enumerate(flat) if i % 37 == 0]
    checked, mism = r1.audit_sample(stocks, sample)
    print(f"TIMING AUDIT — entries asserted on all trades; truncated recompute {checked} checked, {mism} mismatches.")

    # ---- dial steps, one at a time from each base
    steps_def = {
        "decay": [dict(D=1, S=0.0075, C=None), dict(D=2, S=0.0075, C=None), dict(D=3, S=0.0075, C=None)],
        "stop":  [dict(D=2, S=0.0050, C=None), dict(D=2, S=0.0075, C=None), dict(D=2, S=0.0100, C=None)],
        "cap":   [dict(D=2, S=0.0075, C=None), dict(D=2, S=0.0075, C=0.015)],
    }
    def lab(p):
        return f"D{p['D']}/S{p['S']*100:.2f}%/" + (f"cap{p['C']*100:.1f}%" if p["C"] is not None else "nocap")
    results = {"basis": "equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade, paper only; "
                        "VWAP = equal-weighted typical-price proxy (no volume in stores)",
               "spec": "ekam_intraday_stocks_r2_SPEC.md (frozen 2026-11-14)",
               "control": control,
               "timing_audit": dict(entry_after_signal_asserted_on_all_trades=True,
                                    truncated_recompute_checked=checked,
                                    truncated_recompute_mismatches=mism),
               "steps": {}, "candidates": {}}
    winners = {}
    for T in (4, 5):
        winners[T] = {}
        for step, settings in steps_def.items():
            rows_out, srows = {}, []
            for p in settings:
                nets = [net_of(t, **p) for t in ctxs[T]]
                yr = year_rows(ctxs[T], nets)
                rows_out[lab(p)] = slim(yr)
                srows.append(dict(label=lab(p), params=p,
                                  full25=yr[2025]["jan_oct"]["total"],
                                  full26=yr[2026]["jan_oct"]["total"],
                                  is_base=(p == BASE)))
            w = pick_winner(srows)
            winners[T][step] = w
            results["steps"][f"T{T}-{step}"] = dict(rows=rows_out, winner=w["label"],
                                                   winner_params=w["params"])
            print(f"T{T} step {step}: winner {w['label']} (2025 {w['full25']:+.2f} / 2026 {w['full26']:+.2f})")

    # ---- candidates: combined-after-steps
    bar = {}
    for T in (4, 5):
        cand = dict(D=winners[T]["decay"]["params"]["D"],
                    S=winners[T]["stop"]["params"]["S"],
                    C=winners[T]["cap"]["params"]["C"])
        nets = [net_of(t, **cand) for t in ctxs[T]]
        yr = year_rows(ctxs[T], nets)
        entry = dict(params=cand, label=lab(cand), years={})
        passed_years = {}
        for y in (2025, 2026):
            real = yr[y]["jan_oct"]["total"]; cnt = yr[y]["jan_oct"]["trades"]
            draws = placebo_pct(stocks, y, cnt, cand["D"], cand["S"], cand["C"]) if cnt else []
            pct = round(100.0 * sum(1 for d in draws if d < real) / len(draws), 1) if draws else None
            yr[y]["placebo_pct"] = pct
            yr[y]["placebo_draws"] = (dict(min=round(min(draws), 2),
                                           median=round(sorted(draws)[100], 2),
                                           max=round(max(draws), 2)) if draws else None)
            passed_years[y] = bool(yr[y]["jan_jun"]["total"] > 0 and yr[y]["jul_oct"]["total"] > 0
                                   and yr[y]["jan_oct"]["expectancy"] is not None
                                   and yr[y]["jan_oct"]["expectancy"] >= 80.0
                                   and pct is not None and pct >= 95.0)
            entry["years"][y] = yr[y]
        entry["november_cf"] = yr["november_cf"]
        entry["desired_bar"] = dict(per_year=passed_years,
                                    reached=bool(passed_years[2025] and passed_years[2026]))
        results["candidates"][f"CAND-T{T}"] = entry
        bar[f"CAND-T{T}"] = entry["desired_bar"]["reached"]
        print(f"CAND-T{T} {lab(cand)}: 2025 {yr[2025]['jan_oct']} placebo {yr[2025]['placebo_pct']} | "
              f"2026 {yr[2026]['jan_oct']} placebo {yr[2026]['placebo_pct']} | NOV {yr['november_cf']} | BAR {entry['desired_bar']}")
    results["desired_bar_any_reached"] = any(bar.values())
    with open(os.path.join(WS, "ekam_intraday_stocks_r2_results.json"), "w") as f:
        json.dump(results, f, indent=1)
    print("WROTE ekam_intraday_stocks_r2_results.json")

if __name__ == "__main__":
    main()
