#!/usr/bin/env python3
"""EKAM — one strategy from the indicators that tested good (BB-REV-D + RSI-REV TIME60).
Spec: ekam_SPEC.md (frozen 2026-11-14 before scoring). Research only; changes no
book/ledger/job. Basis: equity cash, frozen 25 names, per 100 shares PROVISIONAL,
Rs40/trade, paper only, real money Rs0. Judged per year, never pooled.
Component definitions are the atlas build's own (imported, not re-implemented).
"""
import csv, json, os, random, sys
import numpy as np

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import indicator_parameter_tuning_stocks_build as ATLAS

NAMES = ATLAS.NAMES
COST = ATLAS.COST
SEED_PLACEBO = 20261114

# ---------------------------------------------------------------- data + signals
def prep(sym):
    dates, o, h, l, c = ATLAS.load_daily(sym)
    n = len(dates)
    mid, sdv = ATLAS.bollinger_bands(c, 20)
    lower = mid - 2 * sdv
    r14 = ATLAS.rsi_wilder(c, 14)
    mm, ss = ATLAS.macd_series(c, 12, 26, 9)

    def cross_up(a, b):
        out = np.zeros(n, dtype=bool)
        ok = ~np.isnan(a) & ~np.isnan(b)
        out[1:] = ok[1:] & ok[:-1] & (a[:-1] <= b[:-1]) & (a[1:] > b[1:])
        return out

    def cross_dn(a, b):
        out = np.zeros(n, dtype=bool)
        ok = ~np.isnan(a) & ~np.isnan(b)
        out[1:] = ok[1:] & ok[:-1] & (a[:-1] >= b[:-1]) & (a[1:] < b[1:])
        return out

    return dict(
        sym=sym, dates=dates, o=o, h=h, l=l, c=c, mid=mid, n=n,
        sig_in={
            "BB": np.concatenate([[False], (c[:-1] < lower[:-1]) & (c[1:] >= lower[1:])
                                  & ~np.isnan(lower[1:])]),
            "RSI": cross_up(r14, np.full(n, 30.0)),
            "MACD": cross_up(mm, ss),
        },
        sig_out={
            "BB": np.where(~np.isnan(mid), c >= mid, False),
            "RSI": np.where(~np.isnan(r14), r14 >= 70, False),
            "MACD": cross_dn(mm, ss),
        },
    )

# ---------------------------------------------------------------- engine
def sim(d, allowed, stop_pct=None, merged=False, events=None):
    """Atlas run_swing semantics, generalised to a merged component union.
    allowed: ordered subset of ['BB','RSI','MACD']. Exit priority per spec:
    TIME60 (RSI in tag) -> hard stop -> CAP +10% (RSI in tag) -> close signals."""
    dates, o, h, l, c, n = d["dates"], d["o"], d["h"], d["l"], d["c"], d["n"]
    trades = []; pos = None; i = 0
    while i < n:
        if pos is None:
            sigs = [k for k in allowed if d["sig_in"][k][i]]
            if sigs and i + 1 < n:
                pos = dict(e=i + 1, E=float(o[i + 1]), comps=tuple(sigs),
                           sig_date=dates[i])
                i += 1; continue
            if sigs and events is not None:
                events.append(("NO_NEXT_DAY", d["sym"], dates[i], "+".join(sigs)))
            i += 1; continue
        if events is not None:
            held = [k for k in allowed if d["sig_in"][k][i]]
            if held:
                events.append(("IGNORED_HELD", d["sym"], dates[i], "+".join(held)))
        e, E, comps = pos["e"], pos["E"], pos["comps"]
        done = None
        if "RSI" in comps and i - e >= 60 and i > e:
            done = (i, float(o[i]), "TIME")
        if done is None and stop_pct is not None and i >= e:
            lvl = E * (1.0 - stop_pct)
            if l[i] <= lvl:
                done = (i, float(o[i]) if o[i] <= lvl else lvl, "STOP")
        if done is None and "RSI" in comps and i >= e:
            lvl = E * 1.10
            if h[i] >= lvl:
                done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
        if done is None:
            fire = None
            for k in comps:
                if d["sig_out"][k][i]:
                    fire = k; break
            if fire is not None:
                kind = ("SIGNAL-" + fire) if merged else "SIGNAL"
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), kind)
                else:
                    done = (i, float(c[i]), "FORCED")
        if done is not None:
            xi, xp, why = done
            trades.append(dict(sym=d["sym"], comps="+".join(comps),
                               signal_date=pos["sig_date"], entry_date=dates[e],
                               exit_date=dates[xi], entry=E, exit=xp,
                               net=round((xp - E) * 100.0 - COST, 2), hold=xi - e,
                               exit_kind=why, forced=(why == "FORCED")))
            pos = None; i = xi; continue
        i += 1
    if pos is not None:
        e, E = pos["e"], pos["E"]
        xp = float(c[n - 1])
        trades.append(dict(sym=d["sym"], comps="+".join(pos["comps"]),
                           signal_date=pos["sig_date"], entry_date=dates[e],
                           exit_date=dates[n - 1], entry=E, exit=xp,
                           net=round((xp - E) * 100.0 - COST, 2), hold=n - 1 - e,
                           exit_kind="FORCED", forced=True))
    return trades

# ---------------------------------------------------------------- stats
def year_sel(trades, year):
    return [t for t in trades if t["entry_date"][:4] == str(year)
            and 1 <= int(t["entry_date"][5:7]) <= 10]

def stats(trades, year):
    sel = year_sel(trades, year)
    if not sel:
        return dict(trades=0, total=0.0, wr=None, avg_hold=None, worst=None,
                    months={}, halves={}, ex_top3=0.0, max_dd=0.0, peak_concurrent=0)
    nets = [t["net"] for t in sel]
    total = round(sum(nets), 2)
    months = {}
    for m in range(1, 11):
        mt = [t["net"] for t in sel if int(t["entry_date"][5:7]) == m]
        months[m] = dict(trades=len(mt), net=round(sum(mt), 2))
    halves = {}
    for name, ms in (("H1", range(1, 7)), ("H2", range(7, 11))):
        ht = [t["net"] for t in sel if int(t["entry_date"][5:7]) in ms]
        halves[name] = dict(trades=len(ht), net=round(sum(ht), 2))
    top = sorted(nets, reverse=True)[:min(3, len(nets))]
    curve = sorted(sel, key=lambda t: (t["exit_date"], t["entry_date"], t["sym"]))
    eq = peak = mdd = 0.0
    for t in curve:
        eq += t["net"]; peak = max(peak, eq); mdd = min(mdd, eq - peak)
    days = sorted({t["entry_date"] for t in sel} | {t["exit_date"] for t in sel})
    conc = 0
    for d0 in days:
        conc = max(conc, sum(1 for t in sel if t["entry_date"] <= d0 <= t["exit_date"]))
    return dict(
        trades=len(sel), total=total,
        wr=round(100.0 * sum(1 for x in nets if x > 0) / len(nets), 2),
        avg_hold=round(sum(t["hold"] for t in sel) / len(sel), 1),
        worst=round(min(nets), 2), months=months, halves=halves,
        ex_top3=round(total - sum(top), 2), max_dd=round(mdd, 2),
        peak_concurrent=conc,
        forced=sum(1 for t in sel if t["forced"]))

# ---------------------------------------------------------------- placebo
def placebo_exit_net(d, e, stop_pct):
    o, h, l, c, mid, n = d["o"], d["h"], d["l"], d["c"], d["mid"], d["n"]
    E = float(o[e]); i = e
    while i < n:
        if i - e >= 60 and i > e:
            return round((float(o[i]) - E) * 100.0 - COST, 2)
        if stop_pct is not None:
            lvl = E * (1.0 - stop_pct)
            if l[i] <= lvl:
                xp = float(o[i]) if o[i] <= lvl else lvl
                return round((xp - E) * 100.0 - COST, 2)
        if not np.isnan(mid[i]) and c[i] >= mid[i]:
            if i + 1 < n:
                return round((float(o[i + 1]) - E) * 100.0 - COST, 2)
            return round((float(c[i]) - E) * 100.0 - COST, 2)
        i += 1
    return round((float(c[n - 1]) - E) * 100.0 - COST, 2)

def placebo(data, year, count, stop_pct, real_total):
    rng = random.Random(SEED_PLACEBO)
    elig = {}
    for sym in NAMES:
        d = data[sym]
        elig[sym] = [i for i, dt in enumerate(d["dates"])
                     if dt[:4] == str(year) and 1 <= int(dt[5:7]) <= 10
                     and i + 1 < d["n"]]
    draws = []
    for _ in range(200):
        tot = 0.0
        for _ in range(count):
            sym = NAMES[rng.randrange(len(NAMES))]
            s = elig[sym][rng.randrange(len(elig[sym]))]
            tot += placebo_exit_net(data[sym], s + 1, stop_pct)
        draws.append(round(tot, 2))
    pct = round(100.0 * sum(1 for x in draws if x <= real_total) / len(draws), 1)
    srt = sorted(draws)
    return dict(n_trades=count, draws=200, real_total=real_total, percentile=pct,
                draw_mean=round(sum(draws) / len(draws), 2),
                draw_median=round(srt[len(srt) // 2], 2))

# ---------------------------------------------------------------- control
ANCHORS = {  # published, indicator_parameter_tuning_stocks_results.json partB
    ("BB-REV-D", "BASE"): dict(dd=-46235.0, years={
        2025: dict(trades=91, total=28946.0, wr=72.53, avg_hold=12.4, worst=-41345.0, forced=0),
        2026: dict(trades=119, total=100067.0, wr=58.82, avg_hold=13.5, worst=-10840.0, forced=0)}),
    ("RSI-REV", "TIME60"): dict(dd=-99431.5, years={
        2025: dict(trades=33, total=63575.5, wr=60.61, avg_hold=45.5, worst=-22630.0, forced=0),
        2026: dict(trades=43, total=108108.9, wr=55.81, avg_hold=35.1, worst=-15040.0, forced=10)}),
    ("MACD-D", "BASE"): dict(dd=-159640.0, years={
        2025: dict(trades=216, total=64237.0, wr=31.48, avg_hold=13.2, worst=-19175.0, forced=0),
        2026: dict(trades=193, total=14101.0, wr=32.64, avg_hold=11.8, worst=-14740.0, forced=8)}),
}

def trade_key(t):
    return (t["sym"], t["entry_date"], t["exit_date"], t["entry"], t["exit"],
            t["net"], t["hold"], t["exit_kind"], t["forced"])

def main():
    out = {"basis": "equity cash, frozen 25 names, per 100 shares PROVISIONAL, "
                    "Rs40/trade, paper only, real money Rs0"}
    data = {sym: prep(sym) for sym in NAMES}

    # ---- CONTROL (a): atlas part_b() rows vs published anchors
    print("control (a): running atlas part_b() ...", flush=True)
    rows, atlas_trades = ATLAS.part_b()
    rowmap = {(r["system"], r["overlay"]): r for r in rows}
    ctrl_a = {}
    for key, anch in ANCHORS.items():
        r = rowmap[key]
        ok = (r["max_drawdown_rs"] == anch["dd"])
        det = {"dd": r["max_drawdown_rs"], "years": {}}
        for yr in (2025, 2026):
            got = r["years"][yr]; exp = anch["years"][yr]
            same = all(got[f] == exp[f] for f in
                       ("trades", "total", "wr", "avg_hold", "worst", "forced"))
            ok = ok and same
            det["years"][yr] = {"match": same, "got": got}
        ctrl_a[f"{key[0]}|{key[1]}"] = {"match": ok, **det}
    # ---- CONTROL (b): EKAM engine single-component == atlas trade lists
    print("control (b): single-component engine check ...", flush=True)
    ctrl_b = {}
    for key, allowed in ((("BB-REV-D", "BASE"), ["BB"]),
                         (("RSI-REV", "TIME60"), ["RSI"]),
                         (("MACD-D", "BASE"), ["MACD"])):
        mine = []
        for sym in NAMES:
            mine.extend(sim(data[sym], allowed))
        a = sorted(trade_key(t) for t in atlas_trades[key])
        b = sorted(trade_key(t) for t in mine)
        ctrl_b[f"{key[0]}|{key[1]}"] = {"match": a == b, "atlas_trades": len(a),
                                        "engine_trades": len(b)}
    out["control"] = {"atlas_rows_vs_published": ctrl_a,
                      "engine_single_component_vs_atlas_trades": ctrl_b}
    all_match = all(v["match"] for v in ctrl_a.values()) and \
        all(v["match"] for v in ctrl_b.values())
    out["control"]["ALL_MATCH"] = all_match
    print(json.dumps(out["control"], indent=1), flush=True)
    if not all_match:
        out["ABORTED"] = "control mismatch - no EKAM numbers produced"
        with open(os.path.join(WS, "ekam_results.json"), "w") as f:
            json.dump(out, f, indent=1)
        print("CONTROL FAILED - aborting before EKAM scoring", flush=True)
        return

    # ---- EKAM scoring
    FORMS = {"S0": None, "S1": 0.08, "S2": 0.12}
    books = {}
    for book, allowed in (("EKAM2", ["BB", "RSI"]), ("EKAM3", ["BB", "RSI", "MACD"])):
        for form, sp in FORMS.items():
            tr = []; ev = []
            for sym in NAMES:
                tr.extend(sim(data[sym], allowed, stop_pct=sp, merged=True, events=ev))
            books[(book, form)] = (tr, ev)
            out.setdefault(book, {})[form] = {
                yr: stats(tr, yr) for yr in (2025, 2026)}
            kinds = {}
            for t in tr:
                kinds[t["exit_kind"]] = kinds.get(t["exit_kind"], 0) + 1
            out[book][form]["exit_kinds_all"] = kinds
            tags = {}
            for t in tr:
                tags[t["comps"]] = tags.get(t["comps"], 0) + 1
            out[book][form]["position_tags_all"] = tags
    # best stop form by frozen rule: argmax over {S1,S2} of two-year total sum
    sums = {f: out["EKAM2"][f][2025]["total"] + out["EKAM2"][f][2026]["total"]
            for f in ("S1", "S2")}
    best_stop = "S1" if sums["S1"] >= sums["S2"] else "S2"
    out["best_stop_form"] = best_stop
    out["best_stop_rule"] = "argmax over {S1,S2} of total_2025 + total_2026; tie -> S1"

    # ---- placebo for EKAM-2 S0 and best stop form
    print("placebo ...", flush=True)
    out["placebo"] = {}
    for form in ("S0", best_stop):
        sp = FORMS[form]
        out["placebo"][form] = {}
        for yr in (2025, 2026):
            st = out["EKAM2"][form][yr]
            out["placebo"][form][yr] = placebo(data, yr, st["trades"], sp, st["total"])

    # ---- November (descriptive): EKAM-2 at S0 and best stop form
    last_date = max(d["dates"][-1] for d in data.values())
    nov = {}
    for form in ("S0", best_stop):
        tr, ev = books[("EKAM2", form)]
        entries = [t for t in tr if "2026-11-02" <= t["entry_date"] <= "2026-11-13"]
        open_at_end = [t for t in tr if t["forced"] and t["exit_date"] == last_date]
        nov[form] = dict(
            entries_nov2_13=[dict(sym=t["sym"], comps=t["comps"],
                                  signal_date=t["signal_date"],
                                  entry_date=t["entry_date"], entry=t["entry"],
                                  status=("OPEN/MARKED" if t in open_at_end
                                          else "CLOSED"),
                                  exit_date=t["exit_date"], exit=t["exit"],
                                  net=t["net"], exit_kind=t["exit_kind"])
                             for t in sorted(entries, key=lambda x: x["entry_date"])],
            open_at_nov13=[dict(sym=t["sym"], comps=t["comps"],
                                entry_date=t["entry_date"], entry=t["entry"],
                                mark=t["exit"], marked_net=t["net"])
                           for t in sorted(open_at_end, key=lambda x: x["entry_date"])],
            signals_no_entry_nov=[e for e in ev
                                  if "2026-11-02" <= e[2] <= "2026-11-13"])
    out["november"] = nov
    out["data_last_date"] = last_date

    with open(os.path.join(WS, "ekam_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(WS, "ekam_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book", "form", "sym", "comps", "signal_date", "entry_date",
                    "exit_date", "entry", "exit", "net", "hold", "exit_kind", "forced"])
        for book in ("EKAM2", "EKAM3"):
            for form in ("S0", "S1", "S2"):
                tr, _ = books[(book, form)]
                for t in sorted(tr, key=lambda x: (x["entry_date"], x["sym"])):
                    w.writerow([book, form, t["sym"], t["comps"], t["signal_date"],
                                t["entry_date"], t["exit_date"], t["entry"], t["exit"],
                                t["net"], t["hold"], t["exit_kind"], t["forced"]])
    print("done. best_stop =", best_stop, flush=True)
    for book in ("EKAM2", "EKAM3"):
        for form in ("S0", "S1", "S2"):
            for yr in (2025, 2026):
                s = out[book][form][yr]
                print(f"{book} {form} {yr}: {s['trades']}t total {s['total']} "
                      f"WR {s['wr']} hold {s['avg_hold']} DD {s['max_dd']} "
                      f"worst {s['worst']} extop3 {s['ex_top3']} peak {s['peak_concurrent']}",
                      flush=True)
    for form, yd in out["placebo"].items():
        for yr, p in yd.items():
            print(f"PLACEBO EKAM2 {form} {yr}: real {p['real_total']} pct {p['percentile']} "
                  f"(draw mean {p['draw_mean']}, median {p['draw_median']}, n {p['n_trades']})",
                  flush=True)

if __name__ == "__main__":
    main()
