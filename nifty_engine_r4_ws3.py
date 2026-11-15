#!/usr/bin/env python3
"""ROUND 4 WS3 — Nifty second-leg family (Cycles 92-97), frozen in
nifty_engine_frozen.md Round-4 WS3 before scoring. NS1 shape transplanted
onto the current candidate book's premium-scored exits. Per-base-leg
searches in entry-time order; a gated-out first crossing ends that base
leg's search; at most one second leg per day."""
import sys, json, math
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r4_harness import (candidate_legs, score_r4, run_r4,
                                     set_current, CURRENT, DAILY, PREV,
                                     spot5m, candles_exact)

S5 = spot5m()
QUAL = {"stop", "be_stop", "runner_stop", "runner_target"}
EXPIRIES = ["2026-01-27", "2026-02-24", "2026-03-30", "2026-04-28", "2026-05-26",
            "2026-06-30", "2026-07-28", "2026-08-25", "2026-09-29", "2026-10-27"]

def monthly_expiry(d):
    for e in EXPIRIES:
        if d <= e: return e
    return None

def second_legs(book_legs, res, room_min, window):
    by_key = {(r["date"], r["direction"]): r for r in res}
    days = defaultdict(list)
    for l in book_legs: days[l["date"]].append(l)
    out, trace = [], []
    for d in sorted(days):
        bases = sorted(days[d], key=lambda x: x["entry_time"])
        sb = S5.get(d, [])
        if not sb: continue
        orc = [b for b in sb if b[0] < "09:30"]
        orh = max(b[2] for b in orc); orl = min(b[3] for b in orc)
        p = PREV[d]; pd = DAILY[p]
        rng = pd["h"] - pd["l"]
        bias_pos = (pd["c"] - pd["l"]) / rng * 100 if rng else 50.0
        bearish = bias_pos < 35
        levels = sorted({pd["h"], pd["c"], pd["l"]})
        book_keys = {(l["date"], l["direction"]) for l in book_legs}
        for base in bases:
            r = by_key[(base["date"], base["direction"])]
            if r["exit_reason"] not in QUAL or r["exit_time"] > "13:30":
                continue
            xi = next((i for i, b in enumerate(sb) if b[0] == r["exit_time"]), None)
            if xi is None: continue
            leg = None; why = "no crossing"
            for j in range(xi + 1, len(sb)):
                t, o, h, l_, c, v = sb[j]
                if t > window: break
                pc = sb[j - 1][4]
                d2 = None
                if c > orh and not (pc > orh): d2 = "CE"
                elif c < orl and not (pc < orl): d2 = "PE"
                if d2 is None: continue
                # first crossing found — gates decide, search ends either way
                if d2 == "CE" and bearish:
                    why = f"cross {t} CE blocked bearish-bias"; break
                if j + 1 >= len(sb):
                    why = f"cross {t} {d2} no entry bar"; break
                entry_spot = sb[j + 1][1]
                risk = abs(entry_spot - (l_ if d2 == "CE" else h))
                if risk == 0:
                    why = f"cross {t} {d2} zero risk"; break
                if d2 == "CE":
                    nxt = [x for x in levels if x > c]
                    room = (min(nxt) - c) if nxt else math.inf
                else:
                    nxt = [x for x in levels if x < c]
                    room = (c - max(nxt)) if nxt else math.inf
                rr = room / risk
                if rr < room_min:
                    why = f"cross {t} {d2} room {rr:.2f} < {room_min}"; break
                exp = monthly_expiry(d)
                if exp is None or exp == d:
                    why = f"cross {t} {d2} expiry-day skip"; break
                strike = int(round(entry_spot / 100.0) * 100)
                leg = dict(index="NIFTY", date=d, direction=d2, strike=strike,
                           expiry=exp, entry_time=sb[j + 1][0],
                           rep="NS1-2L (R4)", sources="NS1-R4",
                           signal_time=t, room_ratio=round(rr, 2))
                why = f"cross {t} {d2} rr {rr:.2f} -> entry {leg['entry_time']} @{strike}"
                break
            trace.append((d, base["direction"], r["exit_reason"], r["exit_time"], why))
            if leg is not None:
                if (d, leg["direction"]) in book_keys:
                    trace.append((d, "DEDUP", "", "", f"second leg {leg['direction']} dropped (already in book)"))
                else:
                    out.append(leg)
                break  # one second leg per day
    return out, trace

CELLS = [(1.5, "14:30"), (1.4, "14:00"), (1.4, "14:30"),
         (1.5, "14:00"), (1.6, "14:00"), (1.6, "14:30")]

if __name__ == "__main__":
    book = candidate_legs()
    res, nc, _ = score_r4(book)
    if "--discover" in sys.argv:
        seen = {}
        for room_min, window in CELLS:
            legs2, trace = second_legs(book, res, room_min, window)
            print(f"cell room {room_min} window {window}: {len(legs2)} second legs")
            for l in legs2:
                k = (l["date"], l["direction"], l["strike"], l["expiry"])
                cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
                seen[k] = bool(cs)
                print(f"    LEG {l['date']} {l['direction']} {l['strike']} exp {l['expiry']} "
                      f"entry {l['entry_time']} rr {l['room_ratio']} candles {'OK' if cs else 'MISSING'}")
        Path("nifty_engine_r4_ws3_legs.json").write_text(json.dumps(
            {f"{k[0]}|{k[1]}|{k[2]}|{k[3]}": v for k, v in seen.items()}, indent=1))
    else:
        cyc = 92
        summary = {}
        for room_min, window in CELLS:
            legs2, trace = second_legs(book, res, room_min, window)
            legs = book + legs2
            name = f"run3r4_c{cyc}_ns1_r{room_min}_w{window.replace(':', '')}"
            c, _ = run_r4(name, legs)
            summary[cyc] = dict(room=room_min, window=window, second_legs=len(legs2),
                                leg_keys=[(l["date"], l["direction"], l["strike"]) for l in legs2],
                                total=c["total"], n=c["n"], ft=c["ft_pct"],
                                banked=c["gate_vs_current"]["banked"],
                                flagged=c["gate_vs_current"]["flagged_freq_only"],
                                failed=[k for k, v in c["gate_vs_current"]["checks"].items() if not v],
                                trace=[list(t) for t in trace])
            if c["gate_vs_current"]["banked"]:
                set_current(c, f"Round-4 Cycle {cyc} (NS1-2L room {room_min} window {window})")
                print(f"*** BANKED Cycle {cyc}: new current = {CURRENT['total']:+,.2f}")
                # second legs for later cells must be recomputed on the new book
                book = candidate_legs() if False else book  # book legs unchanged; exits unchanged
            cyc += 1
        Path("nifty_engine_r4_ws3_results.json").write_text(json.dumps(summary, indent=1))
        print("\nWS3 done. Current candidate:", CURRENT["label"], f"{CURRENT['total']:+,.2f}")
