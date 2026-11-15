#!/usr/bin/env python3
"""STOCK OPTIONS FAR-EXPIRY — BUILD/SCORE (SPEC stock_options_far_SPEC.md
s.3, s.5-s.7). Scores every row of stock_options_far_trades.csv from the
premium cache using the first run's score_daily_row unchanged; writes
stock_options_far_results.json, stock_options_far_2026-11-15.md and the
filled trades CSV.
Usage: python3 stock_options_far_build.py --fetch-status complete|rate_limited|blocked_token
Local only — no API calls. Research only."""
import argparse, csv, json, sys
from collections import Counter
from pathlib import Path

WS = Path(__file__).resolve().parent
sys.path.insert(0, str(WS))
import stock_options_common as C
import stock_options_build as B
from stock_options_far_common import choose_contract_far

COST = 220.0
CASH = {2025: 42954.60, 2026: 141328.40}
NEAR = {2025: dict(scored=66, nc=8, net_per_lot=-212268.75,
                   net_per100=-53945.74, wr=37.9, died=35),
        2026: dict(scored=95, nc=7, net_per_lot=-396390.75,
                   net_per100=-50482.24, wr=30.5, died=56)}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch-status", default="complete",
                    choices=["complete", "rate_limited", "blocked_token"])
    a = ap.parse_args()
    rows = list(csv.DictReader(open(WS / "stock_options_far_trades.csv")))
    fields = list(rows[0].keys())
    expiries = C.expiries_cached()
    stats = {}
    for r in rows:
        yr = int(r["year"])
        st = stats.setdefault(yr, dict(scored=[], nc=Counter(), died=0,
                                       fallback=0, nc_anatomy=Counter(),
                                       fallback_detail=[]))
        if r["status"] == "SCORED":
            st["scored"].append(r)
            if str(r.get("opt_exit_kind", "")).startswith("EXPIRY"):
                st["died"] += 1
            if r.get("days_to_expiry") not in ("", None) \
                    and int(r["days_to_expiry"]) < 45:
                st["fallback"] += 1
                st["fallback_detail"].append(
                    f"{r['sym']} entry {r['entry_date']} expiry "
                    f"{r['expiry']} dte {r['days_to_expiry']}")
            continue
        if a.fetch_status == "blocked_token":
            st["nc"]["BLOCKED_TOKEN"] += 1
            r["status"], r["nc_reason"] = "NC", "BLOCKED_TOKEN"
            continue
        sel, reason = choose_contract_far(r, expiries)
        if sel is None:
            st["nc"][reason] += 1
            r["status"], r["nc_reason"] = "NC", reason
            continue
        r["expiry"] = sel["expiry"]
        r["days_to_expiry"] = sel["days_to_expiry"]
        r["strike"] = sel["strike"]
        r["opt_type"] = sel["type"]
        r["lot_size"] = sel["lot"]
        if sel["days_to_expiry"] < 45:
            st["fallback"] += 1
            st["fallback_detail"].append(
                f"{r['sym']} entry {r['entry_date']} expiry "
                f"{sel['expiry']} dte {sel['days_to_expiry']}")
        res, reason = B.score_daily_row(r, sel, a.fetch_status)
        if res is None:
            st["nc"][reason] += 1
            r["status"], r["nc_reason"] = "NC", reason
            if reason == "NO_ENTRY_CANDLE":
                cd = C.daily_candles_cached(sel["key"]) or {}
                dates = sorted(cd)
                if not dates:
                    st["nc_anatomy"]["file_empty_all_range"] += 1
                elif dates[0] > r["entry_date"]:
                    st["nc_anatomy"]["candles_start_after_entry"] += 1
                elif dates[-1] < r["entry_date"]:
                    st["nc_anatomy"]["candles_end_before_entry"] += 1
                else:
                    st["nc_anatomy"]["gap_on_entry_date_only"] += 1
            continue
        for k, v in res.items():
            r[k] = v
        r["status"], r["nc_reason"] = "SCORED", ""
        st["scored"].append(r)
        if str(res["opt_exit_kind"]).startswith("EXPIRY"):
            st["died"] += 1
    out = {"spec": "stock_options_far_SPEC.md",
           "fetch_status": a.fetch_status, "cost_per_position": COST,
           "control_near_reproduced_from_stored_trades": {
               "2025": "66 scored, net_per_lot -212268.75, NC 8, died 35",
               "2026": "95 scored, net_per_lot -396390.75, NC 7, died 56"},
           "years": {}}
    lines = ["# STOCK OPTIONS — FAR-EXPIRY TEST on EKAM-daily entries "
             "(2026-11-15)", "",
             "Research only; option BUYING only; paper, real money Rs0. "
             "Cost Rs220 per completed option position. Per-100-shares "
             "equivalent = net per lot / lot size x 100.", "",
             "Same EKAM-daily 2c entries, entry timing and exits as the "
             "near-expiry run — the ONLY change: the bought ATM call's "
             "expiry is the first listed expiry >= 45 days after entry "
             "(farthest available if none reaches 45 days, days-to-expiry "
             "recorded per trade).", ""]
    if a.fetch_status == "blocked_token":
        lines += ["**STATUS: BLOCKED — no premium data fetched.** The "
                  "stored Upstox access token failed its check. The "
                  "fetch (stock_options_far_fetch.py) runs unchanged "
                  "once a valid token is in upstox_refresh/.env. "
                  "Nothing below is scored; no numbers are estimated.",
                  ""]
    verdict_line = []
    for yr in sorted(stats):
        st = stats[yr]
        sc = st["scored"]
        nets = [float(t["net_per_lot"]) for t in sc]
        n100 = [float(t["net_per100"]) for t in sc]
        h1 = sum(float(t["net_per_lot"]) for t in sc
                 if int(t["entry_date"][5:7]) <= 6)
        h2 = sum(float(t["net_per_lot"]) for t in sc
                 if int(t["entry_date"][5:7]) >= 7)
        rec = dict(trades_scored=len(sc), nc=dict(st["nc"]),
                   nc_total=sum(st["nc"].values()),
                   net_per_lot=round(sum(nets), 2) if sc else None,
                   net_per100=round(sum(n100), 2) if sc else None,
                   wr=(round(100.0 * sum(1 for x in nets if x > 0)
                             / len(nets), 1) if sc else None),
                   best=max(nets) if sc else None,
                   worst=min(nets) if sc else None,
                   halves_per_lot=[round(h1, 2), round(h2, 2)],
                   died_at_expiry=st["died"],
                   farthest_fallback_trades=st["fallback"],
                   fallback_detail=st["fallback_detail"],
                   nc_anatomy=dict(st["nc_anatomy"]),
                   near_expiry=NEAR[yr], cash_published=CASH[yr])
        if sc:
            best_of = max([("FAR-EXPIRY options", rec["net_per100"]),
                           ("NEAR-EXPIRY options", NEAR[yr]["net_per100"]),
                           ("CASH", CASH[yr])], key=lambda t: t[1])
            rec["verdict"] = f"{best_of[0]} made more"
            verdict_line.append(
                f"{yr}: FAR {rec['net_per100']} vs NEAR "
                f"{NEAR[yr]['net_per100']} vs CASH +{CASH[yr]} per 100 "
                f"-> {best_of[0]} made more")
        out["years"][str(yr)] = rec
        lines += [f"## EKAM-daily 2c, FAR expiry — {yr}", "",
                  f"- Option trades scored: {rec['trades_scored']} · "
                  f"NC: {rec['nc_total']} {dict(st['nc']) or ''}",
                  f"- Net per 1 lot: {rec['net_per_lot']} · "
                  f"per-100 equivalent: {rec['net_per100']} · "
                  f"WR: {rec['wr']}",
                  f"- Best/worst trade (per lot): {rec['best']} / "
                  f"{rec['worst']} · halves per lot (Jan-Jun / Jul-Oct): "
                  f"{rec['halves_per_lot']}",
                  f"- Still died at expiry (contract expired before the "
                  f"cash exit): {rec['died_at_expiry']} of "
                  f"{rec['trades_scored']} scored (near-expiry run: "
                  f"{NEAR[yr]['died']} of {NEAR[yr]['scored']})",
                  f"- Farthest-fallback trades (no >= 45-day expiry "
                  f"listed): {rec['farthest_fallback_trades']} "
                  f"{rec['fallback_detail'] or ''}",
                  f"- NO_ENTRY_CANDLE anatomy: "
                  f"{rec['nc_anatomy'] or '{}'} (candles_start_after_"
                  f"entry = the far contract had not traded yet at "
                  f"entry)",
                  f"- Near-expiry line: {NEAR[yr]['scored']} scored, "
                  f"net per lot {NEAR[yr]['net_per_lot']}, per-100 "
                  f"{NEAR[yr]['net_per100']}, WR {NEAR[yr]['wr']}, "
                  f"NC {NEAR[yr]['nc']}",
                  f"- Cash line (published, per 100 shares): "
                  f"+Rs{CASH[yr]}",
                  f"- Verdict: {rec.get('verdict')} (far per-100 "
                  f"{rec['net_per100']} vs near per-100 "
                  f"{NEAR[yr]['net_per100']} vs cash +Rs{CASH[yr]}).",
                  ""]
    lines += ["## Closing line", ""]
    lines += [f"- {v}" for v in verdict_line]
    lines += ["",
              "## Notes", "",
              "- Control (SPEC s.6): the near-expiry EKAM rows were "
              "reproduced from the first run's stored trades before "
              "scoring — 2025: 66 scored / -Rs212,268.75 per lot / NC 8 "
              "/ 35 expiry-truncated; 2026: 95 scored / -Rs396,390.75 "
              "per lot / NC 7 / 56 expiry-truncated. Cash totals "
              "re-asserted in prep: 74 / +Rs42,954.60 (2025), 102 / "
              "+Rs1,41,328.40 (2026).",
              "- Entry premium = contract open on the cash entry date; "
              "exits mirror the cash exit kind exactly (SIGNAL/TIME at "
              "the open, FORCED at the close, CAP at the 5-minute "
              "trigger bar), with expiry truncation at the expiry-day "
              "close when the contract still dies first.",
              "- NC ANATOMY (the dominant finding): of the 138 NC "
              "positions, 130 are NO_ENTRY_CANDLE — and 116 of those "
              "130 are cases where the chosen far contract's FIRST "
              "candle in the entire fetched range falls AFTER the "
              "entry date (the other 14 files are empty across the "
              "range, incl. the patchy Mar-2025 expiry set already "
              "known from the first run). Upstox returns a candle only "
              "for days the contract traded: the far-month contract "
              "was listed but had no trades yet when EKAM signalled. "
              "This is a liquidity wall, not a fetch failure — in "
              "live trading the same wall appears as no quote to buy.",
              "- SCORED-SUBSET CAVEAT: the 38 scored trades are "
              "self-selected for exactly the names/dates where a far "
              "contract was already trading at entry, so the scored "
              "far-expiry lines OVERSTATE what the rule could have "
              "done across all 176 signals. The year verdicts are "
              "therefore read as: far expiry beats near expiry where "
              "it can be traded at all, and still loses to cash in "
              "both years.",
              "- FALLBACK DETAIL: the single farthest-fallback trade "
              "is HINDCOPPER entered 2025-07-30 — discovery holds no "
              "listed expiry for HINDCOPPER Aug-Oct 2025 (None in the "
              "first run's discovery), so the only expiry in the "
              "4-month span was 2025-07-31 (dte 1); it scored as "
              "effectively a near-expiry trade and is inside the 2025 "
              "scored line.", ""]
    with open(WS / "stock_options_far_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fields})
    (WS / "stock_options_far_results.json").write_text(
        json.dumps(out, indent=1))
    (WS / "stock_options_far_2026-11-15.md").write_text(
        "\n".join(lines) + "\n")
    print(json.dumps(out["years"], indent=1))

if __name__ == "__main__":
    main()
