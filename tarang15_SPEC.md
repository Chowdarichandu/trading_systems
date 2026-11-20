# TARANG Design 15 — Frozen Spec (pre-registered)

**Pre-registered:** 2026-11-17 (IST), before any Design 15
scoring. No Design 15 result exists at the time of writing; no
parameter below has been tuned against any Design 15 result.

**Programme note (owner's standing mandate):** the TARANG
programme CONTINUES — designs iterate from diagnosis until a
gate pass or the owner's stop. Design 15 is the direct
continuation of Design 14, seeded by Design 14's own diagnosis
(`tarang14_2026-11-17.md` Sections 2 and 7):

> *The drift is the largest per-trade engine this programme has
> ever isolated (+₹450.60 net per surviving trade in 2025,
> +₹543.17 in 2026, at full count) — and it cannot be harvested
> raw. The raw excursion stream fails on its own gross
> (negative in 2025), and its stop tail (~39% of entries first
> travel a full −1% against the entry: 1,820 stops,
> −₹15,51,655.70) exceeds the entire square-off engine
> (+₹13,89,925.00). The reversion books' residue was profitable
> because their FILTER — re-cross, rising histogram, freshness,
> quiet selection — had already removed the excursions whose
> aftermath is violent against an entry. Design 15: (i) keep
> the continuation direction and the drift exits (no target —
> closed by Design 14's measurement), but restore a filter in
> front of the entry: the excursion must SURVIVE a short window
> before the with-direction entry is taken; (ii) attack the
> stop tail on the exit side: a disaster stop scaled to the
> excursion's own follow-through range, or a time-stop.*

Design 15 therefore trades **filtered continuation**: the same
Bollinger excursions as Design 14, in the excursion's own
direction, held toward the close — but an excursion only
becomes an entry if it **survives**: price holds outside the
band for the three bars after the excursion bar. The
pre-registered question: **does the survival filter keep the
drift (+₹451/+₹543 per square-off trade) and cut the stop
tail (1,820 stops / −₹15,51,656 in Design 14)?**

**Basis (labelled everywhere):** equity cash only,
PROVISIONAL per 100 shares, ₹40 per completed trade. Paper
only, real money ₹0. No stock options (closed surface).
Nothing is armed; no paper run is started; no live book is
touched.

## 1. Universe and data (unchanged from Designs 6–14)

- Universe: the SAME 127 verified names of Round 6 — liquid +
  Nifty 100 / Nifty Midcap 150 member + F&O segment + ₹2,000
  cap at selection, verification-passed (`tarang6_verify.json`).
- Data: `data/tarang_vol/<SYM>/spot_5m_vol.csv` for the 21
  qualifying incumbents, `data/tarang_wide_vol/<SYM>/spot_5m_vol.csv`
  for the rest — the Round 6 verified volume-bearing stores,
  2025-01-01 → 2026-11-13. No new fetch.
- Indicators: Design 7's frames, imported unchanged
  (`tarang7_score.load_data7` / `add_bb_macd`) — Bollinger
  (20, 2) with POPULATION sd on the continuous 5-minute close
  series, MACD (12, 26, 9) with the family's SMA-seeded EMAs.
  Design 15 reads the bands only; the MACD frame is carried
  for the shared data path and the truncation spot-check.
- Window: entries 2025-01-01 → 2026-11-13; 2025, 2026 and the
  November 2026 slice reported separately, never pooled into
  one verdict.

## 2. The signal — excursion + survival filter

- A bar is **beyond-high** if close > upper band, **beyond-low**
  if close < lower band, **inside** if lower ≤ close ≤ upper;
  a bar with undefined bands is inert (and breaks a run, as in
  the family's state machine). An **excursion** is a maximal
  run of consecutive same-side beyond closes within a session;
  its first bar is the **excursion bar** `a` — identically
  defined to Design 14's signal bar (and the reversion family's
  snap bar).
- **Survival:** the setup lives only if price HOLDS outside
  the band — each of the next three bars (`a+1`, `a+2`, `a+3`,
  same session) closes beyond the band **on the same side**
  (against that bar's own bands). A close back inside the band
  (or beyond the opposite band, or an undefined-band bar, or a
  session break) within those three bars **kills the setup** —
  it was a reversion candidate, not a continuation.
- **Entry:** at the open of the **4th bar after the excursion
  bar** (`a+4`), same session, in the excursion's direction
  (beyond-high → **LONG** +1; beyond-low → **SHORT** −1). A
  setup whose `a+4` bar falls in another session, or whose
  entry time is outside **[09:45, 14:30]**, is skipped, never
  deferred (a setup completing after 14:30 is skipped).
- **Allocation fields (from the excursion bar, as Design 14):**
  **depth** = the excursion close's penetration beyond the
  band in % of the excursion close; **vol_ratio** = volume at
  the excursion bar ÷ mean volume of the 20 bars ending at the
  excursion bar (0 if that mean is 0).
- **Excursion range (the stop ruler):** `exc_range` = the
  excursion bar's own range, high − low, in price points,
  recorded at the signal and carried into the exits and the
  audit.

## 3. Allocation — A4 volume-priority (unchanged from Design 14)

Candidate entries are processed in (date, entry_time,
vol_ratio DESCENDING, depth descending, signal_time, symbol)
order — A4's ranking, exactly as in Designs 4–8 and 14. Caps:
one open position per name (occupancy to the exit bar);
max 2 entries per name per day; max 10 entries per book per
day; re-entry after an exit allowed.

## 4. Exits — drift exits, range-scaled stop, optional time-stop

Evaluated on the trade's OWN day's bars (the Round 4 corrected
indexing), scanning from the entry bar to the square-off bar
inclusive. There is **no target** (closed for drift books by
Design 14's measurement).

- **Disaster stop (both books), RANGE-SCALED:** distance
  `dist = 1.5 × exc_range` (the excursion bar's range, Section
  2), measured from the entry price — LONG stop = entry −
  dist; SHORT stop = entry + dist. The stop fills AT its level
  price on the first bar whose range touches it.
- **TARANG-T15-A:** disaster stop, else the position rides to
  the **15:15 square-off bar's close**.
- **TARANG-T15-B:** T15-A plus a **TIME-STOP**: at the close
  of the first bar whose end is at or after entry + 60 minutes
  (the *check bar*), if the position is not positive at that
  close (side × (close − entry) ≤ 0), it exits at the **next
  bar's open** (reason `timestop`). The check is made once,
  only if the check bar precedes the square-off bar; the
  disaster stop remains the backstop and is evaluated first
  on every bar up to and including the check bar (stop-first
  convention). If the next bar is beyond the square-off bar,
  the position squares off instead.
- Net = side × (exit − entry) × 100 − ₹40. Exit reasons:
  `stop`, `timestop` (T15-B only), `squareoff`.

## 5. Controls gate (identical stack, unmoved)

Per `tarang_SPEC.md` Sections 9–10, the Round 4/5/6/7/8 audit
stack, and `~/workspace/custom-skills/backtest_controls_gate/SKILL.md`,
run in the same run, before any verdict:

1. **Pre-scoring controls:** (a) machinery integrity —
   Design 12's generator and validator at the base
   configuration (W = 10, no second bar), imported unchanged,
   must reproduce Design 8's engine AND validator signal sets
   EXACTLY on all 127 names (147,718 signals), as in Designs
   12–14; (b) **Design 15 parity** — the Design 15 engine
   generator (per-day loop) and the independently written
   vectorised validator must agree EXACTLY on every name
   (surviving-setup set, excursion index, entry index, depth,
   vol_ratio, exc_range). Any failure aborts the run.
2. **Timing/leak audit (per book):** every trade checked —
   entry after signal; entry exactly at excursion + 4 bars;
   fill inside [09:45, 14:30]; survival independently
   recomputed from the validator and matched; exc_range
   recomputed and matched; exit re-simulated bar-by-bar on
   the trade's own day by the independent bar-loop exit of
   Section 4 and matched (bar, price, reason); square-off
   price equal to its own day's square-off-bar close (the
   regression check that exposed the Rounds 1–3 defect); net
   recomputed; caps (≤2/name/day, ≤10/day); no overlapping
   positions per name; each trade's vol_ratio / depth
   recomputed independently and matched; and the whole book
   rebuilt by an independently written allocator (validator
   signals + A4 ranking + bar-loop exits) and matched
   trade-for-trade. Plus a truncation spot-check: Bollinger
   bands and MACD histogram recomputed from bars cut at the
   signal bar must match the engine at that bar. Violations
   must be 0.
3. **Random-entry placebo (200 seeded draws, seed base
   20261118 — the family base):** same names, same days, same
   number of entries per day as the book took, random eligible
   bars 09:45–14:45 (the family's placebo window), random
   side, identical caps — and **the book's OWN exit geometry**
   (Section 4). Stated openly: a random entry has no excursion
   bar, so its range-scaled stop uses **the entry bar's own
   range × 1.5** — the only causal analogue of the excursion
   ruler; the T15-B time-stop applies identically. The book
   must beat the placebo 90th percentile in both years.
4. **Placebo percentile reporting:** the book's percentile
   within its own 200-draw distribution, per year.
5. **Direction-flip placebo (information only):** the book's
   exact entries with the side flipped, under the book's own
   exits (same excursion-ranged stop, same time-stop rule).
6. **Splits and stress:** as listed in Section 6;
   independent re-sum of headline nets from the written
   trades CSV.

## 6. Reporting (binding)

Per book (TARANG-T15-A, TARANG-T15-B): the full gate table
(Section 7); placebo percentiles; side splits (LONG vs SHORT
nets per year); win rate; trade count; halves; full month
table; ex-top-3 per year; max drawdown (overall and per
year); top-10 contributors per year; the **resolution mix**
— stop / timestop / square-off counts, nets and shares of
all trades, per year; the **stop-tail anatomy against
Design 14**: stops count and net (overall and per year) vs
Design 14's 1,820 stops / −₹15,51,655.70, and square-off net
and net-per-square-off-trade per year vs Design 14's
+₹6,90,326.00 / +₹450.60 (2025) and +₹6,99,599.00 / +₹543.17
(2026) — **did the filter keep the drift and cut the tail,
stated plainly**; the November 2026 slice with its trade
count; monthly pace vs the ₹15,000/month stocks floor
(information); and the **cost anatomy** — trades, gross,
levy, gross per trade, net per trade, per year.

## 7. Pass bar (pre-registered, frozen)

A Design 15 book PASSES only if ALL hold:

- Net positive in **both** 2025 and 2026;
- Beats its own random-entry placebo 90th percentile in
  **both** years;
- Ex-top-3 positive in **both** years;
- No month worse than −₹15,000;
- Timing audit clean (0 violations, spot-check included);
- November 2026 slice not worse than −₹3,000.

## 8. Discipline

- The ONLY new variables are the survival filter (Section 2)
  and the exit-side stop ruler (range-scaled disaster stop;
  T15-B's time-stop) — each named in Design 14's seed.
  Direction (continuation), the no-target drift hold, A4
  allocation, Bollinger (20, 2), the excursion definition,
  the [09:45, 14:30] entry window, the name and day caps,
  universe and window are frozen. Nothing is scanned.
- A PASS makes the book a forward-paper CANDIDATE for the
  owner's decision; nothing is armed or started by this run
  either way.
- Whatever the verdict, the report closes with the diagnosis
  that seeds Design 16, in two lines.
