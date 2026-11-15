#!/usr/bin/env python3
"""NOVEMBER REGIME FIX — IOI-1 November counterfactual (the frozen
round5_ioi_score.py ran November only for its merge family, IOI-2).
Uses the gate scorer's own replay_entry / contract_bars / direction
logic verbatim; validates itself against 5 stored Jan-Oct IOI-1 legs
before scoring any November day. Local cache only, no API calls.
"""
import csv, json
from pathlib import Path

TR = Path.home() / "workspace/trading"
CH = TR / "round5_ioi_data" / "chunks"
LOT, COST = 30, 220.0

ds = {}
with open(TR / "round5_ioi_dataset.csv") as f:
    for r in csv.DictReader(f):
        ds[r["date"]] = r

_cache = {}
def contract_bars(exp, strike, typ, day):
    ck = (exp, strike, typ)
    if ck not in _cache:
        days = {}
        for fn in sorted(CH.glob(f"chunk_{exp}_{strike}{typ}_*.json")):
            body = json.loads(fn.read_text())
            for c in ((body.get("data") or {}).get("candles") or []):
                days.setdefault(c[0][:10], {})[c[0][11:16]] = (
                    float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                    float(c[5]), float(c[6]))
        _cache[ck] = days
    bars = _cache[ck].get(day)
    if not bars:
        return None
    return sorted((t, v[0], v[1], v[2], v[3]) for t, v in bars.items())

def replay_entry(bars, entry_time):
    if not bars:
        return None
    bs = [b for b in bars if b[0] >= entry_time]
    if not bs or bs[0][0] != entry_time:
        return None
    entry = bs[0][1]
    stop, target, sq = entry - 50.0, entry + 90.0, "15:10"
    def out(px, reason, t, ft):
        return dict(entry=entry, exit=px, exit_time=t, exit_reason=reason,
                    ft=ft, net=round((px - entry) * LOT - COST, 2))
    for (t, o, h, l, cl) in bs:
        if t > sq:
            break
        if l <= stop:
            return out(stop, "stop", t, 0)
        if h >= target:
            return out(target, "target", t, 1)
        if t == sq:
            return out(cl, "square_off", t, 0)
    lb = bs[-1]
    return out(lb[4], "square_off", lb[0], 0)

def direction(family, ce_q, pe_q):
    if family == "IOI-1":
        if ce_q == "LONG_BUILDUP" and pe_q != "LONG_BUILDUP":
            return "CE"
        if pe_q == "LONG_BUILDUP" and ce_q != "LONG_BUILDUP":
            return "PE"
    else:
        if ce_q == "SHORT_COVERING" and pe_q != "LONG_BUILDUP":
            return "CE"
        if pe_q == "SHORT_COVERING" and ce_q != "LONG_BUILDUP":
            return "PE"
    return None

def score_day(family, day, dirn, entry_time="11:00"):
    r = ds[day]
    strike = int(r["atm"])
    bars = contract_bars(r["expiry"], strike, dirn, day)
    if not bars:
        return None, "no_premium_candles"
    if bars[0][0] > "09:20":
        return None, "series_starts_after_0920"
    rep = replay_entry(bars, entry_time)
    if rep is None:
        return None, f"no_{entry_time}_bar"
    return dict(date=day, direction=dirn, strike=strike, **rep), None

# ---- self-validation: reproduce stored Jan-Oct IOI-1 real legs ----
stored = [r for r in csv.DictReader(open(TR / "round5_ioi_trades.csv"))
          if r["family"] == "IOI-1" and r["mode"] == "real"
          and r["window"] == "JANOCT"]
sample = [stored[i] for i in (0, 40, 80, 120, len(stored) - 1)]
for s in sample:
    got, why = score_day("IOI-1", s["date"], s["direction"])
    assert got is not None, (s["date"], why)
    assert (abs(got["entry"] - float(s["entry"])) < 1e-9
            and abs(got["exit"] - float(s["exit"])) < 1e-9
            and got["exit_time"] == s["exit_time"]
            and abs(got["net"] - float(s["net"])) < 1e-9), (s["date"], got, s)
print("self-validation: 5/5 stored IOI-1 legs reproduced EXACTLY")

# ---- November, both families, day by day ----
NOV_DAYS = sorted(d for d, r in ds.items() if r["window"] == "NOV")
out_rows = []
for fam in ("IOI-1", "IOI-2"):
    for d in NOV_DAYS:
        r = ds[d]
        if r["status"] != "complete":
            out_rows.append(dict(family=fam, date=d, status=r["status"],
                                 direction="", net=""))
            continue
        dirn = direction(fam, r["ce_q"], r["pe_q"])
        if not dirn:
            out_rows.append(dict(family=fam, date=d, status="no_fire",
                                 direction="", net=""))
            continue
        got, why = score_day(fam, d, dirn)
        if got is None:
            out_rows.append(dict(family=fam, date=d, status=f"NC:{why}",
                                 direction=dirn, net=""))
        else:
            out_rows.append(dict(family=fam, date=d, status="leg",
                                 direction=dirn, strike=got["strike"],
                                 entry=got["entry"], exit=got["exit"],
                                 exit_time=got["exit_time"],
                                 exit_reason=got["exit_reason"],
                                 net=got["net"]))
for r in out_rows:
    print(r)
with open(TR / "november_regime_ioi_nov_legs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["family", "date", "status", "direction",
                                      "strike", "entry", "exit", "exit_time",
                                      "exit_reason", "net"],
                       extrasaction="ignore")
    w.writeheader(); w.writerows(out_rows)
for fam in ("IOI-1", "IOI-2"):
    legs = [r for r in out_rows if r["family"] == fam and r["status"] == "leg"]
    print(fam, "November legs:", len(legs),
          "total:", round(sum(float(r["net"]) for r in legs), 2))
print("DONE")
