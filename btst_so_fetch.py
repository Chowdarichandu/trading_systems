#!/usr/bin/env python3
"""BTST-STOCK-OPTIONS (LIQUID-ONLY) — FETCH. Spec: btst_so_SPEC.md.
Stage 'screen': expiry discovery + ATM-CE daily candles (with volume) for
all 25 names x Jan-2025..Oct-2026 -> btst_so_data/screen_daily_*.json,
then the s.2 screen table -> btst_so_data/screen_results.json.
Stage 'trades': 5-min bars for every real + placebo signal contract on the
qualifying names -> btst_so_data/m5_*.json.
Programme route only (stock_options_fetch), browser UA, pacing >= 0.45s.
HTTP 429 = hard stop (exit 3); caches/checkpoints are kept and resumable.
Token check failure: exit 2 before any data call. Research only."""
import json, sys
from datetime import date
from pathlib import Path
from urllib.parse import quote

WS = Path(__file__).resolve().parent
sys.path.insert(0, str(WS))
import btst_so_common as B
import stock_options_fetch as F

DATA = B.DATA
DATA.mkdir(exist_ok=True)

def fetch_screen_daily(key, frm, to):
    fn = DATA / f"screen_daily_{key.replace('|', '_')}.json"
    if fn.exists():
        return
    if key in F.LIVE_KEYS:
        s, body = F.get(f"/v3/historical-candle/{quote(key, safe='')}"
                        f"/days/1/{to}/{frm}")
    else:
        s, body = F.get(f"/v2/expired-instruments/historical-candle/"
                        f"{quote(key, safe='')}/day/{to}/{frm}")
    rows = (body.get("data") or {}).get("candles") if isinstance(body, dict) else None
    if s != 200:
        print(f"  screen daily FAILED (HTTP {s}), not cached: {key}")
        return
    out = [[c[0][:10], float(c[1]), float(c[2]), float(c[3]), float(c[4]),
            float(c[5]) if len(c) > 5 else 0.0] for c in rows or []]
    fn.write_text(json.dumps(out))

def fetch_m5(key, day):
    if B.m5_bars(key, day) is not None:
        return
    fn = DATA / f"m5_{key.replace('|', '_')}_{day}.json"
    if key in F.LIVE_KEYS:
        s, body = F.get(f"/v3/historical-candle/{quote(key, safe='')}"
                        f"/minutes/5/{day}/{day}")
    else:
        s, body = F.get(f"/v2/expired-instruments/historical-candle/"
                        f"{quote(key, safe='')}/5minute/{day}/{day}")
    rows = (body.get("data") or {}).get("candles") if isinstance(body, dict) else None
    if s != 200:
        print(f"  m5 FAILED (HTTP {s}), not cached: {key} {day}")
        return
    out = [[c[0][11:16], float(c[1]), float(c[2]), float(c[3]),
            float(c[4])] for c in rows or []]
    fn.write_text(json.dumps(out))

# ---------------- stage: screen ----------------
def atm_ce(sym, expiry, ref_close):
    pool = B.contracts(sym, expiry)
    if not pool:
        return None
    ces = [c for c in pool if c["type"] == "CE"]
    if not ces:
        return None
    ces.sort(key=lambda c: (abs(c["strike"] - ref_close), c["strike"]))
    return ces[0]

def stage_screen():
    prog_fn = DATA / "screen_progress.json"
    prog = json.loads(prog_fn.read_text()) if prog_fn.exists() else {}
    for sym in B.NAMES:
        daily = B.spot_daily(sym)
        ss = sorted(daily)
        for (y, m) in B.MONTHS:
            tag = f"{sym}|{y}-{m:02d}"
            if prog.get(tag) == "done":
                continue
            expiry = F.discover_expiry(sym, y, m)
            if expiry and not B.contracts(sym, expiry):
                F.probe_contracts(sym, expiry)
            prog[tag] = "done"
            prog_fn.write_text(json.dumps(prog))
            print(f"screen discovery {tag}: expiry {expiry}")
        # daily candles for this name's ATM CEs
        for (y, m) in B.MONTHS:
            expiry = B.expiries().get(f"{sym}|{y}-{m:02d}")
            if not expiry:
                continue
            prev = [d for d in ss if d < f"{y}-{m:02d}-01"]
            if not prev:
                continue
            ref = daily[prev[-1]]["close"]
            atm = atm_ce(sym, expiry, ref)
            if atm is None:
                continue
            span = [d for d in ss if f"{y}-{m:02d}-01" <= d <= expiry]
            if not span:
                continue
            fetch_screen_daily(atm["key"], span[0], expiry)
        print(f"screen candles done: {sym}")
    # ---- compute the s.2 screen table
    table = {}
    for sym in B.NAMES:
        daily = B.spot_daily(sym)
        ss = sorted(daily)
        tot_span = tot_traded = 0
        vols = []
        reasons = []
        for (y, m) in B.MONTHS:
            expiry = B.expiries().get(f"{sym}|{y}-{m:02d}")
            span = [d for d in ss
                    if f"{y}-{m:02d}-01" <= d <= (expiry or f"{y}-{m:02d}-31")]
            if not expiry:
                tot_span += len(span)
                reasons.append(f"{y}-{m:02d}:NO_EXPIRY")
                continue
            prev = [d for d in ss if d < f"{y}-{m:02d}-01"]
            atm = atm_ce(sym, expiry, daily[prev[-1]]["close"]) if prev else None
            if atm is None:
                tot_span += len(span)
                reasons.append(f"{y}-{m:02d}:NO_CONTRACTS")
                continue
            rows = B.screen_daily(atm["key"]) or []
            traded = {r[0] for r in rows}
            tot_span += len(span)
            tot_traded += sum(1 for d in span if d in traded)
            vols += [r[5] for r in rows if r[0] in set(span)]
        vols.sort()
        med = vols[len(vols) // 2] if vols else 0.0
        table[sym] = dict(
            span_sessions=tot_span, traded_sessions=tot_traded,
            coverage=(tot_traded / tot_span if tot_span else 0.0),
            median_daily_volume=med, month_reasons=reasons)
    ranked = sorted(table, key=lambda s: -table[s]["median_daily_volume"])
    for i, sym in enumerate(ranked):
        table[sym]["volume_rank"] = i + 1
    for sym in B.NAMES:
        t = table[sym]
        t["qualified"] = bool(t["coverage"] >= 0.90 and t["volume_rank"] <= 8)
    (DATA / "screen_results.json").write_text(json.dumps(table, indent=1))
    q = [s for s in B.NAMES if table[s]["qualified"]]
    print("QUALIFIED:", q)
    for s in B.NAMES:
        t = table[s]
        print(f"  {s}: cov {t['coverage']:.3f} vol {t['median_daily_volume']:.0f} "
              f"rank {t['volume_rank']} -> {'QUALIFY' if t['qualified'] else 'reject'}")
    return 0

# ---------------- stage: trades ----------------
def stage_trades():
    table = json.loads((DATA / "screen_results.json").read_text())
    quals = {s for s, t in table.items() if t["qualified"]}
    print("qualifiers:", sorted(quals))
    plan = set()
    for sig in B.signals():
        if sig["sym"] not in quals:
            continue
        for arm, t in (("REAL", sig["t"]), ("PLACEBO", None)):
            if arm == "PLACEBO":
                t = B.placebo_day(sig["sym"], sig["t"])
                if t is None:
                    continue
                xs = B.next_session(sig["sym"], t)
            else:
                xs = sig["exit_session"]
            sel, reason = B.choose_contract(sig["sym"], t)
            if sel is None:
                continue
            plan.add((sel["key"], t))
            if xs:
                plan.add((sel["key"], xs))
    print(f"m5 pulls needed: {len(plan)}")
    for key, day in sorted(plan):
        fetch_m5(key, day)
    print("trades fetch complete")
    return 0

def main():
    s, _ = F.get("/v2/user/profile")
    if s != 200:
        print("BLOCKED_TOKEN: profile check failed, no data calls made")
        return 2
    print("token OK")
    stage = sys.argv[1] if len(sys.argv) > 1 else "screen"
    try:
        if stage == "screen":
            return stage_screen()
        return stage_trades()
    except F.RateLimited:
        print("RATE_LIMITED: attempt hard-stopped; caches/checkpoints kept.")
        return 3

if __name__ == "__main__":
    sys.exit(main())
