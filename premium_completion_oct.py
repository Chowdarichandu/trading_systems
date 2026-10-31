#!/usr/bin/env python3
"""Premium completion, October 2026 — signal reconstruction (paper only, no orders).
Reconstructs spot signals for every TAKEN trade in index_options_v2_october_trades.csv
from the progressive spot cache, verifies spot nets match the v2 CSV to the rupee,
and emits the contract/fetch list for the browser-fetch premium scorer.
Rules (frozen, from familyC frozen + familyB):
- Skill S1: first close beyond 09:15-09:30 OR, 09:30-11:30; 09:30 PE only if close<PDL;
  CE blocked on bearish-bias days. Entry = next 5-min open.
- V4/V5: find_signal from daytrader_cash_backtest (setups 1-4, Setup 1 skipped for
  lack of Red bands in that function; V5 in October = V4 set, Family C verified).
- (lA) v2: signal times taken verbatim from v2 CSV notes; entry = next 5-min open.
Expiry convention (stated, carried from v4_options report): monthly 2026-10-27 for
all trades dated 1-27 Oct, weekly 2026-11-03 for 28 Oct trades. Strike = ATM nearest
100 to entry spot.
Premium exit rule (frozen translation, applied uniformly so versions are comparable
on premiums, and labelled as such): stop = entry premium -50 (CE) / +50? No — for
options, stop = entry -50 for CE and entry -50 for PE as well (premium falls when
the trade goes wrong in either direction); target = entry +90. Bar-by-bar on the
option's own 5-min candles, stop checked before target, square-off 15:10 close,
cost Rs 220/trade assumed, lot Nifty 65 / Bank 30.
NOTE on native rules: Skill/(lA) native spot exits are stop=signal high/low and
target=2x spot risk, and (lA) native target is 2x spot risk — those are the SPOT
nets in the v2 CSV. The premium -50/+90 rule is NOT their native rule; it is the
options overlay defined in the v2 frozen spec for V5-v2 and in the v4 options
report, extended here to Skill/(lA) so their premiums can be scored at all
(premium does not move 1:1 with spot, so spot risk cannot be pasted onto premium).
Both the spot net and the premium net are reported side by side; neither is
presented as the other's equivalent.
"""
import sys, os, math, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from daytrader_cash_backtest import find_signal, run_day, bias_of

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
LA = {("NIFTY","2026-10-08"):("11:25","PE"),("NIFTY","2026-10-21"):("11:35","PE"),
      ("NIFTY","2026-10-23"):("10:05","PE"),("BANKNIFTY","2026-10-07"):("09:35","PE"),
      ("BANKNIFTY","2026-10-08"):("13:15","PE"),("BANKNIFTY","2026-10-21"):("11:15","PE"),
      ("BANKNIFTY","2026-10-23"):("09:55","PE")}

def load(sym):
    spot = pd.read_csv(os.path.join(BASE, sym, "spot_5m.csv"), parse_dates=["timestamp"])
    daily = pd.read_csv(os.path.join(BASE, sym, "spot_daily.csv"), parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot.sort_values("timestamp"), daily.sort_values("date")

def skill_signal(day):
    or_c = day[day["time"] < "09:30"]
    orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
    for _, row in day[(day["time"] >= "09:30") & (day["time"] <= "11:30")].iterrows():
        if float(row["close"]) > orh: return "or_breakout","CE",row,orh,orl
        if float(row["close"]) < orl: return "or_breakdown","PE",row,orh,orl
    return None,None,None,orh,orl

def next_open(day, sig_time):
    cand = day[day["time"] >= "09:30"].reset_index(drop=True)
    idx = cand.index[cand["time"] == sig_time]
    if len(idx)==0 or int(idx[0])+1 >= len(cand): return None,None
    return float(cand.iloc[int(idx[0])+1]["open"]), cand.iloc[int(idx[0])+1]["time"]

def atm(price): return int(round(price/100.0)*100)

def main():
    v2 = {}
    with open(os.path.expanduser("~/workspace/trading/index_options_v2_october_trades.csv")) as f:
        for r in csv.DictReader(f):
            if r["exit_reason"] in ("BLOCKED",) or r["spot_points_provisional_net_rs"] in ("NOT_COMPUTED",):
                continue
            if r["version"] in ("Volrix v2 (overlay)",): continue
            v2[(r["version"], r["index"], r["date"])] = r
    out, mismatches = [], []
    for sym in ("NIFTY","BANKNIFTY"):
        spot, daily = load(sym); dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if not (pd.Timestamp("2026-10-01") <= d <= pd.Timestamp("2026-10-28")) or i==0: continue
            ds = d.date().isoformat(); day = spot[spot["date"]==d]
            if day.empty: continue
            prev = dl[i-1]; pdh,pdc,pdl = float(prev["high"]),float(prev["close"]),float(prev["low"])
            bias,_ = bias_of(prev); scale = pdc/55000.0
            # Skill S1
            setup, direction, sig, orh, orl = skill_signal(day)
            if sig is not None:
                blocked = (direction=="PE" and sig["time"]=="09:30" and not (float(sig["close"])<pdl)) or \
                          (direction=="CE" and bias=="bearish")
                if not blocked:
                    entry, etime = next_open(day, sig["time"])
                    # spot net via familyB logic
                    cand = day[day["time"]>="09:30"].reset_index(drop=True)
                    si = int(cand.index[cand["time"]==sig["time"]][0])
                    stop = float(sig["low"]) if direction=="CE" else float(sig["high"])
                    risk = abs(entry-stop); target = entry+2*risk if direction=="CE" else entry-2*risk
                    net, reason = None, None
                    for j in range(si+1, len(cand)):
                        row = cand.iloc[j]
                        if direction=="CE":
                            if float(row["low"])<=stop: net,reason = -risk*100-40,"stop"; break
                            if float(row["high"])>=target: net,reason = 2*risk*100-40,"target"; break
                        else:
                            if float(row["high"])>=stop: net,reason = -risk*100-40,"stop"; break
                            if float(row["low"])<=target: net,reason = 2*risk*100-40,"target"; break
                        if row["time"]=="15:10":
                            net = (1 if direction=="CE" else -1)*(float(row["close"])-entry)*100-40; reason="square_off"; break
                    key = ("Skill v2 (S1)", sym, ds)
                    if key in v2:
                        exp_net = float(v2[key]["spot_points_provisional_net_rs"])
                        if abs(net-exp_net) > 0.01: mismatches.append((key, net, exp_net))
                        out.append({"version":"Skill v2 (S1)","index":sym,"date":ds,"setup":setup,"direction":direction,
                                    "signal_time":sig["time"],"entry_time":etime,"entry_spot":entry,
                                    "strike":atm(entry),"expiry":"2026-10-27" if ds<"2026-10-28" else "2026-11-03",
                                    "spot_net":net,"spot_exit":reason,"v2_spot_net":exp_net})
            # V4 (also V5 in October)
            r = run_day(day, pdh, pdc, pdl, bias, scale, 100, 40.0)
            if r["exit_reason"] in ("target","stop","square_off"):
                setup, direction, sig = find_signal(day, pdh, pdc, pdl, bias, scale)
                sig_time = str(sig["timestamp"])[11:16]
                for ver in ("V5-v2",):
                    key = (ver, sym, ds)
                    if key in v2:
                        exp_net = float(v2[key]["spot_points_provisional_net_rs"])
                        if abs(float(r["net_rs"])-exp_net) > 0.01: mismatches.append((key, float(r["net_rs"]), exp_net))
                        out.append({"version":ver,"index":sym,"date":ds,"setup":setup,"direction":direction,
                                    "signal_time":sig_time,"entry_time":str(r["entry_time"])[11:16] if r.get("entry_time") else "",
                                    "entry_spot":float(r["entry_price"]),"strike":atm(float(r["entry_price"])),
                                    "expiry":"2026-10-27" if ds<"2026-10-28" else "2026-11-03",
                                    "spot_net":round(float(r["net_rs"]),2),"spot_exit":r["exit_reason"],"v2_spot_net":exp_net})
            # (lA)
            if (sym, ds) in LA:
                st, direction = LA[(sym,ds)]
                entry, etime = next_open(day, st)
                key = ("(lA) v2 (L1)", sym, ds)
                if key in v2:
                    out.append({"version":"(lA) v2 (L1)","index":sym,"date":ds,"setup":"la_pe_rescan_reentry_L1","direction":direction,
                                "signal_time":st,"entry_time":etime,"entry_spot":entry,"strike":atm(entry),
                                "expiry":"2026-10-27" if ds<"2026-10-28" else "2026-11-03",
                                "spot_net":float(v2[key]["spot_points_provisional_net_rs"]),"spot_exit":v2[key]["exit_reason"],
                                "v2_spot_net":float(v2[key]["spot_points_provisional_net_rs"])})
    out.sort(key=lambda x:(x["version"],x["index"],x["date"]))
    with open(os.path.expanduser("~/workspace/trading/index_options_premium_recon_oct.csv"),"w",newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
    print(f"reconstructed {len(out)} trades; v2 taken trades {len(v2)}; mismatches {len(mismatches)}")
    for m in mismatches: print("MISMATCH", m)
    for o in out: print(o["version"], o["index"], o["date"], o["setup"], o["direction"], "sig", o["signal_time"], "entry", o["entry_time"], o["entry_spot"], "strike", o["strike"], o["expiry"], "spot", o["spot_net"], o["spot_exit"])
    # fetch list: unique (index, expiry, strike, direction, date)
    uniq = sorted({(o["index"],o["expiry"],o["strike"],o["direction"],o["date"]) for o in out})
    print(f"unique contract-days to fetch: {len(uniq)}")
    for u in uniq: print("FETCH", u)

if __name__ == "__main__": main()
