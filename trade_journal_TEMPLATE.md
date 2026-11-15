# Trade Journal — entry template (November 2026 paper)

One entry per paper trade, written by the daily RSI engine (17:15) for every primary,
control and shadow trade. Journals: `november_journal_bank.md`, `november_journal_nifty.md`,
`november_journal_stocks.md`. Placeholders in <angle brackets> — never leave a field blank;
write "n/a — <reason>" instead. Paper only, real money ₹0.

---

## <YYYY-MM-DD> · <INDEX/STOCK> · <CE/PE or LONG/SHORT> <strike/symbol> · <PRIMARY | CONTROL | SHADOW-TUNED v<n>>

- **Strategy in play:** <frozen setup name + book, e.g. B2 opening-range breakout, BNF-PAPER-V1>
- **Basis for the trade (why this trade, why then):** <the trigger in plain words — level(s)
  involved (PDH/PDC/PDL, OR high/low, Red band), the confirming candle and its time, the rule
  in the frozen spec that authorised entry. This is the audit trail: a reader must be able to
  re-derive the entry from the spec + candles alone.>
- **Market context at entry:** <gap up/down/flat, day type so far (trend/chop), spot level,
  time of day, anything the spec treats as state (e.g. premium band, cold/warm state)>
- **Entry:** <HH:MM> @ ₹<entry premium> (open of entry candle, per frozen convention) · 1 lot
- **Planned exits at entry:** stop ₹<…> (−50) · target ₹<…> (+90) [Nifty runner: lock +50 after
  +90, second target +150] · square-off 15:10
- **What actually happened:** <path in a line or two — best point reached (MFE +<n> pts at
  <time>), worst point (MAE −<n> pts), then the exit>
- **Exit:** <HH:MM> @ ₹<exit premium> — <TARGET | STOP | RUNNER-LOCK | SQUARE-OFF 15:10>
- **Result:** <±₹ net after ₹220 cost> (<± points> on the premium) · full-target? <yes/no>
- **Rules followed exactly?** <yes — or name the deviation; a deviation is a defect, logged as such>
- **Same-day comparison:** <what the control (index) / incumbent (shadow) did on this signal —
  taken/skipped and its result; "no equivalent signal" if none>

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** <one named cause from the taxonomy: entry-bar whipsaw /
  stop-before-target race · fired into overhead resistance (or support for PE) · no
  follow-through chop · runner locked then decayed · gap through stop · slow give-back
  (exit-rule failure, entry was right) · other (describe)>
- **Evidence:** <the candle facts that prove the cause — times, levels, premium path>
- **Has history seen this before?** <how often this cause appears for this setup in the
  backtest (count / share of the setup's losses), worst historical month for it>
- **The fix:** <the tuning candidate this failure feeds — rule diff in one line — and its
  status: PROPOSED (in tonight's tuning queue) | TESTING | GATE PASS → shadow from <date> |
  GATE FAIL (<which leg>) | ALREADY FIXED by shadow v<n> (link) | NO FIX — accepted risk
  (<why>)>
- **Lesson ID:** <RSI-<INDEX>-<NNN>, cross-referenced in the RSI log and candidate registry>

### If the trade won
- **Why it worked:** <which part of the basis carried it — level quality, confirmation,
  follow-through — one or two lines; winners are audited too, so a lucky win is labelled lucky>
- **Give-back check:** <MFE vs captured — if it ran far beyond the exit, note it as exit-tuning evidence>
