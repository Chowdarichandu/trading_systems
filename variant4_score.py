#!/usr/bin/env python3
"""Variant 4 — hit-quality filters on NS1 second legs and NS2 afternoon legs.
Paper only, no orders, no stocks. Index OPTIONS, October 2026 premiums only.
FROZEN RULES (written before any filter outcome was computed):
  Population: the 15 October premium extra legs in
    index_options_newsetup_premium_october_trades.csv with
    (family=NS1, leg=second) or (family=NS2, leg=afternoon_rescan).
    Morning/base legs are NEVER filtered; unified-base legs are NEVER filtered.
  Base track V4B = unified base (34 unique-once trades, from
    index_options_october_UNIQUE_trades.md: Nifty 16 / +14169.75 / FT 6,
    Bank 18 / +11040.00 / FT 10) PLUS the 15 extra legs counted as
    additional legs (a second trade that day, even if it shares the
    date+index+direction key of a unified trade). V4B is therefore a
    legs track, not a unique-keys track; this is stated, not hidden.
  Filter (a) first-leg gate, two nested readings, both frozen:
    (a-NS) keep extra leg iff that day's first leg exited NOT as a stop
           (target or square_off). (a-T) keep iff first leg exited as a
           target only.
    First leg, NS-track reading (PRIMARY for NS1, and the literal NS2
    reading): NS1 second -> that day's NS1 base_S1 premium leg;
    NS2 afternoon -> NO morning leg exists by NS2 construction, so the
    gate FAILS for every NS2 afternoon leg under this reading.
    First leg, unified reading (SENSITIVITY, also frozen): earliest
    unified-base trade that date+index (by entry time); if no unified
    trade that date+index exists, the gate FAILS. Note 21 Oct has TWO
    unified trades per index (CE stop, then PE target); the unified
    reading uses the FIRST (earliest) one, not the preceding one.
  Filter (b) room >= 2x: keep iff spot room_ratio >= 2.0, where
    room = distance from the signal-bar close to the next PD level in
    direction (CE: smallest PD level > close, else infinity; PE:
    largest PD level < close, else infinity), PD = previous trading
    day's daily high/close/low, and spot risk = |entry_spot-stop_spot|
    from the NS Jan-Oct spot file. Base NS gate was >= 1.5; (b) tightens
    it to >= 2.0. Infinite room (no PD level in direction) keeps.
  Filter (c) premium extension, NO LOOKAHEAD: for the traded contract,
    from its cached 5-min option candles for that day, let
    low_to_entry / high_to_entry = min low / max high over candles
    with time <= entry candle (entry candle included). Position =
    (entry_premium - low_to_entry) / (high_to_entry - low_to_entry).
    Keep iff position <= 0.67, i.e. entry premium is NOT in the top
    third of the contract's premium range so far that day. Range 0
    keeps (no extension measurable). Full-day range is NOT used.
  Frequency: trades / 18 days * 5. FT = premium_full_target only;
  square-off greens never count as FT. Net per 1 lot, Nifty 65 / Bank 30,
  -50/+90 overlay, Rs 220 cost, exactly as in the premium file.
  No filter is combined with another; each is scored alone.
  Nothing is adopted on October alone.
"""
import csv, json, re
from pathlib import Path

T = Path.home() / "workspace/trading"
prem = list(csv.DictReader(open(T / "index_options_newsetup_premium_october_trades.csv")))
extra = [r for r in prem if (r["family"] == "NS1" and r["leg"] == "second")
         or (r["family"] == "NS2" and r["leg"] == "afternoon_rescan")]
assert len(extra) == 15, len(extra)

# --- NS-track first legs (premium exit reason) ---
base_s1 = {}
for r in prem:
    if r["family"] == "NS1" and r["leg"] == "base_S1":
        base_s1[(r["index"], r["date"])] = r["prem_exit_reason"]

# --- Unified base: parse UNIQUE markdown table ---
uni = []
for line in (T / "index_options_october_UNIQUE_trades.md").read_text().splitlines():
    m = re.match(r"\|\s*\d+\s*\| ([\d-]+) \| (NIFTY|BANKNIFTY) \| (CE|PE) \| (\d+) \| [\d-]+ \| ([\d:]+) \| ([\d.]+) \| ([\d:]+) \| ([\d.]+) \| (target|stop|square_off) \| ([+−-]?₹[\d,.]+) \|", line)
    # columns are: # | date | index | dir | strike | expiry | entry time | entry prem | exit time | exit prem | reason | net | ... ; expiry is the [\d-]+ after strike, entry time follows it, so the pattern above already accounts for it (strike, expiry, entry_time...)
    if m:
        date, idx, dr, strike, et, ep, xt, xp, reason, net = m.groups()
        uni.append(dict(date=date, index=idx, direction=dr, entry_time=et,
                        entry_prem=float(ep), exit_reason=reason,
                        net=float(net.replace("₹", "").replace("−", "-").replace(",", ""))))
assert len(uni) == 34, len(uni)
uni_first = {}
for u in sorted(uni, key=lambda x: x["entry_time"]):
    uni_first.setdefault((u["index"], u["date"]), u)
uni_tot = {}
for idx in ("NIFTY", "BANKNIFTY"):
    sub = [u for u in uni if u["index"] == idx]
    uni_tot[idx] = dict(n=len(sub), ft=sum(1 for u in sub if u["exit_reason"] == "target"),
                        net=round(sum(u["net"] for u in sub), 2))
print("unified check:", uni_tot)
assert uni_tot["NIFTY"] == dict(n=16, ft=6, net=14169.75)
assert uni_tot["BANKNIFTY"] == dict(n=18, ft=10, net=11040.0)

# --- Spot data for filter (b) ---
def load_spot(idx):
    bars = {}
    for row in csv.DictReader(open(T / f"data/progressive/{idx}/spot_5m.csv")):
        d, t = row["timestamp"].split(" ")
        bars[(d, t[:5])] = float(row["close"])
    daily = sorted(csv.DictReader(open(T / f"data/progressive/{idx}/spot_daily.csv")),
                   key=lambda r: r["date"])
    prev = {}
    for i, row in enumerate(daily):
        if i:
            prev[row["date"]] = (float(daily[i-1]["high"]), float(daily[i-1]["close"]),
                                 float(daily[i-1]["low"]))
    return bars, prev

spot = {idx: load_spot(idx) for idx in ("NIFTY", "BANKNIFTY")}
spot_legs = {}
for fam, fn in (("NS1", "index_options_newsetup_ns1_trades_jan_oct_2026.csv"),
                ("NS2", "index_options_newsetup_ns2_trades_jan_oct_2026.csv")):
    for r in csv.DictReader(open(T / fn)):
        if r["date"].startswith("2026-10"):
            spot_legs[(fam, r["index"], r["date"], r["leg"])] = r

# --- Option candles for filter (c) ---
def load_candles(r):
    idx, strike, typ, day, exp = r["index"], r["strike"], r["direction"], r["date"], r["expiry"]
    names = [f"candles_premium_{idx}_{strike}{typ}_{day}_{exp}.json"]
    if idx == "NIFTY":
        names.append(f"candles_Nifty_50_{strike}{typ}_{day}.json")
    else:
        names.append(f"candles_Nifty_Bank_{strike}{typ}_{day}.json")
    for nm in names:
        p = T / "v4_options_oct_data" / nm
        if p.exists():
            cs = json.loads(p.read_text())["data"]["candles"]
            cs = sorted(cs, key=lambda c: c[0])
            return nm, cs
    return None, None

rows = []
for r in extra:
    idx, date = r["index"], r["date"]
    key = (r["family"], idx, date, r["leg"])
    sl = spot_legs[key]
    risk = abs(float(sl["entry_spot"]) - float(sl["stop_spot"]))
    bars, prev = spot[idx]
    sig_close = bars[(date, r["signal_time"])]
    pdh, pdc, pdl = prev[date]
    if r["direction"] == "CE":
        above = [v for v in (pdh, pdc, pdl) if v > sig_close]
        room = (min(above) - sig_close) if above else float("inf")
    else:
        below = [v for v in (pdh, pdc, pdl) if v < sig_close]
        room = (sig_close - max(below)) if below else float("inf")
    ratio = float("inf") if room == float("inf") else room / risk
    # (a)
    ns_first = base_s1.get((idx, date)) if r["family"] == "NS1" else None
    u = uni_first.get((idx, date))
    uni_first_reason = u["exit_reason"] if u else None
    # (c) — CAREFUL: the premium file's entry_time column is the SPOT exit
    # bar time (a quirk of newsetups_score.replay, which sets entry_time to
    # the exit bar), NOT the premium entry candle time. The premium scorer
    # (newsetup_premium_score.score_premium) defines premium entry as the
    # first option candle with time > signal_time, so (c) uses exactly that.
    nm, cs = load_candles(r)
    entry_prem = float(r["entry_premium"])
    if cs is None:
        pos, lo, hi, prem_entry_time = None, None, None, None
    else:
        after = [c for c in cs if c[0][11:16] > r["signal_time"]]
        assert after, (r, nm)
        ec = after[0]; prem_entry_time = ec[0][11:16]
        assert abs(ec[1] - entry_prem) < 0.06, (r, nm, ec[1], entry_prem)
        upto = [c for c in cs if c[0][11:16] <= prem_entry_time]
        lo = min(c[3] for c in upto); hi = max(c[2] for c in upto)
        pos = None if hi == lo else (entry_prem - lo) / (hi - lo)
    rows.append(dict(family=r["family"], index=idx, date=date, leg=r["leg"],
                     direction=r["direction"], signal_time=r["signal_time"],
                     entry_time=r["entry_time"], prem_entry_time=prem_entry_time,
                     entry_premium=entry_prem,
                     exit_reason=r["prem_exit_reason"], ft=int(r["premium_full_target"]),
                     net=float(r["premium_net_per_1_lot_rs"]),
                     signal_close=sig_close, pdh=pdh, pdc=pdc, pdl=pdl,
                     spot_risk=round(risk, 2), room=(None if room == float("inf") else round(room, 2)),
                     room_ratio=(None if ratio == float("inf") else round(ratio, 3)),
                     ns_first=ns_first, uni_first=uni_first_reason,
                     candle_file=nm, ext_lo=lo, ext_hi=hi,
                     ext_pos=(None if pos is None else round(pos, 3)),
                     a_ns=("KEEP" if ns_first in ("target", "square_off") else "DROP"),
                     a_t=("KEEP" if ns_first == "target" else "DROP"),
                     a_uni_ns=("KEEP" if uni_first_reason in ("target", "square_off") else "DROP"),
                     a_uni_t=("KEEP" if uni_first_reason == "target" else "DROP"),
                     b=("KEEP" if ratio >= 2.0 else "DROP"),
                     c=("KEEP" if (pos is None or pos <= 0.67) else "DROP")))

with open(T / "index_options_toward_20k_variant4_legs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

def summ(sub):
    n = len(sub); ft = sum(x["ft"] for x in sub); net = round(sum(x["net"] for x in sub), 2)
    return dict(n=n, ft=ft, ft_pct=(round(100*ft/n, 1) if n else None),
                net=net, wk=round(n/18*5, 2))

print("\n=== EXTRA-LEG SUBSET (unfiltered base) ===")
for idx in ("NIFTY", "BANKNIFTY"):
    print(idx, summ([x for x in rows if x["index"] == idx]))
    for fam in ("NS1", "NS2"):
        print("  ", fam, summ([x for x in rows if x["index"] == idx and x["family"] == fam]))

filters = [("base (no filter)", None), ("a-NS (NS-track, not-stop)", "a_ns"),
           ("a-T (NS-track, target only)", "a_t"),
           ("a-NS (unified-first, not-stop)", "a_uni_ns"),
           ("a-T (unified-first, target only)", "a_uni_t"),
           ("b (room_ratio >= 2.0)", "b"), ("c (ext position <= 0.67)", "c")]
print("\n=== FILTERED EXTRA SUBSET + FULL TRACK (unified + filtered extra) ===")
for name, col in filters:
    for idx in ("NIFTY", "BANKNIFTY"):
        sub = [x for x in rows if x["index"] == idx and (col is None or x[col] == "KEEP")]
        s = summ(sub); u = uni_tot[idx]
        full = dict(n=u["n"]+s["n"], ft=u["ft"]+s["ft"],
                    ft_pct=round(100*(u["ft"]+s["ft"])/(u["n"]+s["n"]), 1),
                    net=round(u["net"]+s["net"], 2), wk=round((u["n"]+s["n"])/18*5, 2))
        print(f"{name} | {idx} | extra {s} | full {full}")
    print()
