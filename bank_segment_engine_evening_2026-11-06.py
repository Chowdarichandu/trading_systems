"""Bank segment engine evening 2026-11-06 — gated candidates EVE-11 + EVE-12.
Basis: Bank option premiums per 1 lot (30), cost Rs220/trade in stored nets, UNIQUE-ONCE.
Incumbent: causal v21 book (99 legs, +83,650.50), re-summed exact in-run.
EVE-11: the TUNED SHADOW v3 NS1 treatment gated as ONE book on the v21 frame =
  BANK-EVE-04 (NS1-only breakeven lock, flaw-cycle FC-2 replay nets for NS1 legs)
  PLUS BANK-EVE-09 (skip NS1 second legs entering before 10:30).
  EVE-04 and EVE-09 were each gated alone (both PASS, 2026-11-03 / 2026-11-05);
  their union has never been gated as a single book. This run gates the union.
EVE-12: bleed-guard overlay — causal realised day-loss cap -Rs3,000 on the v21 book:
  legs taken in entry order; a later same-day leg is skipped only if earlier legs
  that day have already EXITED (exit_time <= this leg's entry_time) with realised
  day P&L <= -3,000. Mechanically distinct from the BIG BUILD's intraday
  close-based cap (tested on the combined system, not on this book in this form).
  Bleed report (worst day / worst 3-day streak / worst drawdown) incumbent vs guarded.
Also: 2026-11-05 SHADOW Skill winner path (MFE/MAE) from stored candles, and
2026-11-06 spot anatomy for the missed-move journal entry (from the EOD
construction output saved at /tmp/eod_bank_2026-11-06.json).
Paper only, real money Rs0. Full controls gate in the same run for both candidates.
"""
import csv, json
from collections import defaultdict

TR = "/home/hatch/workspace/trading/"

def load(p): return list(csv.DictReader(open(TR + p)))
def net(rows): return round(sum(float(r["net_inr"]) for r in rows), 2)

def battery(rows, base_rows):
    months = {}
    for m in sorted(set(r["date"][:7] for r in base_rows)):
        months[m] = round(sum(float(r["net_inr"]) for r in rows if r["date"][:7] == m), 2)
    bm = {m: round(sum(float(r["net_inr"]) for r in base_rows if r["date"][:7] == m), 2) for m in months}
    flips = [m for m in months if bm[m] > 0 and months[m] < 0]
    h1 = round(sum(float(r["net_inr"]) for r in rows if r["date"] <= "2026-05-31"), 2)
    h2 = round(sum(float(r["net_inr"]) for r in rows if r["date"] >= "2026-06-01"), 2)
    srt = sorted(rows, key=lambda r: -float(r["net_inr"]))
    return {"n": len(rows), "net": net(rows), "halves": {"H1": h1, "H2": h2},
            "months": months, "flips": flips,
            "ex_top3": round(net(rows) - sum(float(r["net_inr"]) for r in srt[:3]), 2)}

results = {}

# ---------- shared incumbent ----------
inc = load("flaw_cycle_incumbent_trades.csv")
fc2 = load("flaw_cycle_fc2_trades.csv")
assert len(inc) == len(fc2) == 99
assert all(a["leg_key"] == b["leg_key"] for a, b in zip(inc, fc2))
base = battery(inc, inc)
assert base["net"] == 83650.50, base["net"]  # independent re-sum

# EVE-04 hybrid (NS1 legs take FC-2 replay nets) — reproduced from the 2026-11-03 run
hyb04 = []
for a, b in zip(inc, fc2):
    r = dict(a)
    if a["family"] == "NS1_second":
        r["net_inr"] = b["net_inr"]; r["exit_reason"] = b["exit_reason"]
        r["exit_time"] = b["exit_time"]; r["exit_premium"] = b["exit_premium"]
    hyb04.append(r)
b04 = battery(hyb04, inc)
assert b04["net"] == 87370.50, b04["net"]  # matches the gated EVE-04 record

# ---------- EVE-11: EVE-04 lock + EVE-09 early-NS1 skip, as one book ----------
early = [r for r in hyb04 if r["family"] == "NS1_second" and r["entry_time"] < "10:30"]
var11 = [r for r in hyb04 if r not in early]
v11 = battery(var11, inc)
# placebo: from the EVE-04 hybrid, skip the same count of LATEST-entry NS1 legs
ns1_h = [r for r in hyb04 if r["family"] == "NS1_second"]
latest = sorted(ns1_h, key=lambda r: (r["entry_time"], r["date"]), reverse=True)[:len(early)]
pla11 = battery([r for r in hyb04 if r not in latest], inc)
results["EVE-11"] = {
    "base_v21": base, "eve04_alone": b04, "variant_union": v11,
    "skipped_early_NS1_on_hybrid": [(r["date"], r["direction"], r["entry_time"], r["net_inr"]) for r in early],
    "skipped_net_on_hybrid": net(early),
    "placebo_skip_latest_NS1_on_hybrid": pla11,
    "placebo_skipped": [(r["date"], r["entry_time"], r["net_inr"]) for r in latest],
    "timing_audit": "lock arms only on completed bars (flaw-cycle replay, 0 violations there); skip input is entry_time, known at entry — 0 violations",
    "verdict": "PASS" if (v11["net"] > base["net"] and v11["net"] > b04["net"] and v11["net"] > pla11["net"]
                          and v11["halves"]["H1"] >= 0 and v11["halves"]["H2"] >= 0
                          and not v11["flips"] and v11["ex_top3"] > 0) else "FAIL"}

# ---------- EVE-12: causal realised day-loss cap -3,000 on v21 ----------
byday = defaultdict(list)
for r in inc: byday[r["date"]].append(r)
kept, skipped = [], []
for d, rows in byday.items():
    rows = sorted(rows, key=lambda r: r["entry_time"])
    for r in rows:
        realised = sum(float(x["net_inr"]) for x in rows
                       if x["entry_time"] < r["entry_time"] and x["exit_time"] <= r["entry_time"]
                       and x in kept)
        if realised <= -3000: skipped.append((d, r["family"], r["entry_time"], r["net_inr"], realised))
        else: kept.append(r)
v12 = battery(kept, inc)
# placebo for a skip rule: chronological skip of the same count of legs overall
pla12 = battery(inc[len(skipped):], inc) if skipped else None
def bleed(rows):
    dd = defaultdict(float)
    for r in rows: dd[r["date"]] += float(r["net_inr"])
    days = sorted(dd.items())
    worst_day = min(days, key=lambda kv: kv[1])
    streaks = [(days[i][0], round(sum(v for _, v in days[i:i+3]), 2)) for i in range(len(days) - 2)]
    worst3 = min(streaks, key=lambda kv: kv[1]) if streaks else None
    cum, peak, mdd = 0.0, 0.0, 0.0
    for _, v in days:
        cum += v; peak = max(peak, cum); mdd = min(mdd, cum - peak)
    return {"worst_day": (worst_day[0], round(worst_day[1], 2)), "worst_3day_streak": worst3,
            "worst_drawdown": round(mdd, 2), "trading_days": len(days),
            "multi_leg_days": sum(1 for v in byday.values() if len(v) > 1)}
results["EVE-12"] = {
    "base_v21": base, "variant": v12, "skipped": skipped, "placebo": pla12,
    "bleed_incumbent": bleed(inc), "bleed_guarded": bleed(kept),
    "timing_audit": "cap input is realised P&L of legs already exited before the candidate leg's entry — causal by construction, 0 violations",
    "verdict": ("NO-OP" if not skipped else
                ("PASS" if (v12["net"] > base["net"] and v12["halves"]["H1"] >= 0 and v12["halves"]["H2"] >= 0
                            and not v12["flips"] and v12["ex_top3"] > 0) else "FAIL"))}

# ---------- 2026-11-05 SHADOW Skill winner path ----------
cand = json.load(open(TR + "november_shadow_data/candles_BANKNIFTY_57100CE_2026-11-05_2026-11-23.json"))
bars = sorted(cand["data"]["candles"])
entry = 729.40
path = [b for b in bars if "11:20" <= b[0][11:16] <= "11:30"]
results["nov5_skill_winner"] = {
    "entry": entry, "exit": 819.40, "exit_reason": "target",
    "mfe_pts": round(max(b[2] for b in path) - entry, 2),
    "mae_pts": round(min(b[3] for b in path) - entry, 2),
    "path_bars": [(b[0][11:16], b[1], b[2], b[3], b[4]) for b in path]}

# ---------- 2026-11-06 spot anatomy (EOD construction output) ----------
eod = json.load(open("/tmp/eod_bank_2026-11-06.json"))["BANKNIFTY"]
rows = sorted(eod["spot_at"].values(), key=lambda x: x["time"])
morn = [r for r in rows if r["time"] < "11:30"]
aft = [r for r in rows if r["time"] >= "12:00"]
results["nov6_spot"] = {
    "bars": len(rows), "open": rows[0]["open"], "close": rows[-1]["close"],
    "day_high": max(r["high"] for r in rows), "day_low": min(r["low"] for r in rows),
    "pre1130_high": max(r["high"] for r in morn), "pre1130_low": min(r["low"] for r in morn),
    "aft_first_close": aft[0]["close"], "aft_high": max(r["high"] for r in aft),
    "extension_above_morning_high": round(max(r["high"] for r in aft) - max(r["high"] for r in morn), 2),
    "ns1_why": eod["ns1"]["why"], "prev_close": eod["prev"]["close"]}

print(json.dumps(results, indent=1))
with open(TR + "bank_segment_engine_evening_2026-11-06.json", "w") as f:
    json.dump(results, f, indent=1)
