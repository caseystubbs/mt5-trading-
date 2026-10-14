# Potential upgrades

Status key: **Proposed** (idea, not approved) · **Approved** · **In progress** · **Done**

Every strategy change must be versioned and tested out-of-sample before it goes live. Operations items don't change the signal.


## Operations (no change to the trading signal)

### 1. Weekly targets → approval queue — **Done** (Oct 14, 2026)
**Problem:** EA v2.02 does not act on the weekly targets, so Friday's picks are never traded unless someone does it by hand.

**Proposal:** After the Friday run, create the needed close/open commands as *awaiting approval*. Casey approves, then they are sent to the EA. A position closed by hand is never reopened automatically.

**Evidence:** v2.02 `OnTimer` intentionally skips `PollTargets` (DEV_LOG 2026-10-13).

### 2. Stop trading at the Sunday reopen — **Done** (Oct 14, 2026)
**Problem:** Every model trade so far filled at the Sunday open, at spreads of **130–365 points**, versus **6–9 points** on weekday fills. That is roughly $12 of spread, more than all realized profit to date (+$4.41).

**Proposal:** Execute the weekly changes Monday after the London open (about 3–4 AM ET), and only if the spread is under a set limit; otherwise retry hourly.

**Result:** Built with #1. Plans run Monday from 4 AM ET, weekdays 4 AM–4 PM ET only; opens need a spread of 30 points or less. The backtest shows Sunday execution would have cost about 22% a year.

### 3. Complete the feedback records — **Done** (Oct 14, 2026)
**Problem:** Fills sent by remote command record signal score 0 and are always labeled "macrofx-v1.1". The full pair ranking from each Friday run is not saved.

**Proposal:** Carry the target's score and the strategy version on every command and fill; store the full ranking per run.

**Result:** Commands carry score, version and plan number; the EA's fills are tagged when it acknowledges; plan trades are labelled as model trades; each Friday run saves the full 28-pair ranking.

### 4. Upload broker swap rates — *Proposed* · Priority: high (decides whether carry is viable)
**Problem:** The dashboard shows swap already charged, but not what a pair *will* cost per night.

**Proposal:** The EA uploads `MODE_SWAPLONG`/`MODE_SWAPSHORT` for all 28 pairs daily, so the dashboard shows expected nightly swap for current and upcoming trades.

### 5. Remote drawdown limit — *Proposed*
**Problem:** The kill switch can only be tested at the terminal.

**Proposal:** A server-side drawdown limit that can only be **stricter** than the EA's local 10%. That allows remote testing and tighter risk without reinstalling.


## Strategy research (needs a new version and out-of-sample testing)

### 6. Historical backtest — **Done** (Oct 14, 2026)
**Problem:** There are 3 model-driven exits so far, which is far too few to tell whether the signal has an edge.

**Proposal:** Backtest v1.1 over 10+ years of daily data with realistic costs (Sunday vs weekday spreads, swap). Use it to test items 7–10 in days instead of months of live trading.

**Result:** 2000–2026, 1,397 weekly rebalances using the live engine code. **No edge:** −6.5%/yr before costs, −7.5%/yr with weekday costs, losing in both halves (t = −1.55). Swap not modelled. See the Backtest tab and `docs/backtest/REPORT.md`.

### 7. Rotation buffer (hysteresis) — *Tested, on hold*
**Problem:** Last week USDCHF was replaced by NZDUSD over a **0.0002** score difference, paying about $3 in Sunday spread for nothing.

**Proposal:** Keep a held pair while it is still eligible, unless a replacement beats it by a margin (e.g. 0.25).

**Backtest:** halves trading (57 → 31 trades a year) and cost drag (1.1% → 0.6% a year), but the result stays negative (−7.2%/yr). Worth keeping in any future signal; doesn't fix this one.

### 8. Clean up the pair score — *On hold*
**Problem:** Agreement is counted twice (0.20 + 0.15), and the fixed bonus terms add 0.38–0.50 to every eligible pair, which makes the 0.50 minimum almost meaningless.

**Proposal:** Make the bonuses proportional to the signal, or raise the minimum; test both.

### 9. Swap / carry awareness — *Proposed* (now part of #11)
**Problem:** The model ignores swap, so it can hold a trade that pays swap every night for weeks.

**Proposal:** First version: block a pair when swap strongly opposes the position. Second version: subtract expected weekly carry from the pair score.

### 10. Volatility stop — *Tested, on hold*
**Problem:** No protection between weekly rebalances except the 10% kill switch. AUDCHF went as low as −$13.17 and never got above +$1.65 in profit.

**Proposal:** Test a stop at a multiple of each pair's recent volatility, as already listed in the weekly review's research items.

**Backtest:** a 2× weekly-volatility stop made no material difference (−7.6%/yr vs −7.5%/yr).

### 11. Research a new signal — *Proposed* · Priority: highest for research
**Problem:** The backtest shows currency momentum alone has not paid in G8 FX since 2000, at any of its four horizons.

**Proposal:** Test carry (interest-rate differential), carry + momentum, and longer holding periods, through the same backtest before any of them touch the demo. Needs a source of historical short-term interest rates.

**Hold:** No signal changes, no size increase and no live account until a candidate shows a real edge in the backtest.

**Research done (Oct 14, 2026):** see `docs/research/LONG_TERM_FX_SYSTEMS.md` (Backtest tab).
- The evidence says G10 momentum died around 2001. Our exact engine earned +13.5%/yr (Sharpe 0.75, t = 3.8) over 1975–1999, so the code is right.
- Value (5-year real FX reversal) stayed positive in both halves of 2000–2026 (Sharpe 0.30); value + trend reached 0.35 with a −12% max drawdown. Both are small and fail a 1% swap-fee net test.
- Next steps, in order:
  1. EA logs MidasFX swap and spreads daily (#4).
  2. One-time fetch of FRED/BIS rates and real effective exchange rates from outside the sandbox.
  3. Backtest carry + value (dollar-neutral, monthly) and dollar carry against pass criteria written down before the run.
- Real money only at $10,000+ (a $1,000 account cannot size these strategies).


## Done

- **Weekly approval queue, Monday execution, complete records, backtest** — Oct 14, 2026 (#1, #2, #3, #6).
- **Restart + network outage** verified on the real terminal (17/17), Oct 14, 2026.
- **Bridge v2.02 remote control** — claim tokens, pause latch, duplicate guards, 28 backend tests, live demo execution verified (Oct 13, 2026).
