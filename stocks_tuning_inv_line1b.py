#!/usr/bin/env python3
"""INV tuning loop — Line 1b: INV-LONG concentration stress + DBL follow-up.
Spec: stocks_tuning_inv_frozen.md, section 'Line 1b' (frozen before scoring).
Row operations only on cached chains via the validated Line 1 helpers.
EQUITY CASH intraday, LONG/SHORT, paper only. Provisional per 100 shares;
net = gross - Rs40/trade. Appends the Line 1b section to
stocks_tuning_inv_report.md and merges numbers into
stocks_tuning_inv_results.json under families.L1b.
"""
import json, sys, collections
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_tuning_inv import (build_cell, p2_filter, block, summarize, breadth,
                               load_results, save_results, report_append, dump_trades,
                               cond_inv1, cond_dbl, SYMBOLS)

CAP = 2000.0

def inv_long_rows():
    rows = [r for r in p2_filter(build_cell("T125_S050")) if cond_inv1(r)]
    return [r for r in rows if r["direction"] == "LONG"]

def dbl_rows(label):
    return [r for r in p2_filter(build_cell(label)) if cond_dbl(r)]

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

# ---------- anchors ----------
il = inv_long_rows()
b_il = block(il)
assert b_il["all"]["trades"] == 249 and abs(b_il["all"]["net_total"] - 24185.73) < 0.01 \
    and abs(b_il["jan_may"]["net_total"] - 14751.12) < 0.01 \
    and abs(b_il["jun_oct"]["net_total"] - 9434.61) < 0.01 \
    and b_il["breadth"]["pos_stocks"] == 12, f"INV-LONG anchor FAIL: {b_il['all']} {b_il['breadth']}"
dbl125 = dbl_rows("T125_S050")
b_dbl = block(dbl125)
assert b_dbl["all"]["trades"] == 390 and abs(b_dbl["all"]["net_total"] - 16548.78) < 0.01 \
    and abs(b_dbl["jan_may"]["net_total"] - 7861.57) < 0.01 \
    and abs(b_dbl["jun_oct"]["net_total"] - 8687.21) < 0.01 \
    and b_dbl["breadth"]["pos_stocks"] == 9, f"DBL anchor FAIL: {b_dbl['all']} {b_dbl['breadth']}"
print("ANCHORS PASS: INV-LONG 249/+24185.73 (JM 14751.12 / JO 9434.61, breadth 12/25); "
      "DBL@T125 390/+16548.78 (JM 7861.57 / JO 8687.21, breadth 9/25)")

per_stock_il = b_il["breadth"]["per_stock_net"]
print("INV-LONG per-stock nets (top):",
      sorted(per_stock_il.items(), key=lambda kv: -kv[1])[:5])

out = {"anchors": {"inv_long": b_il, "dbl_t125": b_dbl}}

# ---------- S1: concentration stress ----------
s1 = {}
variants = {
    "S1a_ex_TVSMOTOR": [r for r in il if r["stock"] != "TVSMOTOR"],
    "S1b_ex_GLENMARK": [r for r in il if r["stock"] != "GLENMARK"],
    "S1c_ex_both": [r for r in il if r["stock"] not in ("TVSMOTOR", "GLENMARK")],
}
for k, rows in variants.items():
    s1[k] = block(rows)

# (d) winsorised accounting
def winsorised(rows):
    def per_stock(rs):
        per = collections.defaultdict(float)
        for r in rs:
            per[r["stock"]] += r["net"]
        return {s: round(per.get(s, 0.0), 2) for s in SYMBOLS}
    tot_ps = per_stock(rows)
    jm_ps = per_stock([r for r in rows if r["date"] < "2026-06-01"])
    jo_ps = per_stock([r for r in rows if r["date"] >= "2026-06-01"])
    wins_tot = round(sum(min(v, CAP) for v in tot_ps.values()), 2)
    wins_jm = round(sum(min(v, CAP) for v in jm_ps.values()), 2)
    wins_jo = round(sum(min(v, CAP) for v in jo_ps.values()), 2)
    n = len(rows)
    wins_pos = sorted([min(v, CAP) for v in tot_ps.values() if v > 0], reverse=True)
    top3 = round(100.0 * sum(wins_pos[:3]) / wins_tot, 1) if wins_tot > 0 else None
    base = summarize(rows)
    return {"trades": n, "win_pct": base["win_pct"],
            "net_total_winsorised": wins_tot, "jan_may_winsorised": wins_jm,
            "jun_oct_winsorised": wins_jo,
            "net_exp_winsorised": round(wins_tot / n, 2) if n else None,
            "pos_stocks": sum(1 for v in tot_ps.values() if v > 0),
            "top3_share_pct_winsorised": top3,
            "per_stock_net_raw": tot_ps}

s1["S1d_winsorised_2000"] = winsorised(il)
out["S1"] = s1
c_blk, d_blk = s1["S1c_ex_both"], s1["S1d_winsorised_2000"]
c_ok = (c_blk["jan_may"]["net_total"] > 0 and c_blk["jun_oct"]["net_total"] > 0
        and (c_blk["all"]["net_exp"] or 0) > 0)
d_ok = (d_blk["jan_may_winsorised"] > 0 and d_blk["jun_oct_winsorised"] > 0
        and (d_blk["net_exp_winsorised"] or 0) > 0)
if c_blk["all"]["net_total"] <= 0 or d_blk["net_total_winsorised"] <= 0:
    s1_verdict = "FALLS"
elif c_ok and d_ok:
    s1_verdict = "STANDS"
else:
    s1_verdict = "STANDS WEAKENED"
out["S1_verdict"] = s1_verdict
print("S1:", {k: (v["all"]["net_total"] if "all" in v else v["net_total_winsorised"]) for k, v in s1.items()},
      "| verdict:", s1_verdict)

# ---------- S2: DBL LONG-only ----------
s2 = {}
for label, tag in (("T125_S050", "primary"), ("T100_S050", "shadow")):
    rows = [r for r in dbl_rows(label) if r["direction"] == "LONG"]
    s2[label] = block(rows)
    dump_trades(rows, f"L1b_S2_DBL_LONG_{label}")
    print(f"S2 DBL LONG @{label} ({tag}):", s2[label]["all"], s2[label]["jan_may"],
          s2[label]["jun_oct"], "breadth", s2[label]["breadth"]["pos_stocks"], "PASS", s2[label]["pass_gate"])
out["S2"] = s2

# ---------- S3: DBL both directions, friendlier exits ----------
s3 = {}
for label in ("T100_S050", "T125_S065"):
    rows = dbl_rows(label)
    s3[label] = block(rows)
    dump_trades(rows, f"L1b_S3_DBL_{label}")
    print(f"S3 DBL @{label}:", s3[label]["all"], s3[label]["jan_may"], s3[label]["jun_oct"],
          "breadth", s3[label]["breadth"]["pos_stocks"], "PASS", s3[label]["pass_gate"])
out["S3"] = s3

# ---------- S4: INV-LONG month table ----------
months = [f"2026-{m:02d}" for m in range(1, 11)]
mt = {}
cum = 0.0
for m in months:
    s = summarize([r for r in il if r["date"].startswith(m)])
    cum = round(cum + s["net_total"], 2)
    mt[m] = {"trades": s["trades"], "net_total": s["net_total"], "cumulative": cum,
             "flag_below_minus3000": s["net_total"] < -3000}
top2 = sorted((v["net_total"] for v in mt.values()), reverse=True)[:2]
top2_share = round(100.0 * sum(top2) / b_il["all"]["net_total"], 1) if b_il["all"]["net_total"] > 0 else None
out["S4"] = {"months": mt, "top2_months_share_pct": top2_share,
             "flagged_months": [m for m, v in mt.items() if v["flag_below_minus3000"]]}
print("S4 months:", {m: v["net_total"] for m, v in mt.items()}, "| top2 share:", top2_share,
      "| flagged:", out["S4"]["flagged_months"])

# ---------- save ----------
res = load_results()
res.setdefault("families", {})["L1b"] = out
save_results(res)

# ---------- report ----------
L = ["## Line 1b — INV-LONG concentration stress + DBL follow-up (spec: frozen file, Line 1b section)\n"]
L.append("Anchors reproduced to the paisa before scoring: INV-LONG 249 trades, +₹24,185.73 "
         "(halves +₹14,751.12 / +₹9,434.61, breadth 12/25); DBL @ T125/S050 390 trades, "
         "+₹16,548.78 (halves +₹7,861.57 / +₹8,687.21, breadth 9/25).\n")
L.append(f"INV-LONG per-stock nets behind the concentration warning: "
         f"TVSMOTOR ₹{per_stock_il['TVSMOTOR']}, GLENMARK ₹{per_stock_il['GLENMARK']} — "
         f"together ₹{round(per_stock_il['TVSMOTOR'] + per_stock_il['GLENMARK'], 2)} of the "
         f"₹24,185.73 total ({round(100.0 * (per_stock_il['TVSMOTOR'] + per_stock_il['GLENMARK']) / 24185.73, 1)}%).\n")
L.append("### Family S1 — INV-LONG concentration stress\n")
L.append(TABLE_HEAD)
L.append(table_row("INV-LONG (reference)", b_il))
L.append(table_row("S1a ex-TVSMOTOR", s1["S1a_ex_TVSMOTOR"]))
L.append(table_row("S1b ex-GLENMARK", s1["S1b_ex_GLENMARK"]))
L.append(table_row("S1c ex-both", s1["S1c_ex_both"]))
d = d_blk
L.append(f"| S1d winsorised (per-stock cap +₹2,000) | {d['trades']} | {d['win_pct']} | — "
         f"| {d['net_exp_winsorised']} | {d['jan_may_winsorised']} | {d['jun_oct_winsorised']} "
         f"| {d['net_total_winsorised']} | — | {d['pos_stocks']}/25 | {d['top3_share_pct_winsorised']} | accounting |")
L.append("")
L.append(f"**S1 verdict (pre-declared rule): INV-LONG {s1_verdict}.** "
         f"Ex-both: total ₹{c_blk['all']['net_total']}, halves ₹{c_blk['jan_may']['net_total']} / "
         f"₹{c_blk['jun_oct']['net_total']}, expectancy ₹{c_blk['all']['net_exp']}, breadth "
         f"{c_blk['breadth']['pos_stocks']} positive stocks of the remaining 23. Winsorised: total "
         f"₹{d['net_total_winsorised']}, halves ₹{d['jan_may_winsorised']} / ₹{d['jun_oct_winsorised']}, "
         f"expectancy ₹{d['net_exp_winsorised']} (breadth unchanged by construction — a positive cap "
         f"cannot flip a stock's sign).\n")
L.append("### Family S2 — DBL LONG-only\n")
L.append(TABLE_HEAD)
L.append(table_row("DBL LONG-only @ T125_S050 (primary)", s2["T125_S050"]))
L.append(table_row("DBL LONG-only @ T100_S050 (shadow)", s2["T100_S050"]))
L.append("")
p2 = s2["T125_S050"]
L.append(f"**S2 verdict:** DBL LONG-only at the primary exit "
         f"{'PASSES the full gate — frozen as an additional v2 candidate in stocks_dbl_candidate_spec.md' if p2['pass_gate'] else 'does NOT pass the full gate'} "
         f"(n={p2['all']['trades']}, halves ₹{p2['jan_may']['net_total']} / ₹{p2['jun_oct']['net_total']}, "
         f"breadth {p2['breadth']['pos_stocks']}/25, expectancy ₹{p2['all']['net_exp']}). "
         f"Shadow exit T100/S050: {'passes' if s2['T100_S050']['pass_gate'] else 'does not pass'} "
         f"(breadth {s2['T100_S050']['breadth']['pos_stocks']}/25).\n")
L.append("### Family S3 — DBL both-directions at friendlier exits\n")
L.append(TABLE_HEAD)
for label in ("T100_S050", "T125_S065"):
    L.append(table_row(f"DBL both-dir @ {label}", s3[label]))
L.append("")
any_s3 = [L_ for L_ in s3 if s3[L_]["pass_gate"]]
L.append(f"**S3 verdict:** {'passing cell(s): ' + ', '.join(any_s3) + ' — frozen in stocks_dbl_candidate_spec.md.' if any_s3 else 'neither cell passes the full gate'} "
         f"T100/S050 breadth {s3['T100_S050']['breadth']['pos_stocks']}/25 (halves "
         f"₹{s3['T100_S050']['jan_may']['net_total']} / ₹{s3['T100_S050']['jun_oct']['net_total']}); "
         f"T125/S065 breadth {s3['T125_S065']['breadth']['pos_stocks']}/25 (halves "
         f"₹{s3['T125_S065']['jan_may']['net_total']} / ₹{s3['T125_S065']['jun_oct']['net_total']}).\n")
L.append("### Family S4 — INV-LONG month table\n")
L.append("| Month | Trades | Net ₹ | Cumulative ₹ | Flag |\n|---|---|---|---|---|")
for m in months:
    v = mt[m]
    L.append(f"| {m} | {v['trades']} | {v['net_total']} | {v['cumulative']} | "
             f"{'**< −₹3,000**' if v['flag_below_minus3000'] else ''} |")
L.append("")
L.append(f"Months below −₹3,000: {out['S4']['flagged_months'] if out['S4']['flagged_months'] else 'NONE'}. "
         f"Top-2 months' share of the Jan–Oct total: {top2_share}% "
         f"(the two largest monthly nets sum to ₹{round(sum(top2), 2)} of ₹24,185.73).\n")
report_append("\n".join(L) + "\n")
print("REPORT APPENDED. S1 verdict:", s1_verdict,
      "| S2 pass:", s2["T125_S050"]["pass_gate"], s2["T100_S050"]["pass_gate"],
      "| S3 pass:", {k: v["pass_gate"] for k, v in s3.items()})
json.dump({"S1_verdict": s1_verdict,
           "S2_pass": {k: v["pass_gate"] for k, v in s2.items()},
           "S3_pass": {k: v["pass_gate"] for k, v in s3.items()}},
          open("/tmp/l1b_flags.json", "w"))
