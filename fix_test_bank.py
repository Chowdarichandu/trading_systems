#!/usr/bin/env python3
"""FIX TEST 2026-11-02 — BANK NIFTY: break-hold confirmation for U1-pool OR-break legs.
Baseline = frozen B2 base pool as stored (historical_proof_bank_B2_trades.csv, 89 legs).
Variant  = each OR-break leg (Skill V3 among source systems) is taken ONLY if, after the
first 5-min close beyond the OR level (Skill V3 reconstruction, OR = 09:15-09:25 bars,
signal window 09:30-11:30), a later 5-min bar closes still beyond that level BEFORE any
bar closes back inside the OR; entry = open of the bar after the confirming close, on the
leg's ATM premium candle (strike = round(spot open of entry bar/100)*100, same rule as the
original prep); G0 exits -50/+90 stop-before-target incl. entry bar, square-off 15:10 close,
lot 30, cost Rs220. Non-OR legs pass through unchanged.
Placebo  = opposite option type at each confirmed leg's entry bar/strike (same G0 exits).
Paper only, real money Rs0. Premium candles: official caches first, then live fetch via the
expired-instruments route (browser UA), saved to fix_tests_2026-11-02_cache/ only.
"""
import csv, json, glob, urllib.request, urllib.parse
from pathlib import Path

TR = Path.home() / "workspace/trading"
SCRATCH = TR / "fix_tests_2026-11-02_cache"
CACHE_DIRS = [TR / "aggressive_data", TR / "v4_options_oct_data", TR / "historical_proof_data", SCRATCH]
COST, LOT = 220.0, 30
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"

def read_token():
    for line in (TR / "upstox_refresh/.env").read_text().splitlines():
        if line.startswith("UPSTOX_ACCESS_TOKEN="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no token")

# ---------------- spot ----------------
def load_spot():
    d = {}
    with open(TR / "data/progressive/BANKNIFTY/spot_5m.csv") as f:
        for r in csv.DictReader(f):
            day, t = r["timestamp"][:10], r["timestamp"][11:16]
            d.setdefault(day, []).append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    for day in d: d[day].sort()
    return d

# ---------------- contracts ----------------
def contract_map(expiry):
    m = {}
    for p in [TR / f"historical_proof_data/contracts_BANKNIFTY_{expiry}.json",
              TR / f"v4_options_oct_data/contracts_Nifty_Bank_{expiry}.json"]:
        if p.exists():
            for c in (json.loads(p.read_text()).get("data") or []):
                if c.get("weekly") is False:
                    m[(float(c["strike_price"]), c["instrument_type"])] = c["instrument_key"]
            if m: break
    return m

# ---------------- premium candles ----------------
def load_cached(strike, typ, day, exp):
    tag = f"BANKNIFTY_{int(strike)}{typ}_{day}_{exp}"
    cands = []
    for d in CACHE_DIRS:
        for name in (f"candles_{tag}.json", f"candles_premium_{tag}.json"):
            p = d / name
            if p.exists(): cands.append(p)
    if not cands:
        for d in CACHE_DIRS:
            cands += [Path(x) for x in glob.glob(str(d / f"candles_*BANKNIFTY*{int(strike)}{typ}_{day}*.json"))]
    # scratch fetch files
    sp = SCRATCH / f"candles_{tag}.json"
    if sp.exists() and sp not in cands: cands.insert(0, sp)
    for p in cands:
        try: data = json.loads(p.read_text()).get("data", {}).get("candles", [])
        except Exception: continue
        rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4]))
                for c in sorted(data, key=lambda c: c[0]) if c[0][:10] == day]
        if rows: return rows, f"cache:{p.name}"
    return None, None

def fetch_candles(strike, typ, day, exp, cmap, tok):
    key = cmap.get((float(strike), typ))
    if not key: return None, "NO_CONTRACT"
    url = (f"https://api.upstox.com/v2/expired-instruments/historical-candle/"
           f"{urllib.parse.quote(key, safe='')}/5minute/{day}/{day}")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}", "Accept": "application/json", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r: body = r.read().decode()
    except Exception as e:
        return None, f"FETCH_ERROR {type(e).__name__}"
    try: data = json.loads(body).get("data", {}).get("candles", [])
    except Exception: return None, "FETCH_BAD_JSON"
    if not data: return None, "FETCH_EMPTY"
    tag = f"BANKNIFTY_{int(strike)}{typ}_{day}_{exp}"
    (SCRATCH / f"candles_{tag}.json").write_text(body)
    rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4]))
            for c in sorted(data, key=lambda c: c[0]) if c[0][:10] == day]
    return (rows, "fetched") if rows else (None, "FETCH_NO_DAY_ROWS")

def get_candles(strike, typ, day, exp, cmap, tok):
    rows, src = load_cached(strike, typ, day, exp)
    if rows: return rows, src
    return fetch_candles(strike, typ, day, exp, cmap, tok)

# ---------------- G0 replay (verbatim convention from oct2026_fresh/score_fresh.py) ----
def replay_g0(bars, entry_time):
    idx = [i for i, b in enumerate(bars) if b[0] >= entry_time]
    if not idx: return None
    i0 = idx[0]
    if bars[i0][0] > "15:10" or bars[i0][0] != entry_time: return None
    entry = bars[i0][1]
    stop, target = entry - 50.0, entry + 90.0
    for b in bars[i0:]:
        t, o, h, l, c = b
        if t > "15:10": break
        if l <= stop: return dict(entry=entry, exit=stop, exit_time=t, exit_reason="stop", entry_bar=t if False else bars[i0][0])
        if h >= target: return dict(entry=entry, exit=target, exit_time=t, exit_reason="target", entry_bar=bars[i0][0])
        if t == "15:10": return dict(entry=entry, exit=c, exit_time=t, exit_reason="square_off", entry_bar=bars[i0][0])
    return None

def mins(t): return int(t[:2]) * 60 + int(t[3:5])
def plus5(t):
    m = mins(t) + 5
    return f"{m//60:02d}:{m%60:02d}"

def stats(nets_by_leg):
    nets = list(nets_by_leg)
    return round(sum(nets), 2)

def main():
    tok = read_token()
    spot = load_spot()
    legs = list(csv.DictReader(open(TR / "historical_proof_bank_B2_trades.csv")))
    cmaps = {e: contract_map(e) for e in sorted({r["expiry"] for r in legs})}

    # ---- baseline audit: replay stored legs, compare to stored net ----
    audit_bad = []
    for r in legs:
        bars, src = get_candles(int(float(r["strike"])), r["direction"], r["date"], r["expiry"], cmaps[r["expiry"]], tok)
        rep = replay_g0(bars, r["entry_time"]) if bars else None
        if rep is None:
            audit_bad.append((r["date"], r["direction"], "no replay")); continue
        net = round((rep["exit"] - rep["entry"]) * LOT - COST, 2)
        if abs(net - float(r["net_rs"])) > 0.01 or abs(rep["entry"] - float(r["entry_premium"])) > 0.01:
            audit_bad.append((r["date"], r["direction"], f"replay net {net} vs stored {r['net_rs']}"))
    print(f"BASELINE AUDIT: {len(legs)-len(audit_bad)}/{len(legs)} legs reproduce stored net exactly; mismatches: {audit_bad}")

    results = []   # one dict per leg
    timing_violations = []
    for r in legs:
        date, direc = r["date"], r["direction"]
        is_or = "Skill V3" in r["source_systems"]
        base_net = float(r["net_rs"])
        leg = dict(date=date, direction=direc, rep=r["representative_system"], sources=r["source_systems"],
                   is_or=is_or, base_entry=r["entry_time"], base_net=base_net,
                   base_reason=r["exit_reason"], base_exit=r["exit_time"],
                   base_strike=int(float(r["strike"])), expiry=r["expiry"])
        if not is_or:
            leg.update(variant_status="PASS_THROUGH", variant_net=base_net, variant_reason=r["exit_reason"],
                       variant_entry=r["entry_time"], variant_exit=r["exit_time"])
            results.append(leg); continue
        day = spot.get(date)
        if not day:
            leg.update(variant_status="NOT_COMPUTED", note="no spot bars"); results.append(leg); continue
        orb = [b for b in day if b[0] < "09:30"]
        orh = max(b[2] for b in orb); orl = min(b[3] for b in orb)
        level = orl if direc == "PE" else orh
        beyond = (lambda c: c < level) if direc == "PE" else (lambda c: c > level)
        sig = None
        for b in day:
            if "09:30" <= b[0] <= "11:30" and beyond(b[4]): sig = b; break
        if sig is None:
            leg.update(variant_status="NOT_COMPUTED", note="no OR-break close reconstructable in 09:30-11:30")
            results.append(leg); continue
        leg["signal_bar"] = sig[0]
        leg["signal_vs_stored"] = "match" if plus5(sig[0]) == r["entry_time"] else f"recon {plus5(sig[0])} vs stored entry {r['entry_time']}"
        # confirmation scan
        seq = [b for b in day if b[0] > sig[0]]
        conf_bar, rejected = None, False
        for b in seq:
            if beyond(b[4]): conf_bar = b; break
            else: rejected = True; break
        if rejected:
            leg.update(variant_status="REJECTED_NO_HOLD", variant_net=0.0, variant_reason="no_trade",
                       fail_bar=seq[0][0] if seq else "")
            results.append(leg); continue
        if conf_bar is None:
            leg.update(variant_status="REJECTED_NO_HOLD", variant_net=0.0, variant_reason="no_trade",
                       note="ran out of bars without an inside close (all beyond) — no next-bar entry before day end")
            results.append(leg); continue
        entry_time = plus5(conf_bar[0])
        if entry_time > "15:10":
            leg.update(variant_status="REJECTED_NO_HOLD", variant_net=0.0, variant_reason="no_trade",
                       note=f"confirmation too late (entry would be {entry_time})")
            results.append(leg); continue
        ebar = [b for b in day if b[0] == entry_time]
        if not ebar:
            leg.update(variant_status="NOT_COMPUTED", note="no spot entry bar"); results.append(leg); continue
        strike = int(round(ebar[0][1] / 100.0) * 100)
        bars, src = get_candles(strike, direc, date, r["expiry"], cmaps[r["expiry"]], tok)
        rep = replay_g0(bars, entry_time) if bars else None
        if rep is None:
            leg.update(variant_status="NOT_COMPUTED", note=f"premium unavailable ({src})", conf_bar=conf_bar[0],
                       variant_strike=strike)
            results.append(leg); continue
        vnet = round((rep["exit"] - rep["entry"]) * LOT - COST, 2)
        # timing audit: entry bar strictly after confirming bar; premium entry == open of entry bar
        if not (mins(entry_time) > mins(conf_bar[0]) and rep["entry_bar"] == entry_time):
            timing_violations.append((date, direc))
        leg.update(variant_status="CONFIRMED", variant_net=vnet, variant_reason=rep["exit_reason"],
                   variant_entry=entry_time, variant_exit=rep["exit_time"], variant_strike=strike,
                   variant_entry_premium=rep["entry"], conf_bar=conf_bar[0], candle_src=src)
        # placebo: opposite type, same entry bar & strike number
        opp = "CE" if direc == "PE" else "PE"
        pbars, psrc = get_candles(strike, opp, date, r["expiry"], cmaps[r["expiry"]], tok)
        prep = replay_g0(pbars, entry_time) if pbars else None
        if prep is None:
            leg["placebo_status"] = f"NOT_COMPUTED ({psrc})"
        else:
            leg["placebo_status"] = "COMPUTED"
            leg["placebo_net"] = round((prep["exit"] - prep["entry"]) * LOT - COST, 2)
            leg["placebo_reason"] = prep["exit_reason"]
        results.append(leg)

    json.dump(results, open(TR / "fix_tests_2026-11-02_cache/bank_results.json", "w"), indent=1, default=str)
    json.dump(dict(audit_bad=audit_bad, timing_violations=timing_violations),
              open(TR / "fix_tests_2026-11-02_cache/bank_audit.json", "w"), indent=1, default=str)

    # ---- summaries ----
    nc = [l for l in results if l["variant_status"] == "NOT_COMPUTED"]
    matched = [l for l in results if l["variant_status"] != "NOT_COMPUTED"]
    or_m = [l for l in matched if l["is_or"]]
    conf = [l for l in or_m if l["variant_status"] == "CONFIRMED"]
    rej = [l for l in or_m if l["variant_status"] == "REJECTED_NO_HOLD"]
    print(f"\nUNIVERSE: stored 89 | NOT_COMPUTED {len(nc)} | matched {len(matched)} (OR {len(or_m)}: confirmed {len(conf)}, rejected {len(rej)}; pass-through {len(matched)-len(or_m)})")
    for l in nc: print("  NC:", l["date"], l["direction"], l.get("note"))
    b_all = stats([l["base_net"] for l in results])
    b_m = stats([l["base_net"] for l in matched])
    v_m = stats([l["variant_net"] for l in matched])
    b_trades = len(matched); v_trades = sum(1 for l in matched if l["variant_reason"] != "no_trade")
    b_ft = sum(1 for l in matched if l["base_reason"] == "target")
    v_ft = sum(1 for l in matched if l.get("variant_reason") == "target")
    qs = lambda rows, nk, rk, ek: sum(1 for l in rows if l[rk] == "stop" and mins(l[ek]) - mins(l[nk]) <= 10)
    print(f"BASELINE full-89 net {b_all} | MATCHED baseline net {b_m} trades {b_trades} FT {b_ft}/{b_trades}")
    print(f"VARIANT  matched net {v_m} trades {v_trades} FT {v_ft}/{v_trades}")
    print(f"OR-leg quick stops: baseline {qs(or_m,'base_entry','base_reason','base_exit')} -> variant {qs(conf,'variant_entry','variant_reason','variant_exit')} (of {len(conf)} confirmed); rejected legs' baseline quick stops: {qs(rej,'base_entry','base_reason','base_exit')}")
    print(f"Rejected legs baseline net total: {stats([l['base_net'] for l in rej])} | Confirmed legs baseline net: {stats([l['base_net'] for l in conf])} -> variant net: {stats([l['variant_net'] for l in conf])}")
    pl = [l for l in conf if l.get("placebo_status") == "COMPUTED"]
    print(f"PLACEBO (opposite type at confirmed entries): n={len(pl)} net {stats([l['placebo_net'] for l in pl])} vs variant on same legs {stats([l['variant_net'] for l in pl])}")
    for label, rows in (("H1 Jan-May", [l for l in matched if l["date"] <= "2026-05-31"]),
                        ("H2 Jun-Oct", [l for l in matched if l["date"] >= "2026-06-01"])):
        print(f"{label}: baseline {stats([l['base_net'] for l in rows])} -> variant {stats([l['variant_net'] for l in rows])}")
    print("MONTHS (matched): month baseline -> variant")
    for m in range(1, 11):
        rows = [l for l in matched if l["date"][5:7] == f"{m:02d}"]
        if rows: print(f"  2026-{m:02d}: {stats([l['base_net'] for l in rows])} -> {stats([l['variant_net'] for l in rows])}  (n base {len(rows)}, variant trades {sum(1 for l in rows if l['variant_reason']!='no_trade')})")
    for name, key in (("baseline", "base_net"), ("variant", "variant_net")):
        top3 = sorted(matched, key=lambda l: -l[key])[:3]
        rest = stats([l[key] for l in matched]) - stats([l[key] for l in top3])
        print(f"EX-TOP3 {name}: total {stats([l[key] for l in matched])} minus top3 {[round(l[key],2) for l in top3]} = {round(rest,2)}")
    print("TIMING VIOLATIONS:", timing_violations)

if __name__ == "__main__":
    main()
