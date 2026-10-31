#!/usr/bin/env python3
"""INV tuning loop — families T1..T6. Spec: stocks_tuning_inv_frozen.md.
Imports the validated machinery/helpers from stocks_tuning_inv.py and
scores each family from the cached chains, appending its section to
stocks_tuning_inv_report.md and its numbers to
stocks_tuning_inv_results.json. Run in order: T1 T2 T3 T4 T5 T6.
"""
import json, sys, collections, statistics
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_tuning_inv import (build_cell, p2_filter, block, summarize, breadth,
                               load_results, save_results, report_append, dump_trades,
                               cond_inv1, CONDS, plain_label, PLAIN_CELLS, SYMBOLS, BASE)

def inv_rows(label, cap=2, cutoff="10:30", cond=cond_inv1):
    return [r for r in p2_filter(build_cell(label), cap, cutoff) if cond(r)]

def rank_key(b):
    return (min(b["jan_may"]["net_total"], b["jun_oct"]["net_total"]), b["all"]["net_total"])

def table_row(name, b):
    a, jm, jo, oc = b["all"], b["jan_may"], b["jun_oct"], b["october"]
    br = b["breadth"]
    return (f"| {name} | {a['trades']} | {a['win_pct']} | {a['gross_exp']} | {a['net_exp']} "
            f"| {jm['net_total']} ({jm['trades']}) | {jo['net_total']} ({jo['trades']}) "
            f"| {a['net_total']} | {oc['net_total']} | {br['pos_stocks']}/25 | {br['top3_share_pct']} "
            f"| {'**PASS**' if b['pass_gate'] else 'no'} |")

TABLE_HEAD = ("| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) "
              "| Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |\n"
              "|---|---|---|---|---|---|---|---|---|---|---|---|")

def best3_of_T1(res):
    return res["families"]["T1"]["best3"]

# ================= T1 — exit ladder =================
def fam_T1():
    res = load_results()
    cells = {}
    lines = []
    for tp, sp in PLAIN_CELLS:
        label = plain_label(tp, sp)
        rows = inv_rows(label)
        b = block(rows)
        cells[label] = b
        dump_trades(rows, f"T1_{label}")
    ranked = sorted(cells, key=lambda L: rank_key(cells[L]), reverse=True)
    best3 = ranked[:3]
    res["families"]["T1"] = {"cells": cells, "best3": best3,
                             "ranking_by_min_half_then_total": ranked}
    save_results(res)
    lines.append("## Family T1 — EXIT LADDER on INV1 (verdict below)\n")
    lines.append(TABLE_HEAD)
    for L in [plain_label(tp, sp) for tp, sp in PLAIN_CELLS]:
        lines.append(table_row(L, cells[L]))
    lines.append("")
    pos = [L for L in ranked if cells[L]["jan_may"]["net_total"] > 0 and cells[L]["jun_oct"]["net_total"] > 0]
    lines.append(f"Cells positive in BOTH halves (before breadth): {pos if pos else 'NONE'}.")
    lines.append(f"Best 3 by weaker-half net: {', '.join(f'{L} (JM ₹{cells[L]['jan_may']['net_total']}, JO ₹{cells[L]['jun_oct']['net_total']}, total ₹{cells[L]['all']['net_total']}, breadth {cells[L]['breadth']['pos_stocks']}/25)' for L in best3)}.")
    base = cells["T125_S050"]
    best = cells[best3[0]]
    if best3[0] == "T125_S050":
        verdict = ("**Verdict: the frozen T125/S050 is itself the ladder's best cell** — no exit "
                   "change improves the weaker half. Ladder closed as a tuning direction "
                   "(cells that pass the full gate, if any, are marked in the table).")
    else:
        verdict = (f"**Verdict:** best cell {best3[0]} vs baseline T125/S050 — weaker half "
                   f"₹{min(best['jan_may']['net_total'], best['jun_oct']['net_total'])} vs "
                   f"₹{min(base['jan_may']['net_total'], base['jun_oct']['net_total'])}; "
                   f"full-gate pass: {best['pass_gate']}. Detail per cell in the table; "
                   f"rejected cells stand as reported (no cell is hidden).")
    lines.append(verdict + "\n")
    report_append("\n".join(lines) + "\n")
    print("T1 done. best3:", best3, "| both-halves-positive cells:", pos)

# ================= T2 — trail exits =================
def fam_T2():
    res = load_results()
    out = {}
    lines = ["## Family T2 — TRAIL EXIT on INV1\n", TABLE_HEAD]
    for label, desc in (("TRA", "activate +0.75% / trail 0.4%"), ("TRB", "activate +1.0% / trail 0.5%")):
        rows = inv_rows(label)
        b = block(rows)
        mix = collections.Counter(r["exit_reason"] for r in rows)
        b["exit_mix"] = {k: [v, round(100.0 * v / len(rows), 1)] for k, v in sorted(mix.items())} if rows else {}
        out[label] = b
        dump_trades(rows, f"T2_{label}")
        lines.append(table_row(f"{label} ({desc})", b))
    res["families"]["T2"] = out
    save_results(res)
    base = res["families"]["T1"]["cells"]["T125_S050"]
    for label in ("TRA", "TRB"):
        b = out[label]
        lines.append(f"{label} exit mix: {b['exit_mix']}. Weaker half ₹{min(b['jan_may']['net_total'], b['jun_oct']['net_total'])} "
                     f"vs plain T125/S050 ₹{min(base['jan_may']['net_total'], base['jun_oct']['net_total'])}; full-gate pass: {b['pass_gate']}.")
    verdict = ("**Verdict:** " + ("at least one trail variant passes the full gate — see table."
               if any(out[L]["pass_gate"] for L in out) else
               "neither trail variant passes the full gate; trailing does not fix INV1's weaker half. Trail direction closed."))
    lines.append(verdict + "\n")
    report_append("\n".join(lines) + "\n")
    print("T2 done.", {L: (out[L]["jan_may"]["net_total"], out[L]["jun_oct"]["net_total"], out[L]["pass_gate"]) for L in out})

# ================= T3 — direction split =================
def fam_T3():
    res = load_results()
    cells = []
    for L in ["T125_S050", "T100_S050"] + best3_of_T1(res):
        if L not in cells:
            cells.append(L)
    out = {}
    lines = ["## Family T3 — DIRECTION split of INV1 (LONG-only / SHORT-only)\n", TABLE_HEAD]
    for L in cells:
        rows = inv_rows(L)
        entry = {}
        for d in ("LONG", "SHORT"):
            sub = [r for r in rows if r["direction"] == d]
            b = block(sub)
            entry[d] = b
            lines.append(table_row(f"{L} {d}-only", b))
        entry["combined"] = block(rows)
        out[L] = entry
    res["families"]["T3"] = out
    save_results(res)
    t10_long = out["T100_S050"]["LONG"]; t10_short = out["T100_S050"]["SHORT"]
    lines.append(f"**The T10 question:** INV1 at T10/S050 combined has Jan–May −₹517.74 (the known flip). "
                 f"LONG-only at T10: Jan–May ₹{t10_long['jan_may']['net_total']} (n={t10_long['jan_may']['trades']}), "
                 f"Jun–Oct ₹{t10_long['jun_oct']['net_total']} — the flip is "
                 f"{'CURED on the LONG side' if t10_long['jan_may']['net_total'] > 0 else 'NOT cured even LONG-only'}. "
                 f"SHORT-only at T10: Jan–May ₹{t10_short['jan_may']['net_total']}, Jun–Oct ₹{t10_short['jun_oct']['net_total']}.")
    any_pass = [f"{L}-{d}" for L in out for d in ("LONG", "SHORT") if out[L][d]["pass_gate"]]
    lines.append(f"Direction configurations passing the full gate: {any_pass if any_pass else 'NONE'}.")
    lines.append("**Verdict:** " + ("LONG-only is a genuine v2 candidate where marked PASS above."
                 if any_pass else "no direction-only configuration passes the full gate; direction filtering is not the fix.") + "\n")
    report_append("\n".join(lines) + "\n")
    print("T3 done. T10 LONG JM/JO:", t10_long["jan_may"]["net_total"], t10_long["jun_oct"]["net_total"],
          "| T10 SHORT JM/JO:", t10_short["jan_may"]["net_total"], t10_short["jun_oct"]["net_total"], "| passes:", any_pass)

# ================= T4 — condition variants =================
def fam_T4():
    res = load_results()
    best1 = best3_of_T1(res)[0]
    out = {}
    lines = ["## Family T4 — CONDITION VARIANTS (P2 pool, row filters)\n", TABLE_HEAD]
    for L in ["T125_S050", best1]:
        if L in out:
            continue
        out[L] = {}
        p2 = p2_filter(build_cell(L))
        for vname in ("INV1", "N20", "DBL", "BAND"):
            rows = [r for r in p2 if CONDS[vname](r)]
            b = block(rows)
            out[L][vname] = b
            lines.append(table_row(f"{L} cond={vname}", b))
            dump_trades(rows, f"T4_{L}_{vname}")
    res["families"]["T4"] = out
    save_results(res)
    any_pass = [f"{L}-{v}" for L in out for v in out[L] if out[L][v]["pass_gate"] and v != "INV1"]
    lines.append(f"New condition variants passing the full gate: {any_pass if any_pass else 'NONE'} "
                 f"(INV1 itself is the reference, not a new variant).")
    lines.append("**Verdict:** " + ("a condition variant passes — frozen as candidate material below in the summary."
                 if any_pass else "no condition variant beats the base INV1 condition through the full gate; the 50DMA condition stands as the best of this family.") + "\n")
    report_append("\n".join(lines) + "\n")
    print("T4 done. best1:", best1, "| passes:", any_pass)

# ================= T5 — February diagnosis =================
def med(rows, k):
    vals = [r[k] for r in rows if r.get(k) is not None]
    return round(statistics.median(vals), 3) if vals else None

def cut_table(rows, keyfn, name):
    groups = collections.defaultdict(list)
    for r in rows:
        groups[keyfn(r)].append(r)
    out = {}
    for g in sorted(groups, key=lambda x: str(x)):
        s = summarize(groups[g])
        out[str(g)] = s
    return out

def fam_T5():
    res = load_results()
    rows = inv_rows("T125_S050")
    feb = [r for r in rows if r["date"].startswith("2026-02")]
    jm_ex = [r for r in rows if r["date"] < "2026-06-01" and not r["date"].startswith("2026-02")]
    jo = [r for r in rows if r["date"] >= "2026-06-01"]
    def gap_bucket(r):
        g = r["gap_pct"]
        if g is None: return "n/a"
        if g < -1: return "<-1%"
        if g < -0.3: return "-1..-0.3%"
        if g <= 0.3: return "-0.3..+0.3%"
        if g < 1: return "+0.3..+1%"
        return ">+1%"
    def adr_bucket(r):
        a = r["adr"] or 0
        if a < 4: return "ADR 3-4"
        if a < 5: return "ADR 4-5"
        return "ADR 5+"
    diag = {
        "feb": summarize(feb), "jan_may_ex_feb": summarize(jm_ex), "jun_oct": summarize(jo),
        "feb_by_direction": cut_table(feb, lambda r: r["direction"], "direction"),
        "jmex_by_direction": cut_table(jm_ex, lambda r: r["direction"], "direction"),
        "jo_by_direction": cut_table(jo, lambda r: r["direction"], "direction"),
        "feb_by_round": cut_table(feb, lambda r: f"round{r['round']}", "round"),
        "jmex_by_round": cut_table(jm_ex, lambda r: f"round{r['round']}", "round"),
        "feb_by_gap": cut_table(feb, gap_bucket, "gap"),
        "jmex_by_gap": cut_table(jm_ex, gap_bucket, "gap"),
        "jo_by_gap": cut_table(jo, gap_bucket, "gap"),
        "feb_by_adr": cut_table(feb, adr_bucket, "adr"),
        "jmex_by_adr": cut_table(jm_ex, adr_bucket, "adr"),
        "feb_by_stock": cut_table(feb, lambda r: r["stock"], "stock"),
        "feb_exit_mix": {k: [v, round(100.0 * v / len(feb), 1)] for k, v in sorted(collections.Counter(r["exit_reason"] for r in feb).items())},
        "jmex_exit_mix": {k: [v, round(100.0 * v / len(jm_ex), 1)] for k, v in sorted(collections.Counter(r["exit_reason"] for r in jm_ex).items())},
        "medians": {"gap_pct": {"feb": med(feb, "gap_pct"), "jm_ex_feb": med(jm_ex, "gap_pct"), "jun_oct": med(jo, "gap_pct")},
                    "adr": {"feb": med(feb, "adr"), "jm_ex_feb": med(jm_ex, "adr"), "jun_oct": med(jo, "adr")},
                    "abs_gap_pct": {"feb": med([dict(r, ag=abs(r["gap_pct"] or 0)) for r in feb], "ag"),
                                    "jm_ex_feb": med([dict(r, ag=abs(r["gap_pct"] or 0)) for r in jm_ex], "ag"),
                                    "jun_oct": med([dict(r, ag=abs(r["gap_pct"] or 0)) for r in jo], "ag")}},
    }
    res["families"]["T5"] = diag
    save_results(res)
    def cut_lines(title, tbl):
        ls = [f"- {title}:"]
        for g, s in tbl.items():
            ls.append(f"  - {g}: n={s['trades']}, net ₹{s['net_total']}, grossExp ₹{s['gross_exp']}, win {s['win_pct']}%")
        return ls
    L = ["## Family T5 — FEBRUARY DIAGNOSIS (report only — NO filter built)\n"]
    L.append(f"INV1 February 2026 at T125/S050: n={diag['feb']['trades']}, net ₹{diag['feb']['net_total']}, "
             f"grossExp ₹{diag['feb']['gross_exp']}, win {diag['feb']['win_pct']}%. Comparators: "
             f"Jan–May ex-Feb n={diag['jan_may_ex_feb']['trades']}, net ₹{diag['jan_may_ex_feb']['net_total']}, grossExp ₹{diag['jan_may_ex_feb']['gross_exp']}; "
             f"Jun–Oct n={diag['jun_oct']['trades']}, net ₹{diag['jun_oct']['net_total']}, grossExp ₹{diag['jun_oct']['gross_exp']}.")
    L += cut_lines("February by direction", diag["feb_by_direction"])
    L += cut_lines("Jan–May ex-Feb by direction", diag["jmex_by_direction"])
    L += cut_lines("February by chain round", diag["feb_by_round"])
    L += cut_lines("Jan–May ex-Feb by chain round", diag["jmex_by_round"])
    L += cut_lines("February by day-gap bucket", diag["feb_by_gap"])
    L += cut_lines("Jan–May ex-Feb by day-gap bucket", diag["jmex_by_gap"])
    L += cut_lines("February by ADR bucket", diag["feb_by_adr"])
    L += cut_lines("Jan–May ex-Feb by ADR bucket", diag["jmex_by_adr"])
    worst = sorted(diag["feb_by_stock"].items(), key=lambda kv: kv[1]["net_total"])[:5]
    L.append(f"- February's worst stocks: {', '.join(f'{s} (n={v['trades']}, ₹{v['net_total']})' for s, v in worst)}.")
    L.append(f"- Exit mix Feb: {diag['feb_exit_mix']} vs Jan–May ex-Feb: {diag['jmex_exit_mix']}.")
    L.append(f"- Medians — day gap %: Feb {diag['medians']['gap_pct']['feb']} vs JM-ex {diag['medians']['gap_pct']['jm_ex_feb']} vs JO {diag['medians']['gap_pct']['jun_oct']}; "
             f"|gap|: Feb {diag['medians']['abs_gap_pct']['feb']} vs JM-ex {diag['medians']['abs_gap_pct']['jm_ex_feb']} vs JO {diag['medians']['abs_gap_pct']['jun_oct']}; "
             f"ADR: Feb {diag['medians']['adr']['feb']} vs JM-ex {diag['medians']['adr']['jm_ex_feb']} vs JO {diag['medians']['adr']['jun_oct']}.")
    fd, fe = diag["feb_by_direction"], diag["jmex_by_direction"]
    L.append(f"**What distinguishes February (in numbers):** both directions lose in February "
             f"(LONG ₹{fd.get('LONG', {}).get('net_total')} on {fd.get('LONG', {}).get('trades')} trades, "
             f"SHORT ₹{fd.get('SHORT', {}).get('net_total')} on {fd.get('SHORT', {}).get('trades')} trades) whereas "
             f"Jan–May ex-Feb pays on LONGs (₹{fe.get('LONG', {}).get('net_total')}); February's gross expectancy is "
             f"₹{diag['feb']['gross_exp']}/trade against ₹{diag['jan_may_ex_feb']['gross_exp']} for the rest of Jan–May — "
             f"the entries themselves were worse, not just the exits (exit mix and round mix in the cuts above). "
             f"No February filter is built from this — that would be hindsight. Any feature named here "
             f"(direction mix, gap, ADR, round) is ex-ante knowable, but using it requires its own frozen "
             f"family on a fresh window, not a patch on this data.\n")
    report_append("\n".join(L) + "\n")
    print("T5 done. Feb:", diag["feb"], "| medians:", diag["medians"])

# ================= T6 — chain / entry structure =================
def fam_T6():
    res = load_results()
    chain = build_cell("T125_S050")
    out = {}
    lines = ["## Family T6 — CHAIN / ENTRY STRUCTURE on INV1 @ T125/S050\n", TABLE_HEAD]
    for cap in (1, 2, 3):
        for cutoff in ("10:30", "11:30"):
            rows = [r for r in p2_filter(chain, cap, cutoff) if cond_inv1(r)]
            b = block(rows)
            name = f"cap{cap}_cut{cutoff.replace(':', '')}"
            out[name] = b
            lines.append(table_row(name, b))
            dump_trades(rows, f"T6_{name}")
    res["families"]["T6"] = out
    save_results(res)
    any_pass = [k for k, v in out.items() if v["pass_gate"]]
    lines.append(f"Structure cells passing the full gate: {any_pass if any_pass else 'NONE'}. "
                 f"Baseline (cap2, 10:30) is the frozen P2 shape; cap/cutoff changes are v2-candidate material only where marked PASS.")
    lines.append("**Verdict:** " + ("chain/entry structure yields a passing configuration — see table."
                 if any_pass else "no cap/cutoff combination passes the full gate; the frozen cap-2 / 10:30 structure is not improved by loosening or tightening.") + "\n")
    report_append("\n".join(lines) + "\n")
    print("T6 done. passes:", any_pass)

if __name__ == "__main__":
    fn = {"T1": fam_T1, "T2": fam_T2, "T3": fam_T3, "T4": fam_T4, "T5": fam_T5, "T6": fam_T6}[sys.argv[1]]
    fn()
