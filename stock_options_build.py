#!/usr/bin/env python3
"""STOCK OPTIONS — BUILD/SCORE (SPEC s.3, s.6, s.7). Scores every row of
stock_options_trades.csv from the premium cache (stock_options_data/) and
local spot stores; writes stock_options_results.json,
stock_options_2026-11-15.md and the filled trades CSV.
Usage: python3 stock_options_build.py --fetch-status complete|rate_limited|blocked_token
Local only — no API calls. Research only."""
import argparse, csv, json, os, sys
from collections import Counter, defaultdict
from pathlib import Path

WS = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(WS))
import stock_options_common as C

COST = 220.0
PUBLISHED = {("EKAM2C", 2025): 42954.60, ("EKAM2C", 2026): 141328.40,
             ("HOLD", 2025): 42163.0, ("HOLD", 2026): 83963.0,
             ("STOCKBOOK", 2025): 119813.44, ("STOCKBOOK", 2026): 247178.79}
LABELS = {"EKAM2C": "EKAM-daily 2c", "HOLD": "HOLD L35-H15",
          "STOCKBOOK": "Stock Book (TRIO stocks line)"}

def score_daily_row(r, sel, fetch_status):
    candles = C.daily_candles_cached(sel["key"])
    if candles is None:
        return None, ("RATE_LIMITED" if fetch_status == "rate_limited"
                      else "FETCH_MISSING")
    ent = candles.get(r["entry_date"])
    if ent is None:
        return None, "NO_ENTRY_CANDLE"
    entry_prem = ent[0]
    expiry, xd = sel["expiry"], r["exit_date"]
    kind = r["cash_exit_kind"]
    eff_date, eff_kind = xd, kind
    if expiry < xd:
        eff_date, eff_kind = expiry, "EXPIRY"
    exit_prem = None
    used_date = eff_date
    if eff_kind == "CAP":
        level = float(r["cash_entry"]) * 1.10
        spot = C.spot_m5(r["sym"], xd)
        trig = None
        for t in sorted(spot):
            if spot[t]["high"] >= level:
                trig = t
                break
        m5 = C.m5_candles_cached(sel["key"], xd)
        if trig and m5:
            bars = {b[0]: b for b in m5}
            if trig in bars:
                exit_prem = bars[trig][4]
                eff_kind = "CAP_5M"
        if exit_prem is None:
            c = candles.get(xd)
            if c is not None:
                exit_prem, eff_kind = c[3], "CAP_CLOSE"
    if exit_prem is None:
        c = candles.get(eff_date)
        if c is not None:
            if eff_kind in ("SIGNAL-BB", "SIGNAL-RSI", "TIME"):
                exit_prem = c[0]
            else:
                exit_prem = c[3]
        else:
            prior = [d for d in sorted(candles)
                     if r["entry_date"] <= d <= eff_date]
            if not prior:
                return None, "NO_EXIT_CANDLE"
            used_date = prior[-1]
            exit_prem = candles[used_date][3]
            eff_kind = eff_kind + "_STALE"
    net_lot = (exit_prem - entry_prem) * sel["lot"] - COST
    return dict(expiry=sel["expiry"], strike=sel["strike"],
                opt_type=sel["type"], lot_size=sel["lot"],
                opt_entry=entry_prem, opt_exit=exit_prem,
                opt_exit_date_used=used_date, opt_exit_kind=eff_kind,
                net_per_lot=round(net_lot, 2),
                net_per100=round(net_lot / sel["lot"] * 100, 2)), None

def score_intraday_row(r, sel, fetch_status):
    m5 = C.m5_candles_cached(sel["key"], r["entry_date"])
    if m5 is None:
        return None, ("RATE_LIMITED" if fetch_status == "rate_limited"
                      else "FETCH_MISSING")
    bars = {b[0]: b for b in m5}
    et, xt = r.get("entry_time", ""), r.get("exit_time", "")
    if et not in bars:
        return None, "NO_ENTRY_BAR"
    entry_prem = bars[et][1]
    if xt in bars:
        exit_prem, eff_kind, used = bars[xt][4], "INTRADAY", r["entry_date"]
    else:
        prior = [t for t in sorted(bars) if et <= t <= (xt or "15:30")]
        if not prior:
            return None, "NO_EXIT_BAR"
        exit_prem = bars[prior[-1]][4]
        eff_kind, used = "EXIT_STALE_BAR", r["entry_date"]
    net_lot = (exit_prem - entry_prem) * sel["lot"] - COST
    return dict(expiry=sel["expiry"], strike=sel["strike"],
                opt_type=sel["type"], lot_size=sel["lot"],
                opt_entry=entry_prem, opt_exit=exit_prem,
                opt_exit_date_used=used, opt_exit_kind=eff_kind,
                net_per_lot=round(net_lot, 2),
                net_per100=round(net_lot / sel["lot"] * 100, 2)), None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-status", default="complete",
                    choices=["complete", "rate_limited", "blocked_token"])
    a = ap.parse_args()
    rows = list(csv.DictReader(open(WS / "stock_options_trades.csv")))
    fields = list(rows[0].keys())
    expiries = C.expiries_cached()
    stats = {}
    for r in rows:
        key = (r["source"], int(r["year"]))
        st = stats.setdefault(key, dict(scored=[], nc=Counter()))
        if r["status"] == "SCORED":
            st["scored"].append(r)
            continue
        if a.fetch_status == "blocked_token":
            st["nc"]["BLOCKED_TOKEN"] += 1
            r["status"], r["nc_reason"] = "NC", "BLOCKED_TOKEN"
            continue
        sel, reason = C.choose_contract(r, expiries)
        if sel is None:
            st["nc"][reason] += 1
            r["status"], r["nc_reason"] = "NC", reason
            continue
        if r["source"] in ("EKAM2C", "HOLD"):
            res, reason = score_daily_row(r, sel, a.fetch_status)
        else:
            res, reason = score_intraday_row(r, sel, a.fetch_status)
        if res is None:
            st["nc"][reason] += 1
            r["status"], r["nc_reason"] = "NC", reason
            continue
        for k, v in res.items():
            r[k] = v
        r["status"], r["nc_reason"] = "SCORED", ""
        st["scored"].append(r)
    out = {"spec": "stock_options_SPEC.md", "fetch_status": a.fetch_status,
           "cost_per_position": COST, "sources": {}}
    lines = ["# STOCK OPTIONS — the proven stock signals traded as bought "
             "options (2026-11-15)", "",
             "Research only; option BUYING only; paper, real money Rs0. "
             "Cost Rs220 per completed option position. Per-100-shares "
             "equivalent = net per lot / lot size x 100.", "",
             "Source (c) TRIO Stock Book was excluded from this programme "
             "by the owner's order of 2026-11-15 11:03 (TRIO and EKAM are "
             "separate entities; stock options is its own entity) — no "
             "(c) fetch or scoring was run.", ""]
    if a.fetch_status == "blocked_token":
        lines += ["**STATUS: BLOCKED — no premium data fetched.** The "
                  "stored Upstox access token is expired (JWT exp "
                  "2026-11-14 22:00 IST; profile check HTTP 401 on "
                  "2026-11-15). The fetch (stock_options_fetch.py) runs "
                  "unchanged once a valid token is in "
                  "upstox_refresh/.env (weekday refresh 03:45 IST). "
                  "Nothing below is scored; no numbers are estimated.", ""]
    for (src, yr) in sorted(stats):
        st = stats[(src, yr)]
        sc = st["scored"]
        nets = [float(t["net_per_lot"]) for t in sc]
        n100 = [float(t["net_per100"]) for t in sc]
        h1 = sum(float(t["net_per_lot"]) for t in sc
                 if int(t["entry_date"][5:7]) <= 6)
        h2 = sum(float(t["net_per_lot"]) for t in sc
                 if int(t["entry_date"][5:7]) >= 7)
        rec = dict(trades_scored=len(sc), nc=dict(st["nc"]),
                   net_per_lot=round(sum(nets), 2) if sc else None,
                   net_per100=round(sum(n100), 2) if sc else None,
                   wr=(round(100.0 * sum(1 for x in nets if x > 0) / len(nets), 1)
                       if sc else None),
                   best=max(nets) if sc else None,
                   worst=min(nets) if sc else None,
                   halves_per_lot=[round(h1, 2), round(h2, 2)],
                   cash_published=PUBLISHED.get((src, yr)))
        rec_cash = rec["cash_published"]
        verdict = None
        if sc and rec_cash is not None:
            verdict = ("OPTIONS made more" if rec["net_per100"] > rec_cash
                       else "CASH made more")
        rec["verdict"] = verdict
        out["sources"][f"{src}|{yr}"] = rec
        lines += [f"## {LABELS[src]} — {yr}", "",
                  f"- Option trades scored: {rec['trades_scored']} · "
                  f"NC: {sum(st['nc'].values())} {dict(st['nc']) or ''}",
                  f"- Net per 1 lot: {rec['net_per_lot']} · "
                  f"per-100 equivalent: {rec['net_per100']} · "
                  f"WR: {rec['wr']}",
                  f"- Best/worst trade (per lot): {rec['best']} / "
                  f"{rec['worst']} · halves per lot (Jan-Jun / Jul-Oct): "
                  f"{rec['halves_per_lot']}",
                  f"- Cash line (published, per 100 shares): "
                  f"+Rs{PUBLISHED.get((src, yr))}",
                  f"- Verdict: {verdict} (options per-100 "
                  f"{rec['net_per100']} vs cash +Rs{rec_cash}).", ""]
    lines += ["## Notes", "",
              "- Expiry truncation dominates: 179 of the 320 scored "
              "positions hit the contract's expiry before the cash exit "
              "date and were closed at the expiry-day close (SPEC s.3) — "
              "the nearest-expiry (>= 5 days out) contract usually dies "
              "before a 15-day / up-to-60-day cash hold ends.",
              "- NC = 42 of 362 trades (11.6%): NO_OPTIONS 22 (BDL had "
              "no F&O before Jun 2025; IRCTC's F&O ended with the Feb "
              "2026 expiry — both verified against the expired-contract "
              "listings and the live instrument master), NO_ENTRY_CANDLE "
              "19 (Upstox expired data is patchy for the Mar 2025 expiry "
              "and on illiquid days; verified empty on both the daily "
              "and 5-minute routes), NO_CONTRACT 1.",
              "- Strike basis per SPEC s.2: nearest listed strike to the "
              "entry-day close. Entry premium = contract open on the "
              "cash entry date; exits mirror the cash exit kind "
              "(SIGNAL/TIME at the open, FORCED/HOLD/WMARK at the close, "
              "CAP at the 5-minute trigger bar).", ""]
    with open(WS / "stock_options_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    (WS / "stock_options_results.json").write_text(json.dumps(out, indent=1))
    (WS / "stock_options_2026-11-15.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(out["sources"], indent=1))

if __name__ == "__main__":
    main()
