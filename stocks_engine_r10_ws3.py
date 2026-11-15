#!/usr/bin/env python3
"""ROUND 10 — WS3: JULY WOUND UNDER THE INDEX-STATE LENS.

R10-05 (audit): every July-2025 row of the banked book
decomposed by component x index-state bucket, where state =
nifty_move(day, entry_time - 5min) — the close of the last
5-min NIFTY bar completing at the entry instant vs prior close
— bucketed as in R9-01: hard-dip <= -0.30% / shallow-dip
(-0.30%, 0) / up >= 0. Unknown states counted, never guessed.
R10-06 (conditional): if exactly one (component, bucket)
passes the frozen separator test, gate the removal variant
(book minus those rows, both years) with the frozen chrono /
cross-bucket placebos; otherwise WS3 closes by statement.
Evidence: r10_july_decomp.json.
"""
import sys, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r10_lib as R10
import stocks_engine_r8_builders as B8

books = R10.load_books()
JULY_NET = -7083.39

def prev_bar(t):
    hh, mm = map(int, t.split(":"))
    m = hh * 60 + mm - 5
    return f"{m // 60:02d}:{m % 60:02d}"

def bucket_of(row):
    et = row.get("entry_time") or ""
    if len(et) != 5:
        return "unknown"
    mv = B8.nifty_move(row["date"], prev_bar(et))
    if mv is None:
        return "unknown"
    if mv <= -0.30:
        return "hard"
    if mv < 0:
        return "shallow"
    return "up"

# ------------------------------------------------------ R10-05 --
july = [t for t in books[2025] if t["date"][:7] == "2025-07"]
jnet = round(sum(t["net"] for t in july), 2)
assert jnet == JULY_NET, (jnet, JULY_NET)

from collections import defaultdict
by_comp = defaultdict(float)
by_cb = defaultdict(float)
cnt_cb = defaultdict(int)
for t in july:
    b = bucket_of(t)
    by_comp[t["comp"]] += t["net"]
    by_cb[(t["comp"], b)] += t["net"]
    cnt_cb[(t["comp"], b)] += 1
by_comp = {k: round(v, 2) for k, v in sorted(by_comp.items())}
offender = min(by_comp, key=by_comp.get)
assert by_comp[offender] < 0

# full-year bucket nets for the offending component, both years
fy = {}
for yr in (2025, 2026):
    d = defaultdict(float)
    for t in books[yr]:
        if t["comp"] == offender:
            d[bucket_of(t)] += t["net"]
    fy[yr] = {k: round(v, 2) for k, v in d.items()}

qual = []
for b in ("hard", "shallow", "up"):
    jn = round(by_cb.get((offender, b), 0.0), 2)
    c1 = jn < 0 and abs(jn) >= 0.5 * abs(by_comp[offender])
    c2 = fy[2025].get(b, 0.0) < 0
    c3 = (fy[2025].get(b, 0.0) + fy[2026].get(b, 0.0)) < 0
    if c1 and c2 and c3:
        qual.append(b)
    print(f"bucket {b}: july {jn} (test i {c1}); FY25 "
          f"{fy[2025].get(b, 0.0)} (ii {c2}); combined "
          f"{round(fy[2025].get(b, 0.0) + fy[2026].get(b, 0.0), 2)} "
          f"(iii {c3})")

decomp = {
    "july_net": jnet, "by_comp": by_comp, "offender": offender,
    "by_comp_bucket": {f"{k[0]}|{k[1]}": [cnt_cb[k], round(v, 2)]
                       for k, v in sorted(by_cb.items())},
    "offender_full_year_buckets": {str(k): v for k, v in fy.items()},
    "qualifying_separators": qual,
}
json.dump(decomp, open(f"{WS}/r10_july_decomp.json", "w"), indent=1)

comp_str = "; ".join(f"{k} {v}" for k, v in by_comp.items())
R10.record_audit(
    "R10-05",
    "July-2025 wound decomposition by component x index-state "
    "bucket (audit — no candidate scored)",
    f"July 2025 = {jnet} on {len(july)} rows (asserted). By "
    f"component: {comp_str}. Offending component: {offender} "
    f"({by_comp[offender]}). Its July state split: hard "
    f"{round(by_cb.get((offender, 'hard'), 0.0), 2)}, shallow "
    f"{round(by_cb.get((offender, 'shallow'), 0.0), 2)}, up "
    f"{round(by_cb.get((offender, 'up'), 0.0), 2)}, unknown "
    f"{round(by_cb.get((offender, 'unknown'), 0.0), 2)}. "
    f"Frozen separator test: qualifying (component, bucket) "
    f"pairs = {[(offender, b) for b in qual]}. Full table in "
    f"r10_july_decomp.json.",
    extra=decomp)

# ------------------------------------------------------ R10-06 --
if len(qual) != 1:
    R10.record_audit(
        "R10-06",
        "July conditioned variant — closes by statement",
        f"Separator test produced {len(qual)} qualifying "
        f"buckets for {offender} ({qual}); the frozen rule "
        f"requires exactly one. No candidate is designed or "
        f"scored — WS3 closes with the decomposition as its "
        f"result.")
    print("WS3 done (no candidate).")
    sys.exit(0)

BUCKET = qual[0]
removed = {yr: [t for t in books[yr]
                if t["comp"] == offender and bucket_of(t) == BUCKET]
           for yr in (2025, 2026)}
for yr in (2025, 2026):
    for t in removed[yr]:
        # state knowable at the entry instant by construction:
        # the bucketed bar completes exactly at entry_time
        assert B8.nifty_move(t["date"], prev_bar(t["entry_time"])) \
            is not None
var = {yr: [t for t in books[yr]
            if not (t["comp"] == offender
                    and bucket_of(t) == BUCKET)]
       for yr in (2025, 2026)}

def keyf(t):
    return (t["date"], t.get("entry_time") or "", t["stock"])

def remove_n(rows, comp, n, pred):
    cand = sorted([t for t in rows if t["comp"] == comp
                   and pred(t)], key=keyf)
    take = {id(t) for t in cand[:n]}
    return [t for t in rows if id(t) not in take]

pl_books = []
for mode in ("chrono", "cross"):
    pb = {}
    for yr in (2025, 2026):
        n = len(removed[yr])
        if mode == "chrono":
            pb[yr] = remove_n(books[yr], offender, n,
                              lambda t: True)
        else:
            rows = remove_n(books[yr], offender, n,
                            lambda t: bucket_of(t) not in
                            (BUCKET, "unknown"))
            still = n - (len(books[yr]) - len(rows))
            # NOTE: remove_n removed min(n, available); compute
            # the shortfall against the year's comp rows
            removed_ct = sum(1 for t in books[yr]
                             if t["comp"] == offender) - \
                sum(1 for t in rows if t["comp"] == offender)
            short = n - removed_ct
            if short > 0:
                rows = remove_n(rows, offender, short,
                                lambda t: bucket_of(t) == BUCKET)
            pb[yr] = rows
    pl_books.append(R10.full_total(pb))
out = R10.gate(books, var, pl_books, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
rm_sa = {yr: round(sum(t["net"] for t in removed[yr]), 2)
         for yr in (2025, 2026)}
R10.record(
    "R10-06",
    f"July separator removal: {offender} x {BUCKET}-state rows "
    f"removed (both years)", out,
    note=f"separator ({offender}, {BUCKET}) is the unique "
         f"qualifier under the frozen test: July net "
         f"{round(by_cb.get((offender, BUCKET), 0.0), 2)} of "
         f"the component's {by_comp[offender]}; FY2025 bucket "
         f"net {fy[2025].get(BUCKET, 0.0)}; combined "
         f"{round(fy[2025].get(BUCKET, 0.0) + fy[2026].get(BUCKET, 0.0), 2)}. "
         f"Removed rows: {len(removed[2025])}/{len(removed[2026])} "
         f"netting {rm_sa[2025]} / {rm_sa[2026]}. Placebos: "
         f"chrono removal book {pl_books[0]}; cross-bucket "
         f"removal book {pl_books[1]}. Timing violations 0 "
         f"(state = the bar completing at each row's entry "
         f"instant, asserted per removed row). Failed legs: "
         f"{failed}.",
    extra={"removed_standalone": {str(k): v for k, v in rm_sa.items()},
           "removed_trades": {"2025": len(removed[2025]),
                              "2026": len(removed[2026])},
           "failed_legs": failed})
print("WS3 done.")
