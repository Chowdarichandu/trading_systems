#!/usr/bin/env python3
"""Historical proof stage 4: charts + per-index reports + status appends."""
import json, csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date

TR = Path.home() / "workspace/trading"
OUT = TR / "historical_proof_data"
stats = json.loads((OUT / "stats.json").read_text())
TRADING_DAYS = 203

OLD = {"BANKNIFTY": {"mixed": 124415.0, "jansep_spot": 110495.0, "oct_premium": 13920.0,
                     "label": "U1-B2", "fname": "index_options_U1_B2_bank_trades.csv"},
       "NIFTY": {"mixed": 168140.25, "jansep_spot": 157365.0, "oct_premium": 10775.25,
                 "label": "U1-N1", "fname": "index_options_U1_N1_nifty_trades.csv"}}
MN = {"01":"Jan","02":"Feb","03":"Mar","04":"Apr","05":"May","06":"Jun","07":"Jul","08":"Aug","09":"Sep","10":"Oct"}

def dd_window(curve):
    peak, peakd, maxdd, troughd = 0.0, curve[0][0], 0.0, curve[0][0]
    for d, c in curve:
        if c > peak: peak, peakd = c, d
        if peak - c > maxdd: maxdd, troughd, pd_ = peak - c, d, peakd
    return maxdd

for sym, cfg in OLD.items():
    s = stats[sym]
    rows = list(csv.DictReader(open(TR / ("historical_proof_bank_B2_trades.csv" if sym == "BANKNIFTY" else "historical_proof_nifty_N1_trades.csv"))))
    curve = [(date.fromisoformat(d), float(c)) for d, c in s["curve"]]
    # chart
    fig, ax = plt.subplots(figsize=(10, 4.2))
    xs = [c[0] for c in curve]; ys = [c[1] for c in curve]
    ax.plot(xs, ys, color="#1f6f43" if sym == "BANKNIFTY" else "#2456a6", lw=1.6)
    ax.fill_between(xs, ys, 0, where=[y >= 0 for y in ys], color="green", alpha=0.08)
    ax.fill_between(xs, ys, 0, where=[y < 0 for y in ys], color="red", alpha=0.12)
    ax.axhline(0, color="black", lw=0.8)
    ax.set_title(f"{'Bank Nifty' if sym=='BANKNIFTY' else 'Nifty'} — {cfg['label']} cumulative net, PREMIUMS ONLY, per 1 lot, Jan–Oct 2026 (paper)")
    ax.set_ylabel("Cumulative net (Rs)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.grid(alpha=0.25)
    fig.tight_layout()
    chart = f"historical_proof_{'bank_B2' if sym=='BANKNIFTY' else 'nifty_N1'}_chart.png"
    fig.savefig(TR / chart, dpi=130); plt.close(fig)

    comp = s["computed"]; total = s["total"]
    ft_pct = round(100.0 * s["targets"] / comp, 1)
    per_week = round(comp / TRADING_DAYS * 5, 2)
    jansep_prem = round(total - cfg["oct_premium"], 2)
    best = max(s["months"], key=lambda m: m["net"]); worst = min(s["months"], key=lambda m: m["net"])
    best_share = round(100.0 * best["net"] / total, 1) if total > 0 else 0.0
    red_months = [m for m in s["months"] if not m["cum_green"]]
    mlines = []
    for m in s["months"]:
        mark = "✅ green" if m["cum_green"] else "🔴 RED"
        mlines.append(f"| {MN[m['month'][5:7]]} 2026 | {m['trades']} | {m['targets']} | {m['stops']} | {m['square_offs']} | {m['full_target_pct']}% | ₹{m['net']:,.2f} | ₹{m['cumulative']:,.2f} | {mark} |")
    dis_lines = []
    for d in s["disagreements"][:6]:
        dis_lines.append(f"- **{d['date']} {d['direction']} ({d['rep']})**: spot provisional ₹{d['old_spot_net']:,.2f} → premium ₹{d['premium_net']:,.2f} (premium exit: {d['premium_exit']}; swing ₹{d['swing']:,.2f})")
    n_dis = len(s["disagreements"])
    jansep_n = comp - (9 if sym == "BANKNIFTY" else 8)
    if sym == "BANKNIFTY":
        verdict_extra = (f"January closes RED (cumulative −₹1,920.00) — the mixed-basis claim of a green close at every "
                         f"month-end does **not** survive on premiums. February recovers it and every later month-end is green. "
                         f"The drawdown is the story: after peaking at ₹32,497.00 at May month-end, the curve fell for four "
                         f"straight months (Jun–Sep all negative months) before October's +₹13,920.00.")
    else:
        verdict_extra = (f"Every month-end closes green cumulatively — that part of the mixed-basis story survives. "
                         f"But the cushion is thin: after May's −₹15,190.00 month the cumulative halved, and the curve's "
                         f"max drawdown of ₹28,231.50 is larger than the entire final total of ₹25,159.00. Hit quality is "
                         f"the weakness: only 25.9% of legs reached the +90 premium target and 42 of 108 legs ended as "
                         f"square-offs — spot moves that the premium never converted into a target.")
    report = f"""# Historical proof — {'Bank Nifty' if sym=='BANKNIFTY' else 'Nifty'} — {cfg['label']} — PREMIUMS ONLY, Jan–Oct 2026

**Real money: ₹0 — paper proof only. No live trades were placed.**

This file covers **{'Bank Nifty' if sym=='BANKNIFTY' else 'Nifty'} only**, in its own channel. It is not pooled with the other index and no combined verdict is made.

![Cumulative equity curve — {'Bank Nifty' if sym=='BANKNIFTY' else 'Nifty'} {cfg['label']}, premiums only](sandbox://workspace/trading/{chart})

## What was done

Every Jan–Sep 2026 leg of the frozen {cfg['label']} (which had only been scored as spot provisional: spot points × 100 shares − ₹40) was re-scored on its **actual option premium candles** fetched from Upstox expired-instruments data (script-token browser-fetch route; the Muse connector was not used). October legs were already premium-scored in the frozen run and are carried in unchanged — the scoring code was re-validated against them and reproduces them exactly (e.g. {'Bank 1 Oct 54900 CE target +₹2,480.00; Bank 13 Oct PE target +₹2,480.00' if sym=='BANKNIFTY' else 'Nifty 8 Oct 22500 PE target +₹5,630.00; Nifty 23 Oct 22500 PE square-off −₹1,334.75'}).

- Scoring (identical to the October overlay): entry premium = open of the 5-min option candle at the leg's entry bar; stop = entry − 50 premium points, checked **before** target = entry + 90 on every bar including the entry bar; square-off at the 15:10 bar close; cost ₹220/trade; net per 1 lot = (exit − entry) × lot − ₹220.
- Strike: ATM nearest 100 to spot at the entry bar (spot from the leg file, or from cached 5-min spot candles at the entry bar where the leg file carried no spot value — source noted per leg in the working file).
- Expiry: the monthly expiry applicable to the trade date — the first monthly expiry on or after the trade date. Monthly expiries in 2026 (both indices, verified from expired-contract data): 27 Jan, 24 Feb, 30 Mar, 28 Apr, 26 May, 30 Jun, 28 Jul, 25 Aug, 29 Sep, 27 Oct. The expiry used is stated per trade in the trades CSV.
- **Lot size, verified from the contract data for every monthly expiry Jan–Oct 2026: {'Bank Nifty 30' if sym=='BANKNIFTY' else 'Nifty 65'} — constant all year.** Not assumed from October; each month's contracts were read and all show the same lot size.
- Completeness: **{comp} of {comp + s['not_computed']} legs COMPUTED, {s['not_computed']} NOT_COMPUTED.** Every Jan–Sep premium candle fetch returned data; no leg was substituted with spot points and nothing was invented.

## Month by month — premiums only, per 1 lot

| Month | Trades | Targets | Stops | Square-offs | Full-target % | Net (₹) | Month-end cumulative (₹) | Month-end |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(mlines)}
| **Jan–Oct total** | **{comp}** | **{s['targets']}** | **{s['stops']}** | **{s['square_offs']}** | **{ft_pct}%** | **₹{total:,.2f}** | — | — |

- **Jan–Oct premium-only total ({'Bank Nifty' if sym=='BANKNIFTY' else 'Nifty'} alone): ₹{total:,.2f} per 1 lot**
- Trades/week: **{per_week}** ({comp} trades over {TRADING_DAYS} trading days)
- Full-target %: **{ft_pct}%**

## Old mixed basis vs new premium-only basis

| Basis | Jan–Sep | October | Jan–Oct |
|---|---|---|---|
| Old (spot provisional Jan–Sep + premiums Oct, "mixed") | ₹{cfg['jansep_spot']:,.2f} (spot points × 100 shares − ₹40 — not an options profit) | ₹{cfg['oct_premium']:,.2f} (premiums) | ₹{cfg['mixed']:,.2f} |
| **New (premiums only)** | **₹{jansep_prem:,.2f}** | **₹{cfg['oct_premium']:,.2f}** | **₹{total:,.2f}** |

The premium-only Jan–Oct total is **₹{cfg['mixed'] - total:,.2f} lower** than the mixed figure. October does not change at all — the entire difference is Jan–Sep, where the spot-provisional unit (spot points × 100 shares) systematically overstated what the option premium actually did: spot moves of +150 to +230 points that scored as ₹15,000–₹23,000 spot "wins" were often only worth a premium stop or a small square-off, because the premium does not move 1:1 with spot and decays while the spot move develops. **{n_dis} of the {jansep_n} Jan–Sep legs change sign** between the two bases. Biggest disagreements:

{chr(10).join(dis_lines)}

## Honest verdict — {'Bank Nifty' if sym=='BANKNIFTY' else 'Nifty'} alone

- Ends positive on premiums alone: **YES — ₹{total:,.2f} per 1 lot over Jan–Oct 2026.** The system is not a fiction; the premium history is green.
- But it is **far smaller** than the mixed-basis ₹{cfg['mixed']:,.2f} suggested — the mixed figure must not be quoted as this system's premium performance again.
- Every month-end green cumulatively: **{'NO' if red_months else 'YES'}** — {('red closes: ' + ', '.join(MN[m['month'][5:7]] for m in red_months) + '.') if red_months else 'all ten month-ends close green.'}
- Worst month: **{MN[worst['month'][5:7]]} 2026, ₹{worst['net']:,.2f}**.
- Max drawdown of the cumulative premium curve (trade by trade): **₹{s['max_drawdown']:,.2f}**.
- Best month: {MN[best['month'][5:7]]} 2026, ₹{best['net']:,.2f} — **{best_share}% of the entire Jan–Oct premium total** comes from that single month.
- {verdict_extra}
- Nothing was re-tuned in this task. {cfg['label']} remains a frozen candidate; November 2026 paper (from Mon 2026-11-02, this index's own log) is still the validation step, and it should be judged against these premium-only numbers, not the mixed ones.

Trade-by-trade detail: `{'historical_proof_bank_B2_trades.csv' if sym=='BANKNIFTY' else 'historical_proof_nifty_N1_trades.csv'}` (entry/exit premium, exit reason, net per leg; October legs flagged in the note column).
"""
    name = "historical_proof_bank_B2.md" if sym == "BANKNIFTY" else "historical_proof_nifty_N1.md"
    (TR / name).write_text(report)
    print("wrote", name, "total", total, "ft", ft_pct, "best share", best_share)

    # status append
    status_file = TR / ("index_channel_bank_status.md" if sym == "BANKNIFTY" else "index_channel_nifty_status.md")
    para = (f"\n\n## Historical proof (premiums only) — appended 2026-10-30\n\n"
            f"**Real money: ₹0 — paper proof only.** Every Jan–Sep leg of frozen {cfg['label']} was re-scored on actual "
            f"Upstox option premium candles (same −50/+90 overlay, ₹220 cost, lot {'30' if sym=='BANKNIFTY' else '65'} verified "
            f"constant Jan–Oct 2026 from contract data); October legs carried in unchanged. All {comp} legs computed, "
            f"{s['not_computed']} NOT_COMPUTED. Premium-only Jan–Oct total for this index alone: **₹{total:,.2f} per 1 lot** "
            f"({per_week} trades/week, {ft_pct}% full-target) — versus the old mixed-basis ₹{cfg['mixed']:,.2f}, which must no "
            f"longer be quoted as premium performance. Month-end cumulative closes: "
            f"{'January closes RED (−₹1,920.00); all other month-ends green.' if red_months else 'green at all ten month-ends.'} "
            f"Worst month {MN[worst['month'][5:7]]} 2026 (₹{worst['net']:,.2f}); max drawdown ₹{s['max_drawdown']:,.2f}; best month "
            f"{MN[best['month'][5:7]]} 2026 (₹{best['net']:,.2f}) is {best_share}% of the total. Nothing re-tuned; {cfg['label']} stays "
            f"frozen for November paper in this channel's own log. Full proof: `{name}`; chart: `{chart}`.\n")
    with open(status_file, "a") as f: f.write(para)
    print("appended", status_file.name)
print("done")
