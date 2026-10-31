#!/usr/bin/env python3
"""Score October NS legs on real option premiums (paper only, no orders).
Frozen premium rule: entry = open of first 5-min option candle with time > spot signal
time; stop = entry - 50, target = entry + 90 option points (CE and PE alike);
stop checked before target on every bar incl. entry bar; square-off 15:10 close;
net = (exit - entry) x lot - Rs 220; lot Nifty 65 / Bank 30; strike ATM nearest 100
to entry spot; expiry 2026-10-27 for 1-27 Oct, 2026-11-03 for 28 Oct.
Rows that cannot be fetched = NOT_COMPUTED (none expected after the fetch run)."""
import csv, json
from pathlib import Path

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
LOT = {"NIFTY": 65, "BANKNIFTY": 30}
LEGACY = {"NIFTY_22500PE_2026-10-23_2026-10-27": "candles_Nifty_50_22500PE_2026-10-23.json",
          "NIFTY_22600CE_2026-10-26_2026-10-27": "candles_Nifty_50_22600CE_2026-10-26.json",
          "BANKNIFTY_54300PE_2026-10-26_2026-10-27": "candles_Nifty_Bank_54300PE_2026-10-26.json",
          "BANKNIFTY_54400PE_2026-10-23_2026-10-27": "candles_Nifty_Bank_54400PE_2026-10-23.json",
          "BANKNIFTY_55200PE_2026-10-21_2026-10-27": "candles_Nifty_Bank_55200PE_2026-10-21.json",
          "NIFTY_22500PE_2026-10-28_2026-11-03": "candles_Nifty_50_22500PE_2026-10-28.json"}

def atm(p):
    return int(round(p / 100.0) * 100)

def candles_for(sym, strike, direction, date, expiry):
    tag = f"{sym}_{strike}{direction}_{date}_{expiry}"
    p = OUT / LEGACY.get(tag, f"candles_premium_{tag}.json")
    d = json.loads(p.read_text())
    cs = sorted(d["data"]["candles"], key=lambda c: c[0])
    return [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in cs]

def score_premium(sym, strike, direction, sig_time, date, expiry):
    cs = candles_for(sym, strike, direction, date, expiry)
    eb = [c for c in cs if c[0] > sig_time]
    if not eb:
        return None
    etime, entry = eb[0][0], eb[0][1]
    stop, target = entry - 50.0, entry + 90.0
    for (t, o, h, l, cl) in eb:
        if t > "15:10":
            break
        if l <= stop:
            return {"entry_premium": entry, "entry_time": etime, "exit_premium": stop,
                    "exit_time": t, "exit_reason": "stop"}
        if h >= target:
            return {"entry_premium": entry, "entry_time": etime, "exit_premium": target,
                    "exit_time": t, "exit_reason": "target"}
        if t == "15:10":
            return {"entry_premium": entry, "entry_time": etime, "exit_premium": cl,
                    "exit_time": t, "exit_reason": "square_off"}
    last = eb[-1]
    return {"entry_premium": entry, "entry_time": etime, "exit_premium": last[4],
            "exit_time": last[0], "exit_reason": "square_off"}

def main():
    rows, out = [], []
    for f in ["ns1", "ns2", "ns3", "ns4", "ns5a", "ns5b", "ns6"]:
        for r in csv.DictReader(open(Path.home() / f"workspace/trading/index_options_newsetup_{f}_trades_jan_oct_2026.csv")):
            if "2026-10-01" <= r["date"] <= "2026-10-28":
                r["family"] = f.upper()
                rows.append(r)
    for r in rows:
        exp = "2026-10-27" if r["date"] <= "2026-10-27" else "2026-11-03"
        strike = atm(float(r["entry_spot"]))
        lot = LOT[r["index"]]
        try:
            s = score_premium(r["index"], strike, r["direction"], r["signal_time"], r["date"], exp)
        except Exception as e:
            s = None
        if s is None:
            out.append({**r, "strike": strike, "expiry": exp, "entry_premium": "", "exit_premium": "",
                        "prem_exit_reason": "", "prem_exit_time": "", "premium_net_per_1_lot_rs": "NOT_COMPUTED",
                        "premium_status": "NOT_COMPUTED"})
        else:
            net = round((s["exit_premium"] - s["entry_premium"]) * lot - 220, 2)
            out.append({**r, "strike": strike, "expiry": exp, "entry_premium": s["entry_premium"],
                        "exit_premium": s["exit_premium"], "prem_exit_reason": s["exit_reason"],
                        "prem_exit_time": s["exit_time"], "premium_net_per_1_lot_rs": net,
                        "premium_status": "COMPUTED",
                        "premium_full_target": 1 if s["exit_reason"] == "target" else 0})
    fields = ["family", "index", "date", "leg", "direction", "signal_time", "entry_time", "entry_spot",
              "strike", "expiry", "entry_premium", "exit_premium", "prem_exit_reason", "prem_exit_time",
              "premium_net_per_1_lot_rs", "premium_status", "premium_full_target",
              "exit_reason", "spot_net_provisional_rs", "note"]
    with open(Path.home() / "workspace/trading/index_options_newsetup_premium_october_trades.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader(); w.writerows(out)
    print("legs:", len(out), "computed:", sum(1 for r in out if r["premium_status"] == "COMPUTED"))
    for fam in sorted({r["family"] for r in out}):
        for sym in ("NIFTY", "BANKNIFTY"):
            sub = [r for r in out if r["family"] == fam and r["index"] == sym]
            comp = [r for r in sub if r["premium_status"] == "COMPUTED"]
            if not sub:
                print(fam, sym, "n=0"); continue
            net = sum(float(r["premium_net_per_1_lot_rs"]) for r in comp)
            ft = sum(int(r["premium_full_target"]) for r in comp)
            print(fam, sym, f"n={len(sub)} computed={len(comp)} prem_net={net:,.2f} "
                  f"prem_FT={ft}/{len(comp)} prem/wk={len(comp)/18*5:.2f}")

if __name__ == "__main__":
    main()
