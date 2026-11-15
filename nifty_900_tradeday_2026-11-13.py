#!/usr/bin/env python3
"""NIFTY Rs900-PER-TRADE-DAY VERIFICATION - 2026-11-13 (owner bar 18:31 IST).

Owner's bar: least minimum AVERAGE return Rs900 per day counted ONLY on
days a trade happens (trade-days); no-trade days excluded entirely.

Basis: Nifty index options, premium per 1 lot (65), cost Rs220/trade inside
nets (harness replay), UNIQUE-ONCE, weekly/monthly expiries per each book's
frozen spec. BUYING only (all books are long-premium constructions).
Offline verification only - no running book or job is touched.

Books measured (leg sets rebuilt deterministically from the stored
harnesses + the frozen r11 component dump, anchors asserted to the paisa
against the gated record of tuning_nifty_2026-11-12):
  DEC-S1   = A + B + C assembly (r11 spec)          +91,168.50 / 97 legs
  TUNED v1 = DEC-S1 - B PE        (EVE-07)          +103,050.25 / 74 legs
  TUNED v2 = DEC-S1 - B PE/A CE/C CE (EVE-11)       +115,950.75 / 59 legs
DEC-S1 is RETIRED (proven B-PE leak) - measured for completeness only.

Controls per book (all recomputed on the trade-day basis):
  timing audit (audit_exact), NC count, independent CSV re-sum,
  month table on BOTH bases (per calendar trading day / per trade-day),
  halves on the trade-day basis, trade-day distribution,
  placebo = shifted-entry family (delay_bars 2..12, incl. canonical
  shift30 = 6 bars) scored on the same days -> trade-day-average
  percentile of the real book inside that family,
  ex-top-3 on the trade-day basis (drop 3 best trade-DAYS; legs variant
  also reported).
Calendar: volrix/nifty_daily_2019_2026.csv (205 trading days Jan-Oct 2026,
the programme-standard calendar used by daily_earner_nifty_build.py).
"""
import sys, json, csv, statistics
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r8_harness as R8
import nifty_engine_r6_harness as R6
from nifty_engine_r2_harness import audit_exact

TR = Path.home() / "workspace/trading"
GEOM = dict(R7.STANDING_GEOM)  # stop -50, BE arm +50, tgt1 +90, lock +60, tgt2 +175, SQ 15:20
BAR = 900.0

# ---------------- trading calendar (programme standard) ---------------------
daily = list(csv.DictReader(open(TR / "volrix/nifty_daily_2019_2026.csv")))
TD = [r["date"] for r in daily if "2026-01-01" <= r["date"] <= "2026-10-31"]
CAL = defaultdict(int)
for d in TD: CAL[d[:7]] += 1
assert len(TD) == 205, len(TD)
MONTHS = [f"2026-{m:02d}" for m in range(1, 11)]

# ---------------- assembly (verbatim from tuning_nifty_2026-11-12.py) -----
A = R7.standing_legs()
B, _fex = R8.gap_fade_legs_r8(threshold=0.005, entry_time="10:05",
                              with_trend=False, exclude_keys=R7.keys_of(A))
C, _eex = R8.expiry_sleeve_legs(R7.keys_of(A) | R7.keys_of(B))
DECS1 = A + B + C
dump = json.loads((TR / "nifty_engine_r11_decs1_legs.json").read_text())
tagmap = {}
for d in dump:
    tagmap[(d["date"], d["direction"], d["entry_time"], int(d["strike"]),
            d["expiry"])] = d["component"]
def comp(l):
    return tagmap[(l["date"], l["direction"], l["entry_time"],
                   int(l["strike"]), l["expiry"])]
for l in DECS1:
    l["_comp"] = comp(l)
from collections import Counter
split = Counter((comp(l), l["direction"]) for l in DECS1)
assert len(DECS1) == 97
assert split[("B", "PE")] == 23 and split[("B", "CE")] == 26
assert split[("A", "PE")] == 25 and split[("A", "CE")] == 10
assert split[("C", "PE")] == 8 and split[("C", "CE")] == 5

def is_bpe(l): return comp(l) == "B" and l["direction"] == "PE"
def is_ace(l): return comp(l) == "A" and l["direction"] == "CE"
def is_cce(l): return comp(l) == "C" and l["direction"] == "CE"
V1 = [l for l in DECS1 if not is_bpe(l)]
V2 = [l for l in DECS1 if not (is_bpe(l) or is_ace(l) or is_cce(l))]
assert len(V1) == 74 and len(V2) == 59

ANCHORS = {"DEC-S1": 91168.50, "TUNED_v1": 103050.25, "TUNED_v2": 115950.75}

# ---------------- statistics ------------------------------------------------
def day_map(res):
    byd = defaultdict(float)
    for r in res: byd[r["date"]] += r["net"]
    return dict(byd)

def book_stats(name, legs):
    res, nc, nc_legs = R6.score_r6(legs, geom=geom_of(name))
    total = round(sum(r["net"] for r in res), 2)
    assert total == ANCHORS[name], (name, total, ANCHORS[name])
    assert nc == 0, (name, nc, nc_legs)
    audit = audit_exact(legs)
    assert audit["violations"] == 0, (name, audit)
    byd = day_map(res)
    tdays = sorted(byd)
    n_td = len(tdays)
    wins = sum(1 for r in res if r["net"] > 0)
    # month table, both bases
    mt = {}
    cum = 0.0
    for m in MONTHS:
        mres = [r for r in res if r["date"][:7] == m]
        mnet = round(sum(r["net"] for r in mres), 2)
        cum = round(cum + mnet, 2)
        mtd_days = len({r["date"] for r in mres})
        mt[m] = {"net": mnet, "cum": cum, "legs": len(mres),
                 "cal_days": CAL[m], "trade_days": mtd_days,
                 "per_cal_day": round(mnet / CAL[m], 2),
                 "per_trade_day": round(mnet / mtd_days, 2) if mtd_days else None}
    # halves on trade-day basis
    halves = {}
    for lab, pred in (("Jan-May", lambda d: d[:7] <= "2026-05"),
                      ("Jun-Oct", lambda d: d[:7] >= "2026-06")):
        h = {d: v for d, v in byd.items() if pred(d)}
        halves[lab] = {"total": round(sum(h.values()), 2), "trade_days": len(h),
                       "per_trade_day": round(sum(h.values()) / len(h), 2) if h else None}
    dayvals = [byd[d] for d in tdays]
    # ex-top-3 trade-DAYS
    top3d = sorted(dayvals, reverse=True)[:3]
    ex3d_total = round(total - sum(top3d), 2)
    ex3d_avg = round(ex3d_total / (n_td - 3), 2) if n_td > 3 else None
    # ex-top-3 legs (reference)
    top3l = sorted((r["net"] for r in res), reverse=True)[:3]
    ex3l = round(total - sum(top3l), 2)
    # independent re-sum via CSV round-trip
    tmp = TR / f"nifty900_tmp_{name}.csv"
    with open(tmp, "w", newline="") as f:
        w = csv.writer(f); w.writerow(["date", "net"])
        for r in res: w.writerow([r["date"], r["net"]])
    resum = round(sum(float(r["net"]) for r in csv.DictReader(open(tmp))), 2)
    tmp.unlink()
    assert resum == total, (name, resum, total)
    # placebo: shifted-entry family, trade-day average statistic
    pl_avgs = {}
    for db in (2, 3, 4, 5, 6, 7, 8, 9, 10, 12):
        pl, pnc, _ = R6.score_r6(legs, geom=geom_of(name), delay_bars=db)
        assert pnc == 0, (name, db, pnc)
        pbyd = day_map(pl)
        pl_avgs[db] = {"total": round(sum(pbyd.values()), 2),
                       "trade_days": len(pbyd),
                       "per_trade_day": round(sum(pbyd.values()) / len(pbyd), 2)}
    real_avg = round(total / n_td, 2)
    below = sum(1 for v in pl_avgs.values() if v["per_trade_day"] < real_avg)
    pct = round(100.0 * below / len(pl_avgs), 1)
    return {
        "name": name, "legs": len(res),
        "total": total, "trade_days": n_td,
        "per_trade_day": real_avg,
        "per_leg": round(total / len(res), 2),
        "win_rate_pct": round(100.0 * wins / len(res), 1),
        "ft_pct": round(100.0 * sum(r["ft"] for r in res) / len(res), 1),
        "month_table": mt,
        "red_months_monthly_net": [m for m in MONTHS if mt[m]["net"] < 0],
        "red_month_ends_cum": [m for m in MONTHS if mt[m]["cum"] < 0],
        "halves_tradeday": halves,
        "tradeday_distribution": {
            "share_ge_900_pct": round(100.0 * sum(1 for v in dayvals if v >= 900) / n_td, 1),
            "median": round(statistics.median(dayvals), 2),
            "worst": round(min(dayvals), 2), "best": round(max(dayvals), 2),
            "losing_tradedays": sum(1 for v in dayvals if v < 0)},
        "ex_top3_tradedays": {"total": ex3d_total, "per_trade_day": ex3d_avg,
                              "dropped_day_nets": [round(x, 2) for x in top3d]},
        "ex_top3_legs_total": ex3l,
        "placebo_shift30": pl_avgs[6],
        "placebo_family": {str(k): v for k, v in pl_avgs.items()},
        "placebo_percentile_tradeday_avg": pct,
        "timing_audit_violations": audit["violations"],
        "not_computed": nc, "resum_ok": True,
        "trade_day_frequency": f"{n_td} trade-days / 205 calendar trading days "
                               f"({round(100.0*n_td/205,1)}%)",
        "legs_detail": [{"date": r["date"], "direction": r["direction"],
                         "entry_time": r["entry_time"], "strike": r["strike"],
                         "expiry": r["expiry"], "net": r["net"],
                         "exit_reason": r.get("exit_reason")} for r in
                        sorted(res, key=lambda x: x["date"])],
    }

def geom_of(name):
    return GEOM

out = {"bar": BAR, "calendar_trading_days": 205,
       "cal_days_by_month": {m: CAL[m] for m in MONTHS}, "books": {}}
for name, legs in (("DEC-S1", DECS1), ("TUNED_v1", V1), ("TUNED_v2", V2)):
    s = book_stats(name, legs)
    out["books"][name] = s
    print(f"{name}: legs {s['legs']} total {s['total']:+,.2f} "
          f"trade-days {s['trade_days']} per-trade-day {s['per_trade_day']:+,.2f} "
          f"per-leg {s['per_leg']:+,.2f} WR {s['win_rate_pct']}% "
          f"placebo-pct {s['placebo_percentile_tradeday_avg']} "
          f"red-months {s['red_months_monthly_net']}")

(TR / "nifty_900_tradeday_2026-11-13_results.json").write_text(
    json.dumps(out, indent=1))
print("WROTE nifty_900_tradeday_2026-11-13_results.json")
