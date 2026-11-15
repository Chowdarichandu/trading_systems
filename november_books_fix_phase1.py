#!/usr/bin/env python3
"""NOVEMBER BOOKS FIX — PHASE 1: LEG-LEVEL LOSS ANATOMY (2026-11-14).

Stored legs only, Jan-Oct 2026. November sets NO rule.
Books: BANK TUNED STACK v2, BANK LEGACY (v21 frame),
       NIFTY TUNED v1 (DEC-S1 minus B PE), NIFTY DEC-S1 (control).
Dimensions per leg: side (CE/PE) x day-type (regime-like per the frozen
definition in november_regime_fix_2026-11-14.md) x entry-time bucket
(pre-11:00 / 11:00-12:30 / post-12:30) x exit class
(entry-bar stop / later stop / target / runner-stop / square-off).
Exit-class mapping (frozen here): exit_reason 'stop' or 'be_stop' ->
entry-bar stop iff exit_time == entry_time else later stop;
'target'/'runner_target' -> target; 'runner_stop' -> runner-stop;
'square_off'/'runner_square_off' -> square-off. Anything else aborts.
Basis: option premiums per 1 lot (Bank 30, Nifty 65), Rs220/trade inside
every stored net, UNIQUE-ONCE, buying only. Paper only, real money Rs0.
"""
import csv, json, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r8_harness as R8
import nifty_engine_r6_harness as R6

TR = Path.home() / "workspace/trading"

# ---------------- regime classification (frozen definition) ----------------
def load_regime(fn):
    out = {}
    for r in csv.DictReader(open(TR / fn)):
        if not ("2026-01-01" <= r["date"] <= "2026-10-31"):
            continue
        rl = r["regime_like"]
        out[r["date"]] = dict(
            regime=("regime" if rl == "True" else
                    "non-regime" if rl == "False" else "unclassified"),
            gap_topq=(r["gap_topq"] == "True"),
            reversal=(r["reversal"] == "True"),
            gap_pct=(float(r["gap_pct"]) if r["gap_pct"] else None),
            morning_pct=(float(r["morning_pct"]) if r["morning_pct"] else None))
    return out

REG_BANK = load_regime("november_regime_days_bank.csv")
REG_NIFTY = load_regime("november_regime_days_nifty.csv")

def bucket(t):
    return "pre-11:00" if t < "11:00" else ("11:00-12:30" if t < "12:30"
                                            else "post-12:30")

def exit_class(reason, et, xt):
    if reason in ("stop", "be_stop"):
        return "entry-bar stop" if xt == et else "later stop"
    if reason in ("target", "runner_target"):
        return "target"
    if reason in ("runner_stop", "lock_stop"):
        return "runner-stop"
    if reason in ("square_off", "runner_square_off"):
        return "square-off"
    raise SystemExit(f"UNMAPPED exit_reason {reason!r}")

# ---------------- leg loaders (anchors asserted) ---------------------------
def bank_legs(fn, netcol="net_inr"):
    legs = []
    for r in csv.DictReader(open(TR / fn)):
        legs.append(dict(date=r["date"], side=r["direction"],
                         family=r.get("family", ""), rep=r.get("rep", ""),
                         entry_time=r["entry_time"],
                         entry_premium=float(r["entry_premium"]),
                         exit_time=r["exit_time"], exit_reason=r["exit_reason"],
                         net=float(r[netcol])))
    return legs

stack = bank_legs("solid60_programme_2026-11-13_bank_A_stack_ALL_X-1_trades.csv")
assert len(stack) == 111 and round(sum(l["net"] for l in stack), 2) == 127351.50
# cross-check vs the features file (x1_net) leg by leg
feat = {(r["date"], r["entry_time"], r["direction"]): float(r["x1_net"])
        for r in csv.DictReader(open(TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv"))}
for l in stack:
    assert feat[(l["date"], l["entry_time"], l["side"])] == l["net"], l
legacy = bank_legs("bank_engine_r6_v21_trades.csv")
assert len(legacy) == 99 and round(sum(l["net"] for l in legacy), 2) == 83650.50

GEOM = dict(R7.STANDING_GEOM)
A = R7.standing_legs()
B, _ = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                           with_trend=False, exclude_keys=R7.keys_of(A))
C, _ = R8.expiry_sleeve_legs(R7.keys_of(A) | R7.keys_of(B))
DECS1 = A + B + C
dump = json.loads((TR / "nifty_engine_r11_decs1_legs.json").read_text())
tagmap = {(d["date"], d["direction"], d["entry_time"], int(d["strike"]),
           d["expiry"]): d["component"] for d in dump}
for l in DECS1:
    l["_comp"] = tagmap[(l["date"], l["direction"], l["entry_time"],
                         int(l["strike"]), l["expiry"])]
res, nc, _ = R6.score_r6(DECS1, geom=GEOM)
assert nc == 0 and round(sum(r["net"] for r in res), 2) == 91168.50
compmap = {(l["date"], l["direction"], l["entry_time"], int(l["strike"]),
            l["expiry"]): l["_comp"] for l in DECS1}
nifty_all = []
for r in res:
    nifty_all.append(dict(
        date=r["date"], side=r["direction"],
        family=compmap[(r["date"], r["direction"], r["entry_time"],
                        int(r["strike"]), r["expiry"])],
        rep=r["rep"], entry_time=r["entry_time"],
        entry_premium=float(r["entry"]), exit_time=r["exit_time"],
        exit_reason=r["exit_reason"], net=float(r["net"])))
decs1 = nifty_all
v1 = [l for l in nifty_all if not (l["family"] == "B" and l["side"] == "PE")]
assert len(v1) == 74 and round(sum(l["net"] for l in v1), 2) == 103050.25

BOOKS = [("BANK_STACK", stack, REG_BANK), ("BANK_LEGACY", legacy, REG_BANK),
         ("NIFTY_TUNED_V1", v1, REG_NIFTY), ("NIFTY_DECS1", decs1, REG_NIFTY)]

# ---------------- dimension assignment -------------------------------------
all_legs = []
for name, legs, reg in BOOKS:
    for l in legs:
        rg = reg.get(l["date"], {}).get("regime", "unclassified")
        row = dict(book=name, date=l["date"], side=l["side"],
                   family=l["family"], rep=l["rep"],
                   entry_time=l["entry_time"], bucket=bucket(l["entry_time"]),
                   entry_premium=l["entry_premium"],
                   exit_time=l["exit_time"], exit_reason=l["exit_reason"],
                   exit_class=exit_class(l["exit_reason"], l["entry_time"],
                                         l["exit_time"]),
                   regime=rg, net=l["net"])
        rinfo = reg.get(l["date"], {})
        row.update(gap_topq=rinfo.get("gap_topq"), reversal=rinfo.get("reversal"),
                   gap_pct=rinfo.get("gap_pct"), morning_pct=rinfo.get("morning_pct"))
        all_legs.append(row)

with open(TR / "november_books_fix_anatomy_legs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(all_legs[0].keys()))
    w.writeheader(); w.writerows(all_legs)

# ---------------- cell tables ----------------------------------------------
def cells(book, keys):
    agg = {}
    for l in all_legs:
        if l["book"] != book: continue
        k = tuple(l[x] for x in keys)
        a = agg.setdefault(k, [0, 0.0, 0])
        a[0] += 1; a[1] += l["net"]; a[2] += (l["net"] > 0)
    return [(k, v[0], round(v[1], 2), round(100.0 * v[2] / v[0], 1))
            for k, v in sorted(agg.items())]

cell_rows = []
for name, _, _ in BOOKS:
    for k, n, net, wr in cells(name, ["side", "regime", "bucket", "exit_class"]):
        cell_rows.append(dict(book=name, side=k[0], regime=k[1], bucket=k[2],
                              exit_class=k[3], legs=n, net=net, win_rate=wr))
with open(TR / "november_books_fix_anatomy_cells.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(cell_rows[0].keys()))
    w.writeheader(); w.writerows(cell_rows)

out = {"books": {}}
for name, legs, _ in BOOKS:
    out["books"][name] = dict(legs=len(legs),
                              total=round(sum(l["net"] for l in legs), 2))
    print(f"\n===== {name}: {len(legs)} legs, total "
          f"{sum(l['net'] for l in legs):+,.2f}")
    for dim in (["side"], ["regime"], ["bucket"], ["exit_class"],
                ["side", "regime"], ["side", "bucket"], ["side", "exit_class"],
                ["regime", "bucket"], ["regime", "exit_class"],
                ["side", "regime", "bucket"], ["family"], ["side", "family"]):
        print(f"-- by {' x '.join(dim)}")
        for k, n, net, wr in cells(name, dim):
            flag = "  <== LOSING" if net < 0 else ""
            print(f"   {'/'.join(k):44s} legs={n:3d} net={net:+12,.2f} "
                  f"WR={wr:5.1f}%{flag}")
    print("-- FULL CROSS cells with >=10 legs and net<0 (LOSING CELLS):")
    big = [r for r in cell_rows if r["book"] == name and r["legs"] >= 10
           and r["net"] < 0]
    if big:
        for r in big:
            print(f"   {r['side']}/{r['regime']}/{r['bucket']}/{r['exit_class']}"
                  f" legs={r['legs']} net={r['net']:+,.2f} WR={r['win_rate']}%")
    else:
        print("   (none)")
    print("-- FULL CROSS cells with >=6 legs and net<0 (watch list):")
    for r in cell_rows:
        if r["book"] == name and 6 <= r["legs"] < 10 and r["net"] < 0:
            print(f"   {r['side']}/{r['regime']}/{r['bucket']}/{r['exit_class']}"
                  f" legs={r['legs']} net={r['net']:+,.2f} WR={r['win_rate']}%")

# ---------------- parallel books: STACK + REGIME-REV -----------------------
cal_bank = sorted({r["date"] for r in csv.DictReader(
    open(TR / "november_regime_days_bank.csv"))
    if "2026-01-01" <= r["date"] <= "2026-10-31"})
print(f"\nBank regime-CSV Jan-Oct days: {len(cal_bank)}")
stack_day = defaultdict(float)
for l in stack: stack_day[l["date"]] += l["net"]
rr = [r for r in csv.DictReader(open(TR / "november_regime_family_trades.csv"))]
rr_jan_oct = [r for r in rr if r["book"] == "BANK_real"]
rr_day = defaultdict(float)
for r in rr_jan_oct: rr_day[r["date"]] += float(r["net"])
assert round(sum(rr_day.values()), 2) == 15872.00

def day_counts(daymap, cal):
    g = sum(1 for d in cal if daymap.get(d, 0.0) > 0)
    r_ = sum(1 for d in cal if daymap.get(d, 0.0) < 0)
    return g, r_, len(cal) - g - r_

comb_day = {d: stack_day.get(d, 0.0) + rr_day.get(d, 0.0) for d in cal_bank}
for lab, dm in (("STACK", stack_day), ("REGIME-REV", rr_day),
                ("PARALLEL COMBINED", comb_day)):
    g, r_, nt = day_counts(dm, cal_bank)
    print(f"PARALLEL Jan-Oct {lab}: total {sum(dm.get(d,0.0) for d in cal_bank):+,.2f}"
          f" days G{g}/R{r_}/NT{nt} (of {len(cal_bank)})")
out["parallel_janoct"] = {
    lab: dict(total=round(sum(dm.get(d, 0.0) for d in cal_bank), 2),
              green=day_counts(dm, cal_bank)[0], red=day_counts(dm, cal_bank)[1],
              no_trade=day_counts(dm, cal_bank)[2])
    for lab, dm in (("stack", stack_day), ("regime_rev", rr_day),
                    ("combined", comb_day))}

# November parallel: 9 trading days Nov 2-13
nov_days = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
s_nov = defaultdict(float)
for r in csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv")):
    if r["net_inr"]:
        s_nov[r["date"]] += float(r["net_inr"])
assert round(sum(s_nov.values()), 2) == -2680.00, sum(s_nov.values())
rr_nov = defaultdict(float)
for r in rr:
    if r["book"] == "BANK_nov": rr_nov[r["date"]] += float(r["net"])
assert round(sum(rr_nov.values()), 2) == 2141.00
comb_nov = {d: s_nov.get(d, 0.0) + rr_nov.get(d, 0.0) for d in nov_days}
print("\nPARALLEL November day-by-day:")
for d in nov_days:
    print(f"   {d}: stack {s_nov.get(d,0.0):+9,.2f}  regime-rev "
          f"{rr_nov.get(d,0.0):+9,.2f}  combined {comb_nov[d]:+9,.2f}")
for lab, dm in (("STACK", s_nov), ("REGIME-REV", rr_nov),
                ("PARALLEL COMBINED", comb_nov)):
    g, r_, nt = day_counts(dm, nov_days)
    print(f"PARALLEL Nov {lab}: total {sum(dm.get(d,0.0) for d in nov_days):+,.2f}"
          f" days G{g}/R{r_}/NT{nt}")
out["parallel_november"] = {
    lab: dict(total=round(sum(dm.get(d, 0.0) for d in nov_days), 2),
              green=day_counts(dm, nov_days)[0], red=day_counts(dm, nov_days)[1],
              no_trade=day_counts(dm, nov_days)[2])
    for lab, dm in (("stack", s_nov), ("regime_rev", rr_nov),
                    ("combined", comb_nov))}
out["parallel_november_days"] = {d: dict(
    stack=s_nov.get(d, 0.0), regime_rev=rr_nov.get(d, 0.0),
    combined=comb_nov[d]) for d in nov_days}

json.dump(out, open(TR / "november_books_fix_phase1_partial.json", "w"), indent=1)
print("\nPHASE 1 DONE — anatomy legs/cells CSVs written")
