# Stock Results-Reaction Profiles — Jan–Oct 2026 (25 watchlist stocks, equity cash)

**FROZEN SPEC below — written 2026-10-31 BEFORE any profile scoring or
tradability test. The P1/P2 rules in this section do not change after
results are seen.**
Paper only, real money ₹0, no orders. Equity cash intraday only,
LONG/SHORT language. Every strategy figure: provisional per 100
shares, ₹40/trade flat cost.

This build is the user's own 2026-10-29 design idea — per-stock
reaction profiles around results (how each stock behaved around its
last results: before, during, after) — never built until now.

## Data & window (frozen)

- Prices: `data/progressive/{SYM}/spot_5m.csv` + `spot_daily.csv`.
  Volume: `data/progressive_vol/{SYM}/spot_5m_vol.csv` (daily volume
  = sum of the day's 5-min bar volumes).
- Window: reaction days 2026-01-01 .. 2026-10-28. October = 1–28 Oct
  (18 trading days); 29 Oct is absent from the price cache and is
  never counted as a zero day.
- Events: `event_type = results` rows of
  `stock_event_calendar_jan_oct_2026.csv`. Reaction day **R** =
  the calendar `reaction_date` when announcement ≤ reaction_date ≤
  announcement + 7 days, otherwise the announcement date itself —
  the same rule the round-5 N4 engine used. **85 usable events**:
  10 stocks with 4 in-window results, 15 stocks with 3.
- Trading days are each stock's own trading days. "Prev close" =
  previous trading day's daily close.

## Profile measurements (frozen definitions, per event)

- **PRE-A (R-7..R-3, 5 days):** cum return % = close(R-3) /
  close(R-8) − 1; volume pace = Σ volume / (5 × baseline); up days =
  count of days closing above their own prev close. Baseline = mean
  daily volume over up to 20 trading days immediately before R-7
  (minimum 5 available days, else pace = NA; baseline day count is
  recorded per row).
- **PRE-B (R-2..R-1, 2 days):** cum return % = close(R-1) /
  close(R-3) − 1; pace = Σ volume / (2 × baseline before R-2);
  up days likewise.
- **PRE-ALL (R-7..R-1, 7 days):** cum return % = close(R-1) /
  close(R-8) − 1; pace = Σ volume / (7 × baseline before R-7).
- **REACTION day R:** gap % = open(R) / prev close − 1; move by
  09:30 = close of the 09:25 five-min bar / prev close − 1 (the N4
  convention); full-day return % = close(R) / prev close − 1;
  volume multiple = volume(R) / baseline before R.
- **POST (R+1..R+5):** follow-through return % = close(R+5) /
  close(R) − 1 (NA if fewer than 5 trading days follow R in the
  data). **CONTINUED** ⇔ post return has the same sign as the
  reaction full-day return AND |post| ≥ 0.5%. **FADED** ⇔ opposite
  sign AND |post| ≥ 0.5%. Otherwise **FLAT**.

## Tradability rules (frozen before scoring)

Common exit engine — identical to the round-5 N4 engine: the exit
scan starts on the bar AFTER the entry bar; within a bar the stop is
checked before the target; if neither level is touched, exit at the
close of the 15:10 bar. **T125** = target +1.25% / stop −0.5%;
**T10** = target +1.0% / stop −0.5% (mirrored for SHORT).
Net = sign × (exit − entry) × 100 shares − ₹40.
Halves: H1 = trade date ≤ 2026-05-31, H2 = trade date ≥ 2026-06-01.
P1 trade date = R; P2 trade date = R+1.

### P1 — the stock's own pre-window signature as a gate on N4

- **Accumulation** (knowable at the close of R-1): PRE-ALL cum
  return ≥ +1.5% AND PRE-ALL volume pace ≥ 1.1×.
  **Distribution:** PRE-ALL cum return ≤ −1.5% AND pace ≥ 1.1×.
- On R, compute the N4-V3 trigger: move by 09:30, |move| ≥ 1.0%.
  Trade ONLY if a signature held AND the trigger direction matches
  it (accumulation + up-trigger → LONG; distribution + down-trigger
  → SHORT). A signature contradicted by the reaction (e.g.
  accumulation into a ≥1% down-reaction) is NO trade.
- Entry = close of the 09:30 bar (recorded 09:35). Primary exit
  T125; T10 reported as the shadow column, as in the N4 line.
- **Ungated comparison:** ALL results-reaction N4 entries (trigger
  ≥ 1.0%, either direction, no signature requirement) — the round-5
  BASE pool. Anchor this build must reproduce: BASE T125 Jan–Oct
  net **+₹2,924.79** provisional per 100 shares (round 5).
- The gate-DROPPED subset (ungated entries the gate rejects) is
  also reported, so the gate's full effect is visible.

### P2 — post-reaction follow-through, gated by the stock's own past

- **Candidate:** a results event whose |reaction full-day return|
  ≥ 2% and whose R+1 exists in the data.
- **Gate (leave-one-out, knowable at the R+1 open):** among THIS
  stock's EARLIER usable events (strictly earlier reaction day,
  with a computable POST window), at least 2 events CONTINUED
  under the frozen definition above. A stock's first and second
  in-window events can never pass — by construction, not by result.
- Entry = open of R+1 (the 09:15 bar's open), direction = sign of
  the reaction-day return. Primary exit T125, T10 secondary.
- **Ungated comparison:** all candidates, no profile gate.

## Honesty clauses (frozen)

- 3–4 events per stock is a small sample. The profiles DESCRIBE
  what happened around those events; they are not laws about the
  stock, and no profile sentence below claims more than its event
  count supports.
- The P1 thresholds (+1.5%, 1.1×) and P2 thresholds (≥2%, ≥2
  earlier continuations) are frozen above, before scoring, and are
  not re-tuned anywhere in this build.
- Anything positive here is in-sample. It adopts nothing; at most
  it earns a frozen paper spec for a fresh window, judged there.

---

# RESULTS — scored 2026-10-31, after the freeze above

**Engine validation:** the ungated P1 pool reproduces the round-5
BASE anchor EXACTLY — 52 trades, T125 net **+₹2,924.79** provisional
per 100 shares — so the exit engine and reaction-day rule are the
same machinery N4-V3 was scored with. All figures below: provisional
per 100 shares, ₹40/trade, paper only, real money ₹0.

**Universe:** 85 results events profiled (all 85 usable; post-window
classifiable for 79). Follow-through across all stocks: **38
CONTINUED / 32 FADED / 9 FLAT** — continuation is a slight majority,
not a law. Median |reaction-day move| = 2.53%.

## P1 — pre-window signature gate on N4 reaction entries: FAILS

Signatures were rare: of 85 events, only **12 accumulation** and
**6 distribution** under the frozen thresholds; the other 67 events
had no signature. Only 6 of the 18 signature events also produced a
matching ≥1% 09:30 trigger.

| P1 (T125 primary) | Trades | Win% | Net ₹ | H1 ₹ | H2 ₹ | Expectancy ₹/trade | Breadth (net+ stocks) |
|---|---|---|---|---|---|---|---|
| Gated | 6 | 50.0 | +1,446.99 | +2,110.78 | **−663.79** | +241.17 | 3/6 |
| Ungated (N4 BASE) | 52 | 36.5 | +2,924.79 | +2,727.65 | +197.14 | +56.25 | 11/25 |
| Gate-DROPPED | 46 | 34.8 | +1,477.80 | +616.87 | +860.93 | +32.13 | 9/23 |

(T10 shadow tells the same story: gated +₹803.53 with H2 −₹765.25.)

**Verdict:** the gate concentrates expectancy (₹241 vs ₹56 per
trade) but on only 6 trades, its second half is negative, and the
trades it DROPS are themselves both-halves positive (+₹1,477.80).
A gate that rejects a profitable pool and keeps a half-negative one
has not separated anything. **P1 does not pass.** The signature is
real information about the pre-window; it is not, at these frozen
thresholds, a trade filter.

## P2 — post-reaction follow-through

### P2 gated (leave-one-out profile gate): UNTESTABLE — the gate starves itself

Only 10 of 85 events had ≥2 earlier continuations available at all,
and only **3 trades** passed the gate with a ≥2% reaction: net
**+₹80.17** at T125 (−₹49.22 at T10), all in H2, 1 of 3 stocks
net-positive. Three trades is not a test. **No verdict either way**
— the per-stock track record inside a 10-month window is simply too
short to gate on, which is itself a finding about this design: a
leave-one-out profile gate needs more history per stock than
Jan–Oct holds.

### P2 UNGATED (all |reaction| ≥ 2% events, enter R+1 open, follow the reaction): BOTH HALVES POSITIVE

| P2 ungated | Trades | Win% | Net ₹ | H1 ₹ (trades) | H2 ₹ (trades) | Expectancy ₹/trade | Gross expectancy ₹/trade | Breadth |
|---|---|---|---|---|---|---|---|---|
| **T125 (primary)** | 48 | 45.8 | **+12,835.88** | +3,498.10 (29) | +9,337.78 (19) | +267.41 | +307.41 | 14/25 stocks net+ |
| T10 (secondary) | 48 | 47.9 | **+9,301.03** | +2,507.00 | +6,794.03 | +193.77 | +233.77 | 14/25 |

Mandatory disclosures, all part of the verdict:

- **It is a SHORT-side result.** SHORTs net **+₹13,109.45**; LONGs
  net **−₹273.57**. In this window, "follow-through" mostly means
  *stocks that fell hard on results kept falling the next day*.
  Splitting the rule by direction now would be hindsight fitting,
  so the frozen rule stands as-is — but nobody should read this as
  a two-sided edge.
- **The money is concentrated even though the count is broad.**
  14 of 25 stocks are net-positive, but the top payers dominate:
  GLENMARK +₹5,112.24, OBEROIRLTY +₹3,916.62, BDL +₹3,177.75,
  TVSMOTOR +₹2,972.00, GODREJCP +₹2,143.82 — the same
  high-reaction, continuation-profile stocks named in the profiles
  below. Worst: HINDUNILVR −₹3,484.80, ASTRAL −₹1,592.10 (ASTRAL
  is a documented FADE stock — the ungated rule walks into it).
- **One data artefact sits inside the candidate set:** VEDL's
  2026-04-30 "reaction" of −64.77% is the demerger price
  adjustment, not a results reaction. Its follow-through trade
  (2026-05-04 SHORT) lost −₹178.50, so the artefact slightly
  HURTS the total; excluding it, T125 net = +₹13,014.38. The
  verdict does not depend on it either way.
- **This is in-sample, and it is NOT N4's V4.** Round 5's V4
  (day+1 follow-through of 09:30-triggered N4 entries, entered at
  the next day's 09:35) lost. P2-ungated differs in the trigger
  (full-day reaction ≥ 2%, no intraday trigger), the entry (R+1
  open) and the population (52 candidates vs V4's
  trigger-confirmed subset). The two results do not contradict
  each other; they test different rules.
- Per the frozen honesty clause: **this adopts nothing.** P2
  ungated is the strongest per-trade expectancy yet found on the
  event axis (+₹267.41/trade vs N4-V3's +₹142.69) and the only
  event-axis variant besides N4 itself that is both-halves
  positive at both exits — it earns, at most, a frozen paper spec
  for a FRESH window, judged there. November is already spoken for
  (N4-V3 primary); whether P2-ungated gets a December paper slot
  is a decision for the main thread, flagged in the delivery
  summary, not silently scheduled here.

---

# PER-STOCK PROFILES — how each stock behaved around its results, Jan–Oct 2026

Reading guide: "pre" = median cumulative return over R-7..R-1 with
median volume pace (1.0× = normal); "reaction" = median reaction-day
return and average |reaction|; "post" = CONTINUED/FADED/FLAT counts
over R+1..R+5. Event counts are small (3–4) — these are
descriptions of what happened, not laws.

- **OBEROIRLTY (4 events) — the clearest signature on the board.**
  Drifts down into results (pre median −1.27%), falls on EVERY
  reaction day (4/4 negative, median −2.92%, avg |move| 3.53%),
  and keeps falling after (4 CONTINUED / 0 FADED). In this window:
  results = down, and down continues.
- **BDL (3) — buy the rumour, sell the news, keep selling.** Runs
  up hard into results (pre median +5.74%), falls on all 3 reaction
  days (median −5.27%, avg |move| 5.64%, reaction volume 3.68×),
  and all 3 post-windows CONTINUED down.
- **GODREJCP (3) — heavy reactions, mostly down, mostly
  continuing.** All 3 reactions negative (median −5.21%), reaction
  volume the highest median multiple among the quiet stocks
  (5.05×); 2 CONTINUED / 1 FLAT.
- **ASTRAL (3) — the fade stock.** Big reactions (avg |move|
  5.70%, reaction volume 3.99×) that reversed every time:
  0 CONTINUED / 3 FADED. Whatever results day does, the next five
  days undid it.
- **HINDCOPPER (3) — accumulation that didn't pay.** The strongest
  pre-window accumulation signature measured (pace median 2.02×,
  pre median +3.69%, 2 frozen-signature accumulation events) — yet
  reactions were mixed and all 3 post-windows FADED. Pre-results
  buying was not rewarded in this window.
- **WIPRO (4) — up into results, down on the day, keeps drifting
  down.** Pre median +4.51%; reactions mostly negative (median
  −1.90%, 1/4 positive, reaction volume 3.5×); 3 CONTINUED /
  1 FLAT.
- **HDFCBANK (4) — small, negative, persistent.** All 4 reactions
  negative but modest (median −1.46%); 3 CONTINUED / 1 FLAT. A
  grind, not a shock.
- **KALYANKJIL (3) — violent and unreliable.** Avg |reaction|
  9.14% on 6.26× median reaction volume, but follow-through
  1 CONTINUED / 2 FADED. Size without direction persistence.
- **VEDL (4) — read with care: one artefact.** The −64.77%
  "reaction" on 2026-04-30 is the demerger price adjustment, not
  a results move, and it distorts every VEDL average. The genuine
  reactions: −11.41% (Jan, CONTINUED down), +0.47% (Jul),
  +3.30% (Oct, no post data).
- **GLENMARK (3) — down on results, unclear after.** All 3
  reactions negative (median −3.88%); post split 1/1/1.
- **TVSMOTOR (4) — split personality.** Reactions split (median
  +0.78%, avg |move| 2.67%); of 3 classifiable posts, 2 CONTINUED /
  1 FADED. Its P2 trades were the single biggest winner
  (+₹4,844.50, Jul LONG) and a large loser (−₹1,872.50, Jan
  SHORT) — high variance, no clean tendency.
- **NATIONALUM (3) — up-leaning reactions.** Median reaction
  +3.60% (2/3 positive, avg |move| 5.54%); posts split 1/1/1.
- **OIL (3) — up-leaning and continuing.** Median reaction +2.30%
  (2/3 positive); 2 CONTINUED / 1 FADED.
- **UNITDSPR (4) — falls into results, rises on them.** Pre median
  −2.92%; reactions 3/4 positive; posts 2 CONTINUED / 1 FADED
  (Oct event has no post data).
- **HINDUNILVR (4) — down into results, nothing after.** Pre
  median −3.51% (the weakest pre-window on the board); reactions
  split; 0 CONTINUED / 2 FADED / 1 FLAT. Also the worst P2-ungated
  payer (−₹3,484.80).
- **HINDZINC (4) — muted reactions, gentle continuation.**
  Median reaction −0.06% (avg |move| 1.83%); 3 CONTINUED / 1 FADED
  on small moves.
- **NHPC (3) — quiet, slightly up.** Median reaction +1.07%;
  2 CONTINUED / 1 FADED.
- **NTPC (3) — the quietest.** Avg |reaction| 1.66%; 0 CONTINUED /
  2 FADED / 1 FLAT. Results barely move it, and what move there is
  fades.
- **ITC (3) — small and fading.** Median reaction +1.10%;
  1 CONTINUED / 2 FADED.
- **IRCTC (3) — small, negative, fading.** All reactions negative
  (median −1.13%); 1 CONTINUED / 2 FADED.
- **INDUSTOWER (4) — negative-leaning, fading.** Median reaction
  −1.92%; 1 CONTINUED / 2 FADED (1 unclassifiable post).
- **HINDALCO (3) — results are a non-event.** Avg |reaction| just
  1.43%; 1 CONTINUED / 2 FADED.
- **PFC (3) — busy tape, no tendency.** Pre-window volume pace
  median 1.26× (elevated, with HINDCOPPER the highest); reactions
  and posts split every way (1/2 post split). No profile to trade.
- **RECLTD (4) — negative-leaning, mixed after.** Median reaction
  −3.01%; posts 1 CONTINUED / 1 FADED / 1 FLAT.
- **TATASTEEL (3) — no pattern.** Reactions split (median +1.60%);
  posts 1/1/1. Three events, three different stories.

**Cross-stock summary:** continuation beat fading only modestly
overall (38 vs 32 of 79), but it is concentrated: the stocks whose
reactions are LARGE and one-directional (OBEROIRLTY, BDL, GODREJCP
down; WIPRO down-after-run-up) continued, while the fade tendency
lives in ASTRAL, HINDCOPPER, HINDUNILVR, NTPC. The pre-window
accumulation signature, by itself, did NOT predict a good reaction
(P1 failed; HINDCOPPER is the cautionary example).

## Files from this build

- This report (frozen spec + results + profiles):
  `stock_reaction_profiles.md`
- Per-event rows (85): `stock_reaction_profiles_events.csv`
- Per-stock summary: `stock_reaction_profiles_summary.csv`
- Trades: `stock_profiles_P1_{gated,ungated,dropped}_{T125,T10}_trades.csv`,
  `stock_profiles_P2_{gated,ungated}_{T125,T10}_trades.csv`
- Engine: `stocks_reaction_profiles.py`; raw results:
  `stock_reaction_profiles_results.json`,
  `stock_reaction_profiles_rows.json`
