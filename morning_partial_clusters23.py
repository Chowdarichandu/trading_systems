"""Apply (o) morning-partial variants to Cluster 2 (CE reclaim) and Cluster 3
(PE slow give-back) ORIGINAL trades from nifty_failing_cases_jan_oct_2026.md.
Direct bar-by-bar replay from the reported entry/stop/target, NOT a signal
rescan (Cluster 2 is setup4 reclaim, not a setup2 breakdown scan).
PE: adverse = high >= stop, favourable = low <= partial/target.
CE: adverse = low <= stop, favourable = high >= partial/target.
Bar order: adverse before favourable, partial before target, square-off 15:10.
100 shares split 50/50, Rs40 once. Green = net > 0.
"""
import pandas as pd, json, os
BASE = os.path.expanduser("~/workspace/trading/data/progressive/NIFTY")
spot = pd.read_csv(os.path.join(BASE, "spot_5m.csv"), parse_dates=["timestamp"])
spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
spot["date"] = spot["timestamp"].dt.normalize()
spot["time"] = spot["timestamp"].dt.strftime("%H:%M")

TRADES = [
    # cluster, date, dir, signal, entry, stop, target, orig_net
    ("2", "2026-01-14", "CE", "11:15", 25747.75, 25720.30, 25802.65, -2785),
    ("2", "2026-10-26", "CE", "09:55", 22635.70, 22549.75, 22807.60, -8635),
    ("3", "2026-02-13", "PE", "09:30", 25549.00, 25586.10, 25474.80, -3750),
    ("3", "2026-04-30", "PE", "10:00", 23848.75, 23880.00, 23786.25, -3165),
    ("3", "2026-05-18", "PE", "09:35", 23358.50, 23394.80, 23285.90, -3670),
]


def replay(date, direction, signal, entry, stop, target, trigger_frac, trail_be):
    d = pd.Timestamp(date)
    day = spot[spot["date"] == d].sort_values("timestamp").reset_index(drop=True)
    cand = day[day["time"] >= "09:30"].reset_index(drop=True)
    sig_idx = cand.index[cand["time"] == signal].tolist()
    assert sig_idx, f"signal {signal} not found {date}"
    sig_idx = sig_idx[0]
    # verify entry = next bar open
    nxt_open = float(cand.iloc[sig_idx + 1]["open"])
    assert abs(nxt_open - entry) < 0.01, f"{date} entry mismatch {nxt_open} vs {entry}"
    risk = abs(stop - entry)
    if direction == "PE":
        plevel = entry - trigger_frac * risk
    else:
        plevel = entry + trigger_frac * risk
    partial_booked = False; partial_net = 0.0; partial_time = None; cur_stop = stop; trailed = False
    for j in range(sig_idx + 1, len(cand)):
        c = cand.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        adverse = (hi >= cur_stop) if direction == "PE" else (lo <= cur_stop)
        if adverse:
            if partial_booked:
                rem = -(cur_stop - entry) * 50 if direction == "PE" else (cur_stop - entry) * 50
                kind = "breakeven_stop_after_partial" if trailed else "stop_after_partial"
                return {"exit": kind, "exit_time": t, "net": round(partial_net + rem - 40, 2),
                        "partial_time": partial_time, "partial_level": round(plevel, 2)}
            return {"exit": "stop", "exit_time": t, "net": round(-risk * 100 - 40, 2),
                    "partial_time": None, "partial_level": round(plevel, 2)}
        fav_partial = (lo <= plevel) if direction == "PE" else (hi >= plevel)
        if not partial_booked and fav_partial:
            partial_booked = True; partial_time = t
            partial_net = (entry - plevel) * 50 if direction == "PE" else (plevel - entry) * 50
            if trail_be:
                cur_stop = entry; trailed = True
            fav_target = (lo <= target) if direction == "PE" else (hi >= target)
            if fav_target:
                rem = (entry - target) * 50 if direction == "PE" else (target - entry) * 50
                return {"exit": "target_same_bar_as_partial", "exit_time": t,
                        "net": round(partial_net + rem - 40, 2), "partial_time": partial_time,
                        "partial_level": round(plevel, 2)}
        fav_target = (lo <= target) if direction == "PE" else (hi >= target)
        if fav_target:
            if partial_booked:
                rem = (entry - target) * 50 if direction == "PE" else (target - entry) * 50
                return {"exit": "target_after_partial", "exit_time": t,
                        "net": round(partial_net + rem - 40, 2), "partial_time": partial_time,
                        "partial_level": round(plevel, 2)}
            return {"exit": "target", "exit_time": t, "net": round(2 * risk * 100 - 40, 2),
                    "partial_time": None, "partial_level": round(plevel, 2)}
        if t == "15:10":
            if partial_booked:
                rem = (entry - cl) * 50 if direction == "PE" else (cl - entry) * 50
                return {"exit": "square_off_after_partial", "exit_time": t,
                        "net": round(partial_net + rem - 40, 2), "partial_time": partial_time,
                        "partial_level": round(plevel, 2)}
            net = (entry - cl) * 100 - 40 if direction == "PE" else (cl - entry) * 100 - 40
            return {"exit": "square_off", "exit_time": t, "net": round(net, 2),
                    "partial_time": None, "partial_level": round(plevel, 2)}
    c = cand.iloc[-1]
    return {"exit": "end_of_data", "exit_time": c["time"], "net": None, "partial_time": partial_time,
            "partial_level": round(plevel, 2)}


if __name__ == "__main__":
    variants = [("o1", 1.0, True), ("o2", 1.0, False), ("o3", 0.5, True)]
    out = {}
    for name, frac, trail in variants:
        print(f"\n=== ({name}) Clusters 2+3 ===")
        rows = []
        for cl, ds, dirc, sig, entry, stop, target, orig in TRADES:
            r = replay(ds, dirc, sig, entry, stop, target, frac, trail)
            rows.append({"cluster": cl, "date": ds, "dir": dirc, "orig_net": orig, **r})
            print(ds, f"Cluster {cl} {dirc}", "orig", orig, "->", r)
        for cl in ("2", "3"):
            sub = [x for x in rows if x["cluster"] == cl]
            g = sum(1 for x in sub if x["net"] is not None and x["net"] > 0)
            tot = sum(x["net"] for x in sub if x["net"] is not None)
            print(f"Cluster {cl}: green {g}/{len(sub)} total {tot}")
        g = sum(1 for x in rows if x["net"] is not None and x["net"] > 0)
        tot = sum(x["net"] for x in rows if x["net"] is not None)
        print(f"Clusters 2+3 combined: green {g}/5 total {tot} (orig total -22005)")
        out[name] = rows
    with open(os.path.expanduser("~/workspace/trading/morning_partial_clusters23_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
