"""O1 cross-confirmation persistence, Jan-Oct 2026. Paper only, no orders.
Frozen definition: ~/workspace/trading/index_options_o1_janoct_frozen.md
Bases: V4 uncapped (recomputed), Skill S1 uncapped (recomputed, Family B functions),
(lA) L1 uncapped candidates (merged JSONs), V5-v2 capped pool (capped_v2 JSONs,
origin signal times recomputed). O1: PE only; confirmer (other index) close below
its own OR low on BOTH signal bar and entry bar (same clock times); CE kept.
Unit: points x 100 shares - Rs 40. NOT options-lot, NOT futures.
"""
import sys, os, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped import load, room_ratio
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal
from progressive_capped import skill_or_outcome

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
QTY, COST = 100, 40.0
SYMS = ("NIFTY", "BANKNIFTY")
OTHER = {"NIFTY": "BANKNIFTY", "BANKNIFTY": "NIFTY"}

def prev_daily(daily, d):
    prev = daily[daily["date"] < d]
    return prev.iloc[-1] if len(prev) else None

def bias_cs(y):
    rng = float(y["high"]) - float(y["low"])
    cs = (float(y["close"]) - float(y["low"])) / rng * 100 if rng else 50.0
    return ("bearish" if cs < 35 else "bullish" if cs >= 80 else "neutral"), cs

def skill_signal(day, or_cut="09:30", sig_from="09:30", sig_to="11:30"):
    or_c = day[day["time"] < or_cut]
    if or_c.empty: return None
    orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
    cand = day[(day["time"] >= sig_from) & (day["time"] <= sig_to)]
    for _, row in cand.iterrows():
        if float(row["close"]) > orh: return "or_breakout", "CE", row, orh, orl
        if float(row["close"]) < orl: return "or_breakdown", "PE", row, orh, orl
    return None

def skill_outcome(day, sig_row, direction):
    cand = day[day["time"] >= "09:30"].reset_index(drop=True)
    idx = cand.index[cand["timestamp"] == sig_row["timestamp"]]
    if len(idx) == 0: return None
    si = int(idx[0])
    if si + 1 >= len(cand): return None
    entry = float(cand.iloc[si + 1]["open"])
    if direction == "CE":
        stop = entry - (entry - float(sig_row["low"])); target = entry + 2 * (entry - stop)
    else:
        stop = entry + (float(sig_row["high"]) - entry); target = entry - 2 * (stop - entry)
    if entry == stop: return None
    d = 1 if direction == "CE" else -1
    for j in range(si + 1, len(cand)):
        row = cand.iloc[j]
        if direction == "CE":
            if float(row["low"]) <= stop: return {"exit_reason": "stop", "net_rs": round(-(entry - stop) * QTY - COST, 2)}
            if float(row["high"]) >= target: return {"exit_reason": "target", "net_rs": round(2 * (entry - stop) * QTY - COST, 2)}
        else:
            if float(row["high"]) >= stop: return {"exit_reason": "stop", "net_rs": round(-(stop - entry) * QTY - COST, 2)}
            if float(row["low"]) <= target: return {"exit_reason": "target", "net_rs": round(2 * (stop - entry) * QTY - COST, 2)}
        if row["time"] == "15:10":
            return {"exit_reason": "square_off", "net_rs": round(d * (float(row["close"]) - entry) * QTY - COST, 2)}
    row = cand.iloc[-1]
    return {"exit_reason": "square_off", "net_rs": round(d * (float(row["close"]) - entry) * QTY - COST, 2)}

def main():
    data = {}
    for sym in SYMS:
        spot, daily = load(sym)
        data[sym] = (spot, daily)
    # per-symbol day structures for O1 checks: day -> {time: close}, or_low, ordered times
    daymap = {}
    for sym in SYMS:
        spot, daily = data[sym]
        m = {}
        for d, grp in spot.groupby("date"):
            grp = grp.sort_values("timestamp")
            times = list(grp["time"])
            m[d] = {"close": {t: float(c) for t, c in zip(grp["time"], grp["close"])},
                    "times": times,
                    "or_low": float(grp[grp["time"] < "09:30"]["low"].min()) if (grp["time"] < "09:30").any() else None}
        daymap[sym] = m
    trading_days = sorted(set(data["NIFTY"][1]["date"]))
    trading_days = [d for d in trading_days if pd.Timestamp("2026-01-01") <= d <= pd.Timestamp("2026-10-28")]
    print(f"trading days in Nifty daily cache Jan-Oct (incl possible prior-day first row handling below): {len(trading_days)}")

    def o1_check(sym, date_str, sig_time):
        """Returns (kept_bool, reason, confirmer_or_low, close_sig, close_entry, entry_time)."""
        conf = OTHER[sym]
        d = pd.Timestamp(date_str)
        traded = daymap[sym].get(d)
        cmap = daymap[conf].get(d)
        if traded is None or cmap is None:
            return False, "missing_day_cache", None, None, None, None
        times = traded["times"]
        if sig_time not in times:
            return False, "signal_bar_missing", cmap["or_low"], None, None, None
        si = times.index(sig_time)
        if si + 1 >= len(times):
            return False, "no_entry_bar", cmap["or_low"], cmap["close"].get(sig_time), None, None
        entry_time = times[si + 1]
        cs = cmap["close"].get(sig_time); ce = cmap["close"].get(entry_time)
        if cs is None or ce is None:
            return False, "confirmer_bar_missing", cmap["or_low"], cs, ce, entry_time
        if cs < cmap["or_low"] and ce < cmap["or_low"]:
            return True, "confirmer_below_ORlow_both_bars", cmap["or_low"], cs, ce, entry_time
        return False, "confirmer_NOT_below_ORlow_both_bars", cmap["or_low"], cs, ce, entry_time

    rows = []  # all base trades, one row per track-trade
    def add(track, sym, date, setup, direction, sig_time, exit_reason, net):
        rows.append({"track": track, "index": sym, "date": date, "setup": setup,
                     "direction": direction, "signal_time": sig_time,
                     "exit_reason": exit_reason, "net_rs": round(float(net), 2),
                     "full_target": bool(exit_reason == "target" and float(net) > 0),
                     "win": bool(float(net) > 0)})

    # ---- V4 uncapped + Skill-filtered origins (for V5) ----
    v4_sig = {}   # (sym,date) -> signal_time
    filt_sig = {} # (sym,date) -> signal_time
    for sym in SYMS:
        spot, daily = data[sym]
        dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != 2026 or d.month > 10 or i == 0:
                continue
            if d > pd.Timestamp("2026-10-28"):
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty: continue
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            ds = d.date().isoformat()
            r = run_day(day_spot, pdh, pdc, pdl, bias, scale, QTY, COST)
            if r["exit_reason"] in ("target", "stop", "square_off"):
                setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
                sig_time = str(sig["time"]) if sig is not None else ""
                v4_sig[(sym, ds)] = sig_time
                add("V4", sym, ds, setup, direction, sig_time, r["exit_reason"], r["net_rs"])
            # Skill filtered (v2 pool definition)
            raw = day_spot.to_dict("records")
            for c in raw: c["timestamp"] = str(c["timestamp"])
            setup, direction, sig = find_skill_signal(raw, ("or",))
            if setup is None: continue
            allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
            if direction not in allowed: continue
            sig_close = float(sig["close"])
            if direction == "CE" and not (sig_close < pdh): continue
            if direction == "PE" and not (sig_close < pdl): continue
            rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
            if rr < 1.0: continue
            out = skill_or_outcome(raw, sig, direction)
            if out is None: continue
            filt_sig[(sym, ds)] = str(sig["time"])
    print(f"V4 uncapped: Nifty {sum(1 for r in rows if r['track']=='V4' and r['index']=='NIFTY')}, "
          f"Bank {sum(1 for r in rows if r['track']=='V4' and r['index']=='BANKNIFTY')}")

    # ---- Skill S1 uncapped ----
    for sym in SYMS:
        spot, daily = data[sym]
        for d in sorted(daily["date"]):
            if d.year != 2026 or d.month > 10 or d > pd.Timestamp("2026-10-28"): continue
            day = spot[spot["date"] == d]
            if day.empty: continue
            y = prev_daily(daily, d)
            if y is None: continue
            pdh, pdc, pdl = float(y["high"]), float(y["close"]), float(y["low"])
            bias, cs = bias_cs(y)
            sig = skill_signal(day)
            if sig is None: continue
            setup, direction, srow, orh, orl = sig
            blocked = None
            if direction == "CE" and bias == "bearish": blocked = "S1_CE_bearish"
            if direction == "PE" and srow["time"] == "09:30" and not (float(srow["close"]) < pdl): blocked = "S1_0930_PE"
            if blocked: continue
            oc = skill_outcome(day, srow, direction)
            if oc is None: continue
            add("Skill v2", sym, d.date().isoformat(), setup, direction, str(srow["time"]), oc["exit_reason"], oc["net_rs"])
    print(f"Skill S1: Nifty {sum(1 for r in rows if r['track']=='Skill v2' and r['index']=='NIFTY')}, "
          f"Bank {sum(1 for r in rows if r['track']=='Skill v2' and r['index']=='BANKNIFTY')}")

    # ---- (lA) v2 L1 (proper L1 engine, NOT the merged JSONs: those use the base
    # 11:30 rescan and drop 2 October v2 days; L1 reproduces October Family C exactly) ----
    from o1_la_l1 import run as la_l1_run
    la_trades = la_l1_run(strict=True)
    for t in la_trades:
        add("(lA) v2", t["symbol"], t["date"], t["setup"], t["direction"],
            t["morning_signal"], t["exit_reason"], t["net_rs"])
    print(f"(lA) v2 L1 uncapped: {len(la_trades)} "
          f"(Nifty {sum(1 for t in la_trades if t['symbol']=='NIFTY')}, "
          f"Bank {sum(1 for t in la_trades if t['symbol']=='BANKNIFTY')})")

    # ---- V5-v2 capped pool (index legs only) ----
    v5_unresolved = []
    for month in range(1, 11):
        p = os.path.join(BASE, f"capped_v2_summary_2026-{month:02d}.json")
        m = json.load(open(p))
        for t in m["unified_capped_trades"]:
            if t["symbol"] not in SYMS: continue
            key = (t["symbol"], t["date"])
            if t["method"] == "V4": sig_time = v4_sig.get(key, "")
            elif t["method"] == "Skill": sig_time = filt_sig.get(key, "")
            else: sig_time = ""
            if not sig_time: v5_unresolved.append((t["symbol"], t["date"], t["method"]))
            add("V5-v2", t["symbol"], t["date"], t["setup"], t["direction"],
                sig_time, t["exit_reason"], t["net_rs"])
    print(f"V5-v2 capped index trades: {sum(1 for r in rows if r['track']=='V5-v2')}, unresolved signal times: {v5_unresolved}")

    # ---- Apply O1 ----
    out = []
    for r in rows:
        if r["direction"] == "CE":
            kept, reason = True, "CE_kept_unchanged"
            orl, cs, ce, et = None, None, None, None
            # still compute entry time for the CSV where possible
            d = pd.Timestamp(r["date"]); tm = daymap[r["index"]].get(d)
            if tm and r["signal_time"] in tm["times"]:
                si = tm["times"].index(r["signal_time"])
                et = tm["times"][si + 1] if si + 1 < len(tm["times"]) else None
        elif not r["signal_time"]:
            kept, reason = False, "UNRESOLVED_signal_time"
            orl, cs, ce, et = None, None, None, None
        else:
            kept, reason, orl, cs, ce, et = o1_check(r["index"], r["date"], r["signal_time"])
        out.append({**r, "o1_kept": kept, "o1_reason": reason,
                    "confirmer": OTHER[r["index"]] if r["direction"] == "PE" else "",
                    "confirmer_or_low": orl, "confirmer_close_signal": cs,
                    "confirmer_close_entry": ce, "entry_time": et})
    pd.DataFrame(out).to_csv(os.path.expanduser("~/workspace/trading/index_options_o1_janoct_trades.csv"), index=False)

    # ---- Summaries ----
    ndays = 203  # per triple/merged Jan-Oct convention; verify below
    # actual trading-day count: distinct dates with spot bars Jan-Oct in either cache
    all_dates = set()
    for sym in SYMS:
        spot, _ = data[sym]
        all_dates |= set(spot[spot["date"] >= pd.Timestamp("2026-01-01")]["date"].dt.date.astype(str))
    print(f"distinct spot dates Jan-Oct (either symbol): {len(all_dates)}")
    tracks = [("V4", "NIFTY"), ("V4", "BANKNIFTY"), ("Skill v2", "NIFTY"), ("Skill v2", "BANKNIFTY"),
              ("(lA) v2", "NIFTY"), ("(lA) v2", "BANKNIFTY"), ("V5-v2", "NIFTY"), ("V5-v2", "BANKNIFTY")]
    summary = {}
    for track, sym in tracks:
        base = [r for r in out if r["track"] == track and r["index"] == sym]
        kept = [r for r in base if r["o1_kept"]]
        filt = [r for r in base if not r["o1_kept"]]
        def summ(rs):
            if not rs: return {"trades": 0, "net": 0.0, "win": "0/0", "win_pct": None, "ft": "0/0", "ft_pct": None, "per_week": 0.0}
            net = round(sum(r["net_rs"] for r in rs), 2)
            w = sum(1 for r in rs if r["win"]); f = sum(1 for r in rs if r["full_target"])
            return {"trades": len(rs), "net": net, "win": f"{w}/{len(rs)}", "win_pct": round(w / len(rs) * 100, 1),
                    "ft": f"{f}/{len(rs)}", "ft_pct": round(f / len(rs) * 100, 1), "per_week": round(len(rs) / ndays * 5, 2)}
        s = {"base": summ(base), "o1": summ(kept),
             "filtered": [{"date": r["date"], "direction": r["direction"], "setup": r["setup"],
                           "signal_time": r["signal_time"], "exit": r["exit_reason"], "net": r["net_rs"],
                           "outcome": "winner" if r["win"] else "loser", "reason": r["o1_reason"]} for r in filt],
             "filtered_winners": sum(1 for r in filt if r["win"]), "filtered_losers": sum(1 for r in filt if not r["win"]),
             "filtered_net": round(sum(r["net_rs"] for r in filt), 2)}
        summary[f"{track} {sym}"] = s
        print(f"\n{track} {sym}: BASE {s['base']} -> O1 {s['o1']} | filtered {len(filt)} "
              f"(winners {s['filtered_winners']}, losers {s['filtered_losers']}, filtered net {s['filtered_net']})")
        # October slice cross-check
        ob = [r for r in base if r["date"].startswith("2026-10")]
        ok = [r for r in ob if r["o1_kept"]]
        print(f"  OCT slice: base {len(ob)}/{round(sum(r['net_rs'] for r in ob),2)} -> O1 {len(ok)}/{round(sum(r['net_rs'] for r in ok),2)}")
        for r in filt:
            print(f"    FILT {r['date']} {r['direction']} {r['setup']} sig {r['signal_time']} {r['exit_reason']} {r['net_rs']} ({'winner' if r['win'] else 'loser'})")
    with open("/tmp/o1_janoct_summary.json", "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print("\nDONE")

if __name__ == "__main__":
    main()
