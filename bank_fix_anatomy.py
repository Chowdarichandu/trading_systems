#!/usr/bin/env python3
"""BANK-FIX STEP 1 — November anatomy (bank_fix_SPEC.md, frozen
2026-11-16 before scoring). Every November Bank leg Nov 2-16 across
stack / legacy lines, with the 5-min premium path after entry:
MFE / MAE and their bar times, check-bar (11:30 / 12:00) readings,
and per-dial mechanical effects. Diagnosis only — selects nothing.
Paper only, real money Rs0."""
import csv, json, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import bank_confgate_shadow_score as CG   # tod_of + score_factors verbatim

LOT, COST = 30, 220.0
SHADOW_DATA = TR / "november_shadow_data"

# ---------- gaps ----------
GAPS = {}
for r in csv.DictReader(open(TR / "november_regime_days_bank.csv")):
    if r["gap_pct"]:
        GAPS[r["date"]] = float(r["gap_pct"])
# Nov 16 is past the frozen regime file: derive from the persisted
# progressive spot file (09:15 open vs prior in-store weekday close),
# the B-FIX-1 scorer's own fallback. Marked as derived.
GAP_SRC = {d: "regime_file" for d in GAPS}
try:
    days = {}
    for r in csv.DictReader(open(TR / "data/progressive/BANKNIFTY/spot_5m.csv")):
        days.setdefault(r["timestamp"][:10], []).append(r)
    if "2026-11-16" in days and "2026-11-16" not in GAPS:
        prev = sorted(d for d in days if d < "2026-11-16")[-1]
        GAPS["2026-11-16"] = (float(days["2026-11-16"][0]["open"])
                              / float(days[prev][-1]["close"]) - 1.0) * 100.0
        GAP_SRC["2026-11-16"] = "progressive_spot_derived"
except Exception as e:
    print("Nov 16 gap derivation failed:", e)

def band(p):
    return "<500" if p < 500 else ("500-800" if p <= 800 else ">800")

def load_day_candles(strike, side, day):
    f = SHADOW_DATA / f"candles_BANKNIFTY_{strike}{side}_{day}_2026-11-23.json"
    if not f.exists():
        return None
    raw = json.load(open(f))["data"]["candles"]
    bars = []
    for c in raw:
        if c[0][:10] != day:
            continue
        bars.append((c[0][11:16], float(c[1]), float(c[2]),
                     float(c[3]), float(c[4])))
    bars.sort()
    return bars

def check_bar(bars, check):
    for b in bars:
        if b[0] >= check:
            return b
    return None

def anatomy_leg(line, date, fam, side, strike, expiry, et, ep, xt, xp,
                reason, net):
    bars = load_day_candles(strike, side, date)
    row = dict(line=line, date=date, family=fam, side=side,
               strike=strike, expiry=expiry, entry_time=et,
               entry_premium=ep, premium_band=band(ep),
               gap_pct=(round(GAPS[date], 4) if date in GAPS else ""),
               gap_source=GAP_SRC.get(date, ""),
               exit_time=xt, exit_premium=xp, exit_reason=reason,
               net_inr=net)
    if bars is None:
        row["candles"] = "MISSING"
        return row
    row["candles"] = "ok"
    held = [b for b in bars if et <= b[0] <= xt]
    assert held, (date, et, xt)
    mfe_b = max(held, key=lambda b: b[2])
    mae_b = min(held, key=lambda b: b[3])
    row["mfe_pts"] = round(mfe_b[2] - ep, 2)
    row["mfe_time"] = mfe_b[0]
    row["mae_pts"] = round(ep - mae_b[3], 2)
    row["mae_time"] = mae_b[0]
    row["ever_in_profit"] = "YES" if row["mfe_pts"] > 0 else "NO"
    for chk, tag in (("11:30", "1130"), ("12:00", "1200")):
        b = check_bar(bars, chk)
        if b is None:
            row[f"chk{tag}_close"] = ""
            row[f"d3{tag}_fires"] = ""
            row[f"d3{tag}_net"] = ""
            continue
        open_at = xt > b[0]
        below = b[4] < ep
        fires = (et <= chk) and open_at and below
        row[f"chk{tag}_time"] = b[0]
        row[f"chk{tag}_close"] = b[4]
        row[f"open_at_{tag}"] = "YES" if open_at else "NO"
        row[f"below_entry_at_{tag}"] = "YES" if below else "NO"
        row[f"d3{tag}_fires"] = "YES" if fires else "NO"
        row[f"d3{tag}_net"] = (round((b[4] - ep) * LOT - COST, 2)
                               if fires else net)
    # dial flags
    g = GAPS.get(date)
    row["bfix1_cell"] = ("YES" if (side == "PE" and g is not None
                                   and g < 0 and 500 <= ep <= 800)
                         else "NO")
    if g is not None:
        f = CG.score_factors(side, ep, CG.tod_of(et), g)
        row["conf_score_nov_basis"] = f[6]
        row["confgate_kept_nov"] = "YES" if f[6] >= 0.5 else "NO"
    else:
        row["conf_score_nov_basis"] = ""
        row["confgate_kept_nov"] = ""
    row["d1_kept"] = ("YES" if (row["bfix1_cell"] == "NO"
                                and row["confgate_kept_nov"] == "YES")
                      else "NO")
    row["d2a_dropped"] = "YES" if et >= "11:30" else "NO"
    row["d2b_dropped"] = "YES" if et >= "12:00" else "NO"
    row["is_ns1"] = "YES" if fam in ("NS1_second", "NS1") else "NO"
    return row

rows = []
# ---- stack line ----
for r in csv.DictReader(open(TR / "november_shadow_stack_bank_log.csv")):
    if not r.get("entry_premium"):
        continue
    rows.append(anatomy_leg(
        "STACK", r["date"], r["family"], r["direction"],
        int(r["strike"]), r["expiry"], r["entry_time"],
        float(r["entry_premium"]), r["exit_time"],
        float(r["exit_premium"]), r["exit_reason"], float(r["net_inr"])))
# ---- legacy line (PRIMARY channel of the frozen V1 log) ----
for r in csv.DictReader(open(TR / "november_paper_bank_log.csv")):
    if r["channel"] != "PRIMARY" or not r.get("entry_premium"):
        continue
    rows.append(anatomy_leg(
        "LEGACY", r["date"], r["system_source"], r["direction"],
        int(r["strike"]), r["expiry"], r["entry_time"],
        float(r["entry_premium"]), r["exit_time"],
        float(r["exit_premium"]), r["exit_reason"], float(r["net_inr"])))

FIELDS = ["line", "date", "family", "side", "strike", "expiry",
          "entry_time", "entry_premium", "premium_band", "gap_pct",
          "gap_source", "exit_time", "exit_premium", "exit_reason",
          "net_inr", "candles", "mfe_pts", "mfe_time", "mae_pts",
          "mae_time", "ever_in_profit", "chk1130_time", "chk1130_close",
          "open_at_1130", "below_entry_at_1130", "d31130_fires",
          "d31130_net", "chk1200_time", "chk1200_close", "open_at_1200",
          "below_entry_at_1200", "d31200_fires", "d31200_net",
          "bfix1_cell", "conf_score_nov_basis", "confgate_kept_nov",
          "d1_kept", "d2a_dropped", "d2b_dropped", "is_ns1"]
with open(TR / "bank_fix_anatomy_november.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)

for line in ("STACK", "LEGACY"):
    sub = [r for r in rows if r["line"] == line]
    tot = round(sum(r["net_inr"] for r in sub), 2)
    print(f"{line}: {len(sub)} legs, total {tot:+,.2f}")
    for r in sub:
        print(f"  {r['date']} {r['family']:>10} {r['side']} {r['strike']} "
              f"entry {r['entry_time']} @{r['entry_premium']:.2f} "
              f"[{r['premium_band']}] gap {r['gap_pct']} -> exit "
              f"{r['exit_time']} {r['exit_reason']} net {r['net_inr']:+,.2f} "
              f"| MFE {r.get('mfe_pts')} @ {r.get('mfe_time')} "
              f"MAE {r.get('mae_pts')} @ {r.get('mae_time')} "
              f"ever_profit {r.get('ever_in_profit')}")

losers = [r for r in rows if r["net_inr"] < 0]
win = [r for r in rows if r["net_inr"] > 0]
print(f"\nLOSERS: {len(losers)} across both lines; "
      f"ever in profit: {sum(1 for r in losers if r.get('ever_in_profit')=='YES')}")
for r in losers:
    print(f"  {r['line']} {r['date']} {r['side']} @{r['entry_premium']:.2f} "
          f"MFE {r.get('mfe_pts')} pts @ {r.get('mfe_time')} "
          f"(turn), net {r['net_inr']:+,.2f}")
print(f"WINNERS: {len(win)}")
for r in win:
    print(f"  {r['line']} {r['date']} {r['family']} {r['side']} "
          f"entry {r['entry_time']} net {r['net_inr']:+,.2f} | "
          f"D1 kept {r['d1_kept']} · D2a drop {r['d2a_dropped']} · "
          f"D2b drop {r['d2b_dropped']} · D3a fires {r.get('d31130_fires')} "
          f"· D3b fires {r.get('d31200_fires')} · NS1 {r['is_ns1']}")

stk = [r for r in rows if r["line"] == "STACK"]
def cf(name, keep_fn):
    kept = [r for r in stk if keep_fn(r)]
    print(f"STACK Nov CF {name}: kept {len(kept)}/{len(stk)} legs, "
          f"net {round(sum(r['net_inr'] for r in kept),2):+,.2f} "
          f"(actual {round(sum(r['net_inr'] for r in stk),2):+,.2f})")
cf("B-FIX-1", lambda r: r["bfix1_cell"] == "NO")
cf("CONF>=0.5 (Nov basis)", lambda r: r["confgate_kept_nov"] == "YES")
cf("D1 combined", lambda r: r["d1_kept"] == "YES")
cf("D2a (>=11:30 cut)", lambda r: r["d2a_dropped"] == "NO")
cf("D2b (>=12:00 cut)", lambda r: r["d2b_dropped"] == "NO")
for tag in ("1130", "1200"):
    tot = round(sum(float(r[f"d3{tag}_net"]) for r in stk), 2)
    print(f"STACK Nov CF D3@{tag}: net {tot:+,.2f} "
          f"(actual {round(sum(r['net_inr'] for r in stk),2):+,.2f})")
cf("D4a (no NS1_second)", lambda r: r["is_ns1"] == "NO")
print("WROTE bank_fix_anatomy_november.csv")
