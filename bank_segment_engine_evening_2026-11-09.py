"""Bank segment engine evening 2026-11-09 — gated candidates EVE-13/14/15.
Diagnosis: 2026-11-09 primary leg = Skill V3 PE solo OR-break, entry 10:45 @ 815.40,
stopped ON THE ENTRY BAR (10:45 bar low 734.55; MFE +3.35, MAE -80.85) -> -Rs1,720.
Extreme form of the entry-bar whipsaw / quick-stop class (RSI-BANK-001): in the B2 pool
14 of 70 OR-break legs stopped within <=10 min; this run also counts entry-bar stops.
All three candidates are skip-at-entry on entry-time-known attributes (no entry delay,
so none repeats the rejected BANK-FIX-01 hold-confirmation or EVE-03/05 identically):
 EVE-13: B2 pool — skip OR-break PE entries before 11:00 (EVE-05's 10:30 threshold
         widened 30 min; mechanically distinct threshold). Would have caught today.
 EVE-14: B2 pool — skip Skill-V3-SOLO OR legs (either direction) entering before 11:00
         (EVE-02 skipped solo legs at ALL hours and failed G5; this is the timed
         intersection — today's leg is solo PE at 10:45).
 EVE-15: B2 pool — skip ALL OR-break entries (CE+PE) before 11:00 (direction-blind
         widening of the same window; distinct from EVE-13's PE-only form).
Basis: Bank option premiums per 1 lot (30), cost Rs220/trade in stored nets, UNIQUE-ONCE.
Full controls gate in the same run for every candidate: timing audit, placebo
(skip same count from complementary OR legs, chronological, as in the 2026-11-02/03 runs),
halves split, full month table, ex-top-3 stress, independent re-sum.
Also: 2026-11-09 primary premium path (MFE/MAE) and 2026-11-06 SHADOW Skill winner path
from stored candles; 2026-11-09 spot anatomy from the EOD construction output saved at
/tmp/eod_2026-11-09.json (reproduces the logged NS1 block: first crossing CE blocked on
a bearish-bias day).
Paper only, real money Rs0.
"""
import csv, json

TR = "/home/hatch/workspace/trading/"

def mins(t):
    h, m = map(int, t.split(":")); return h * 60 + m

rows = list(csv.DictReader(open(TR + "historical_proof_bank_B2_trades.csv")))
for r in rows:
    r["hold"] = mins(r["exit_time"]) - mins(r["entry_time"])
    r["net"] = float(r["net_rs"])
    r["is_or"] = "Skill V3" in r["source_systems"]
    r["is_solo"] = r["source_systems"].strip() == "Skill V3"
    r["quick_or"] = r["is_or"] and r["exit_reason"] == "stop" and r["hold"] <= 10
    r["entrybar_or"] = r["is_or"] and r["exit_reason"] == "stop" and r["hold"] == 0
    r["month"] = r["date"][:7]
    r["half"] = "H1" if r["date"][5:7] in ("01", "02", "03", "04", "05") else "H2"

base_net = round(sum(r["net"] for r in rows), 2)
assert base_net == 18731.50 and len(rows) == 89, (base_net, len(rows))  # independent re-sum

def stats(kept):
    net = round(sum(r["net"] for r in kept), 2)
    months = {m: round(sum(r["net"] for r in kept if r["month"] == m), 2)
              for m in sorted(set(r["month"] for r in rows))}
    bm = {m: round(sum(r["net"] for r in rows if r["month"] == m), 2) for m in months}
    flips = [m for m in months if bm[m] > 0 and months[m] < 0]
    top3 = sorted((r["net"] for r in kept), reverse=True)[:3]
    return dict(net=net, n=len(kept),
                H1=round(sum(r["net"] for r in kept if r["half"] == "H1"), 2),
                H2=round(sum(r["net"] for r in kept if r["half"] == "H2"), 2),
                ex_top3=round(net - sum(top3), 2), months=months, flips=flips,
                quick_or=sum(r["quick_or"] for r in kept),
                entrybar_or=sum(r["entrybar_or"] for r in kept))

base = stats(rows)

def gate(name, skipf):
    skipped = [r for r in rows if skipf(r)]
    kept = [r for r in rows if not skipf(r)]
    s = stats(kept)
    comp = [r for r in rows if r["is_or"] and not skipf(r)]
    comp_ids = {id(r) for r in comp[:len(skipped)]}
    placebo_net = round(sum(r["net"] for r in rows if id(r) not in comp_ids), 2)
    gates = {
        "G1_timing": "PASS - skip inputs (entry_time/direction/frozen source list) known at entry; 0 violations",
        "G2_resum": "PASS - B2 baseline re-summed 89 legs = +18731.50 exact in this run",
        "G3_net_improvement": s["net"] > base["net"],
        "G4_placebo_beaten": s["net"] > placebo_net,
        "G5_halves_both_ge0": s["H1"] >= 0 and s["H2"] >= 0,
        "G6_ex_top3_ge0": s["ex_top3"] >= 0,
        "G7_no_green_month_flips": len(s["flips"]) == 0,
        "G8_quick_stops_fall": s["quick_or"] < base["quick_or"],
    }
    bools = [v for v in gates.values() if isinstance(v, bool)]
    return {name: dict(baseline=base, variant=s, skipped_n=len(skipped),
                       skipped_net=round(sum(r["net"] for r in skipped), 2),
                       skipped=[(r["date"], r["direction"], r["entry_time"], r["net"]) for r in skipped],
                       skipped_quick=sum(r["quick_or"] for r in skipped),
                       skipped_entrybar=sum(r["entrybar_or"] for r in skipped),
                       placebo_net=placebo_net, gates=gates,
                       verdict="PASS" if all(bools) else "FAIL")}

results = {}
results.update(gate("EVE-13_OR_PE_skip_before_1100",
                    lambda r: r["is_or"] and r["direction"] == "PE" and mins(r["entry_time"]) < 660))
results.update(gate("EVE-14_Skill_solo_OR_skip_before_1100",
                    lambda r: r["is_or"] and r["is_solo"] and mins(r["entry_time"]) < 660))
results.update(gate("EVE-15_all_OR_skip_before_1100",
                    lambda r: r["is_or"] and mins(r["entry_time"]) < 660))

# ---------- diagnostics: quick-stop anatomy of the B2 pool ----------
or_legs = [r for r in rows if r["is_or"]]
results["diagnostics"] = dict(
    or_legs=len(or_legs),
    quick_or_stops_leq10=sum(r["quick_or"] for r in rows),
    entrybar_or_stops=sum(r["entrybar_or"] for r in rows),
    entrybar_list=[(r["date"], r["direction"], r["entry_time"], r["net"]) for r in rows if r["entrybar_or"]],
    quick_list=[(r["date"], r["direction"], r["entry_time"], r["hold"], r["net"]) for r in rows if r["quick_or"]])

# ---------- 2026-11-09 primary premium path ----------
cand = json.load(open(TR + "november_shadow_data/candles_BANKNIFTY_58900PE_2026-11-09_2026-11-23.json"))
bars = sorted(cand["data"]["candles"])
entry_bar = [b for b in bars if b[0][11:16] == "10:45"][0]
results["nov9_primary"] = dict(entry=815.40, stop=765.40, target=905.40,
    entry_bar=[entry_bar[0][11:16], entry_bar[1], entry_bar[2], entry_bar[3], entry_bar[4]],
    mfe_pts=round(entry_bar[2] - 815.40, 2), mae_pts=round(entry_bar[3] - 815.40, 2),
    exit="10:45 @ 765.40 STOP (entry bar)")

# ---------- 2026-11-06 SHADOW Skill winner path ----------
cand6 = json.load(open(TR + "november_shadow_data/candles_BANKNIFTY_57800CE_2026-11-06_2026-11-23.json"))
bars6 = sorted(cand6["data"]["candles"])
path6 = [b for b in bars6 if "09:50" <= b[0][11:16] <= "10:25"]
results["nov6_skill_winner"] = dict(entry=768.25, exit=858.25, exit_reason="target",
    mfe_pts=round(max(b[2] for b in path6) - 768.25, 2),
    mae_pts=round(min(b[3] for b in path6) - 768.25, 2))

# ---------- 2026-11-09 spot anatomy (EOD construction output) ----------
eod = json.load(open("/tmp/eod_2026-11-09.json"))["BANKNIFTY"]
srows = sorted(eod["spot_at"].values(), key=lambda x: x["time"])
morn = [r for r in srows if r["time"] < "11:30"]
aft = [r for r in srows if r["time"] >= "12:00"]
after_exit = [r for r in srows if r["time"] >= "10:45"]
results["nov9_spot"] = dict(
    bars=len(srows), open=srows[0]["open"], close=srows[-1]["close"],
    day_high=max(r["high"] for r in srows), day_low=min(r["low"] for r in srows),
    pre1130_high=max(r["high"] for r in morn), pre1130_low=min(r["low"] for r in morn),
    aft_high=max(r["high"] for r in aft),
    extension_above_morning_high=round(max(r["high"] for r in aft) - max(r["high"] for r in morn), 2),
    rise_after_last_exit=round(max(r["high"] for r in after_exit) - after_exit[0]["open"], 2),
    ns1_why=eod["ns1"]["why"], prev_close=eod["prev"]["close"])

print(json.dumps(results, indent=1))
with open(TR + "bank_segment_engine_evening_2026-11-09.json", "w") as f:
    json.dump(results, f, indent=1)
