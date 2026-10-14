# Potential upgrades

Status key: **Proposed** (idea, not approved) · **Approved** · **In progress** · **Done**

Every strategy change must be versioned and tested out-of-sample before it goes live. Operations items don't change the signal.


## Operations (no change to the trading signal)

### 1. Weekly targets → approval queue — *Proposed* · Priority: before next Sunday
**Problem:** EA v2.02 does not act on the weekly targets, so Friday's picks are never traded unless someone does it by hand.

**Proposal:** After the Friday run, create the needed close/open commands as *awaiting approval*. Casey approves, then they are sent to the EA. A position closed by hand is never reopened automatically.

**Evidence:** v2.02 `OnTimer` intentionally skips `PollTargets` (DEV_LOG 2026-10-13).

### 2. Stop trading at the Sunday reopen — *Proposed* · Priority: high
**Problem:** Every model trade so far filled at the Sunday open, at spreads of **130–365 points**, versus **6–9 points** on weekday fills. That is roughly $12 of spread, more than all realized profit to date (+$4.41).

**Proposal:** Execute the weekly changes Monday after the London open (about 3–4 AM ET), and only if the spread is under a set limit; otherwise retry hourly.

### 3. Complete the feedback records — *Proposed*
**Problem:** Fills sent by remote command record signal score 0 and are always labeled "macrofx-v1.1". The full pair ranking from each Friday run is not saved.

**Proposal:** Carry the target's score and the strategy version on every command and fill; store the full ranking per run.

### 4. Upload broker swap rates — *Proposed*
**Problem:** The dashboard shows swap already charged, but not what a pair *will* cost per night.

**Proposal:** The EA uploads `MODE_SWAPLONG`/`MODE_SWAPSHORT` for all 28 pairs daily, so the dashboard shows expected nightly swap for current and upcoming trades.

### 5. Remote drawdown limit — *Proposed*
**Problem:** The kill switch can only be tested at the terminal.

**Proposal:** A server-side drawdown limit that can only be **stricter** than the EA's local 10%. That allows remote testing and tighter risk without reinstalling.


## Strategy research (needs a new version and out-of-sample testing)

### 6. Walk-forward backtest — *Proposed* · Priority: highest for research
**Problem:** There are 3 model-driven exits so far, which is far too few to tell whether the signal has an edge.

**Proposal:** Backtest v1.1 over 10+ years of daily data with realistic costs (Sunday vs weekday spreads, swap). Use it to test items 7–10 in days instead of months of live trading.

### 7. Rotation buffer (hysteresis) — *Proposed*
**Problem:** Last week USDCHF was replaced by NZDUSD over a **0.0002** score difference, paying about $3 in Sunday spread for nothing.

**Proposal:** Keep a held pair while it is still eligible, unless a replacement beats it by a margin (e.g. 0.25).

### 8. Clean up the pair score — *Proposed*
**Problem:** Agreement is counted twice (0.20 + 0.15), and the fixed bonus terms add 0.38–0.50 to every eligible pair, which makes the 0.50 minimum almost meaningless.

**Proposal:** Make the bonuses proportional to the signal, or raise the minimum; test both.

### 9. Swap / carry awareness — *Proposed*
**Problem:** The model ignores swap, so it can hold a trade that pays swap every night for weeks.

**Proposal:** First version: block a pair when swap strongly opposes the position. Second version: subtract expected weekly carry from the pair score.

### 10. Volatility stop — *Proposed*
**Problem:** No protection between weekly rebalances except the 10% kill switch. AUDCHF went as low as −$13.17 and never got above +$1.65 in profit.

**Proposal:** Test a stop at a multiple of each pair's recent volatility, as already listed in the weekly review's research items.


## Done

- **Bridge v2.02 remote control** — claim tokens, pause latch, duplicate guards, 28 backend tests, live demo execution verified (Oct 13, 2026).
