# Potential upgrades

Status key: **Proposed** (idea, not approved) · **Approved** · **In progress** · **Done**

Every strategy change must be versioned and tested out-of-sample before it goes live. Operations items don't change the signal.


## Signal v2 plan — draft for review (Oct 14, 2026)

**Status:** Proposed. Nothing in this section is built, tested or trading. It is written so that someone outside the project can rate it. A scorecard for reviewers is at the end of this section.

### Why a new signal

- **The current signal (v1.1, weekly currency momentum) has no edge.** Backtest 2000–2026 with the live engine code: −6.5% a year before costs, −7.5% with weekday costs, negative in both 2000–2012 and 2013–2026 (Backtest tab).
- **The code is not the problem.** The same engine earned +13.5% a year (Sharpe 0.75) over 1975–1999. Published research dates the death of G10 currency momentum to about 2001.
- **Our follow-up tests point to a blend.** Value (5-year inflation-adjusted reversal) earned Sharpe 0.30 over 2000–2026, positive in both halves. 12-month trend: 0.11. Value + trend: 0.35 with a −12% max drawdown, but it fails a 1% swap-fee net test. Carry could not be tested yet because no interest-rate history was reachable.
- **The literature agrees.** A blend of carry, value and trend is the only construction with a defensible record after 2010, and even that earned low single digits a year (Research report on the Backtest tab).

### The design in one paragraph

Once a month, score each of the 8 currencies (USD, EUR, JPY, GBP, CHF, CAD, AUD, NZD) on four things: **value, carry, macro trend and trend**. Average the four scores and trade the strongest currencies against the weakest through the existing approval queue. Filters can block or shrink a trade but never add one. Outside opinions (banks, analysts) are recorded and scored, but they get no say in trading until they prove themselves.

### The four scores (equal weight, 25% each)

| Score | The question | How it is measured | Evidence so far |
|---|---|---|---|
| **Value** | Is the currency cheap or expensive? | Change in the exchange rate over the past 5 years after adjusting for inflation differences. A big inflation-adjusted fall = cheap = buy. Monthly CPI, lagged for release dates; BIS real effective exchange rates as a cross-check. | Our test: Sharpe 0.30, both halves positive. AQR: 0.60 across 20 developed currencies. Weak recent run (Russell: −0.3%/yr over 5 years to Mar 2024). |
| **Carry** | Which currencies pay you to hold them? | Backtest: 3-month interest rate, lagged one month, minus an estimated broker swap fee. Live: MidasFX's actual swap rates uploaded by the EA (upgrade #4). | G10 carry Sharpe 0.78 over 1976–2013, about zero over 2010–2020, revived 2022–26 as rate gaps reopened. Prone to sudden crashes (2008). |
| **Macro trend** | Are the central bank and the economy moving in the currency's favour? | Two halves, averaged. **Rate direction:** 3-month change in short-term rates and in 2-year yields (10-year as fallback where 2-year history is missing). **Economy:** unemployment falling, industrial production growing, inflation rising versus a year ago. | Dahlquist & Hasseltoft "economic momentum": Sharpe 0.70 over 1976–2017, but in-sample and including emerging markets. Not yet tested by us. |
| **Trend** | Is it already moving? | 12-month return of each currency against the dollar, adjusted for volatility. This replaces the v1.1 weekly engine, which the research says to abandon. | Weakest evidence: our test Sharpe 0.11; −0.16 over 2010–2020 in published work. Kept mainly because it tends to gain when carry crashes (2008). Tested with and without; dropped if the blend is better without it. |

**Combining:** each score is turned into a rank from −1 (worst of the 8) to +1 (best), and the four ranks are averaged. Weights are fixed at 25% each before any test. They will not be tuned to the backtest.

### Portfolio and execution (existing rules unchanged)

- Rebalance **monthly**, on the first Monday after the London open, through the approval queue (Casey approves every plan).
- Long the #1 currency against the #8, and the #2 against the #7: at most **2 pairs**, no currency used twice, **0.01 lots**, **demo only**.
- Keep a held pair unless a replacement beats it by a margin (hysteresis, upgrade #7).
- Same execution guards as today: weekdays 4 AM–4 PM ET, 30-point spread cap, never retry an uncertain order.

### Filters (can only block or shrink a trade)

| Filter | Rule (fixed before testing) | Evidence |
|---|---|---|
| **Swap cost limit** | Skip a pair if the swap against the position costs more than 2% a year. | Retail swap fees take a third to half of a G10 premium. |
| **Carry volatility control** | When the carry trades' own volatility over the past month is above its 3-year median, drop one pair; above twice the median, go flat. | Best-supported crash control: Moreira & Muir, +2.78%/yr alpha on carry. Not full crash protection: 2008 losses came over weeks. |
| **COT crowding** | Cut a currency's carry score when speculators' net position is in the top 10% of its 3-year range. | Weak. Speculators are mostly carry traders, but positioning predicted crash risk only loosely (Brunnermeier, Nagel & Pedersen). |
| **VIX switch** | Cut carry when VIX is above its 1-year 80th percentile. **Tested as a comparison only; expected to fail.** | Against it: VIX spikes arrive with carry losses, not before them, and rising VIX predicted *higher* carry returns 3–4 quarters later. Timing carry with equity volatility turned its alpha negative (−1.28). |

### Add-ons tested only after the core blend

- **News surprise index:** whether each country's data keeps beating or missing economists' forecasts. Each release is weighted by how much the currency actually moved after past surprises. Source: MetaTrader 5's built-in economic calendar (history depth still to be checked), then Forex Factory (from about 2007, if its terms allow), then FXStreet's paid feed.
- **Central bank tone:** AI rates each policy statement hawkish or dovish. Statement archives go back to the 1990s.
- **Dollar carry (separate sleeve):** long the 7 other currencies against USD when their average short-term rate is above the US rate, otherwise short; no position when the gap is under 0.5%. Published Sharpe 0.66 (1983–2010). Our 28-pair ranking currently nets this dollar effect out.

### Tracked only (zero weight in trading)

- **Bank forecasts:** ING's monthly forecast table (free; back issues to about Dec 2022 need a manual download). First check: ING's April 2026 table did slightly worse than "no change" (6-month average miss 3.29% vs 2.93%; direction right 6 of 10).
- **FXStreet Forecast Poll:** weekly 1-week, 1-month and 1-quarter calls on the majors. History needs a paid licence; otherwise recorded from now on.
- **Analysts on X and YouTube:** directional calls logged with dates and scored after 1, 3 and 6 months.
- **Weekly AI research digest on the dashboard:** central bank statements, free bank research, news, and next-meeting rate odds, with a flag wherever they disagree with the model.

**Promotion rule:** an opinion source can be proposed as a versioned add-on only after 12 months of scored calls, if it beats the "no change" baseline and improves the blend in a paper test.

### Data sources

| Data | Source | History | Cost |
|---|---|---|---|
| Daily exchange rates | Fed H.10 (already used) + MT4 history from the EA | 1971 → | Free |
| Monthly CPI, unemployment, industrial production | FRED (OECD Main Economic Indicators) | 1960s–80s → | Free |
| 3-month interest rates | FRED (OECD); US from 1964, Australia from 1968, both updated to Aug 2026 | 1960s–80s → | Free |
| 10-year yields; 2-year yields | FRED (OECD); 2-year from each central bank's website | Varies | Free |
| Policy rates; real effective exchange rates | BIS data portal | Decades | Free |
| Original (unrevised) economic releases | ALFRED (US); OECD revisions database (G7) | Varies | Free |
| VIX | FRED | 1990 → | Free |
| Speculator positioning | CFTC Commitments of Traders | 1986 → (detailed split from 2006) | Free |
| Economic calendar (actual vs forecast) | MT5 built-in calendar; Forex Factory; FXStreet | ~2007 → | Free / paid |
| MidasFX swap rates and spreads | EA upload (upgrade #4) | From now on | Free |

**Access:** the build environment can only reach GitHub, so FRED, BIS and the CFTC are blocked there. Plan: a monthly data job on the Railway service (access still to be confirmed), or manual CSV downloads as a fallback.

### Test rules (written before any run)

- **Period:** 2000–2026 is the main test; 1980s–1999 as a check where data exists.
- **No fitting to 2000–2026.** Use literature defaults: 3-month rates lagged one month, 60-month real exchange-rate change, 12-month trend. The weights and filter thresholds above are fixed now.
- **Only data that was known at the time:** original releases where available, otherwise a 2–3 month lag. COT data is used from its Friday publication, not its Tuesday measurement date.
- **Costs:** weekday spreads per pair, with crosses stressed at 2×. Swap = interest-rate gap minus a 1% fee (0.5% as the optimistic case).
- **Pass (the blend and each score alone are judged the same way):**
  1. Gross Sharpe of at least 0.3 over 2000–2026.
  2. Positive in both 2000–2012 and 2013–2026.
  3. Net Sharpe of at least 0.2 after spreads and swap fees.
  4. Above the 95th percentile of random pair picks (+0.12).
  5. Maximum drawdown at micro-lot sizing of about 30% or less.
- **Add-ons and filters** pass only if they raise net Sharpe, or cut max drawdown without lowering net Sharpe, in both halves.
- **Every variant run is reported, including failures,** with the total number of variants stated.
- **A pass is not proof.** A Sharpe of 0.3 over 26 years is only about 1.5 standard errors from zero.

### What happens after the test

- **Fail:** no signal change. v1.1 stays on demo as an infrastructure test only, and the result is published on the Backtest tab.
- **Pass:** a new version (macrofx-v2.0) runs on demo through the approval queue for at least 6 months as a forward test, with a Signals panel on the dashboard.
- **Real money:** only after a pass, and only on an account of $10,000 or more. Expected net return at proper sizing is roughly 0.5–3% a year. Forced into 0.01 lots on $1,000, the expected gain is about $50 a year.

### Build order

1. **Data job on Railway:** confirm Railway can reach FRED, BIS and the CFTC, then load all history and refresh monthly.
2. **EA additions:** daily swap and spread upload on MT4 (#4), and a calendar export script on MT5.
3. **Backtest:** each score alone, then the blend, then filters and add-ons, against the rules above.
4. **Dashboard:** Signals panel (8 currencies × 4 scores, with history) and the weekly digest.

### Reviewer scorecard

Please rate each item from 1 (poor) to 5 (strong), with a one-line reason.

| Item | Rating (1–5) | Reason |
|---|---|---|
| Choice of the four scores | | |
| Equal weights, fixed in advance | | |
| How macro trend is measured | | |
| Filters (swap limit, carry volatility, COT, VIX) | | |
| Treatment of bank and analyst opinions | | |
| Test rules and pass criteria | | |
| Data plan | | |
| Execution and risk limits | | |
| **Overall: worth building?** | | |

**Open questions:**
1. Should trend stay in the blend at all?
2. Should dollar carry be a separate sleeve or part of the blend?
3. Monthly or quarterly rebalancing?
4. Are 2 pairs enough diversification?
5. What is missing?

### Independent review #1 — AI reviewer (Oct 14, 2026)

**Who:** a separate Claude Opus 5.5 agent that had not seen how the plan was developed. It read only this page, the research report and the backtest report, and was asked for an honest rating, not encouragement. This is not a human expert review; more reviewers are welcome.

**Checked afterwards against project files:** the −0.02 result for 12-month ranking (`docs/backtest/REPORT.md`), the 30-run random benchmark, the GBP/EUR/JPY rate-data gaps (`docs/research/notes/retail_implementation_and_data.md`), and the five Dahlquist & Hasseltoft variables (Alpha Architect summary). All confirmed.

**Overall: 3 out of 5. Worth building as a narrowed, low-cost research test, not as a source of income.**

| Item | Rating | Reason |
|---|---|---|
| Choice of the four scores | 3 | Carry and value are right. "Trend" as written ranks the 8 currencies on 12-month returns, which is the abandoned momentum factor (that ranking scored −0.02 in the v1.1 check). The 0.11 cited came from a different strategy: time-series trend on the 7 USD pairs. Macro trend is not one of the research report's ranked specs. |
| Equal weights, fixed in advance | 3 | A sound default, but half the weight goes to the two weakest scores. "Drop trend if the blend is better" un-fixes the weights. Ranks ignore how big a rate gap is; the report used z-scores. |
| How macro trend is measured | 2 | Doesn't follow its source: Dahlquist & Hasseltoft used 3–5-year trends in industrial production, retail sales, unemployment, consumer and producer prices, and no interest rates. Rate changes overlap carry. AUD/NZD data are mostly quarterly; unrevised data exist only for the US and G7. |
| Filters | 2 | The 2% swap limit double-counts carry and would veto most swap-paying trades when rate gaps are wide. Own-volatility control is the only supported filter (t ≈ 1.9), but "above the 3-year median" means running one pair about half the time. COT has no support in the research notes. VIX is expected to fail. |
| Treatment of bank and analyst opinions | 4 | Zero weight is right. But 12 months of calls can't prove skill, and a "disagrees with the model" flag invites manual vetoes. |
| Test rules and pass criteria | 3 | Good habits: every variant reported, both halves, costs, honest t-stat. But 2000–2026 is already used (value and trend were tested on it), the bar is only t ≈ 1.5, and the random benchmark is 30 runs of the weekly design. |
| Data plan | 3 | Right, free sources. Missing known gaps: GBP 3-month rate stops at Jan 2026, euro needs a Euribor splice, JPY starts Apr 2002. EUR value needs 60 months after 1999 unless a German proxy or BIS REER is used. Railway access unconfirmed. |
| Execution and risk limits | 3 | Monday fills, spread cap, demo-only and the $10K rule are good. But 2 micro-lots run several times the volatility the evidence assumes, there is no tie-break (averaged ranks tie often), and the 0.25 hysteresis margin is on v1.1's old score scale. |
| **Overall: worth building?** | **3** | Yes as a narrowed research test; no as income. |

**Answers to the open questions:**
1. **Trend:** keep it only as a time-series trend on USD pairs, as its own sleeve, or drop it, and decide before running. Choosing after seeing 2000–2026 results is fitting to the data.
2. **Dollar carry:** a separate sleeve, tested as a main candidate alongside the blend. A dollar-neutral ranking can't express it, and the dollar part of carry paid the cleaner return.
3. **Rebalancing:** monthly, fixed now. Don't test both and pick.
4. **Two pairs:** not enough. They often make the same risk-on bet (long AUD/NZD against JPY/CHF). Check whether MidasFX offers a cent or nano account.
5. **Missing:** a true holdout (pre-2000 data, plus NOK/SEK, which are free in the H.10 file); a definition of "gross" that includes the rate differential; a tie-break rule; rules for when Casey may override a plan; forward-test criteria that check operations (fills, swap), not P&L.

**Top 5 problems, with fixes:**
1. **The trend score revives dead momentum** (and divides by zero for USD). Fix: make it a time-series USD-pair sleeve, or remove it.
2. **Multiple testing.** Roughly 15–20 new variants on top of about 15 earlier runs on the same data; the best of 15 zero-edge variants would show a Sharpe near 0.3 by luck. Fix:
   - Name one primary hypothesis: carry + value, 50/50, 2 against 2, monthly.
   - Commit the spec before running.
   - Require pre-2000 and NOK/SEK as a confirmation gate.
   - Rebuild the random benchmark for the monthly design with at least 1,000 runs.
   - Treat everything else as exploratory.
3. **Macro trend is unproven and doesn't match its source.** Fix: move it to add-ons. If kept, copy Dahlquist & Hasseltoft's variables and horizons, and test rate direction separately.
4. **Filters distort the blend.** Fix:
   - Model swap inside returns instead of a 2% veto.
   - Apply volatility control to the blend's own volatility, trigger at about 1.5× the median, and say which pair is dropped.
   - Drop VIX; move COT to tracked-only.
5. **Live won't match the backtest.** Live carry uses MidasFX swap while the backtest uses 3-month rates, and manual approval is an untested filter. Fix: compute live scores from the same rate data, use broker swap only for costs, log every override, and measure drawdown at exact live sizing.

**Verdict:** the core idea, carry plus value, matches the literature and our research. Around it the plan adds two shaky scores, four filters (two unsupported) and enough variants that a pass on the already-used 2000–2026 data would mean little. Trim to carry + value, with dollar carry as a separate test, before building anything beyond the data job.

| Expected result for the trimmed blend | |
|---|---|
| Gross Sharpe, 2000–2026 | about 0.2–0.4 |
| 2000–2012 | clearly positive |
| 2013–2026 | weak (0–0.2), propped up by 2022–26 |
| Net Sharpe after a 1% swap fee | about 0.1–0.25 |
| Max drawdown at live sizing | 35–50%, driven by 2008 |

Most likely outcome: a gross pass that fails the net or drawdown test under the plan's own rules. Chance of a clean pass: roughly one in three, and even a pass would not be statistically convincing.

**Status:** the plan above has **not** been revised yet. Changes wait for Casey's decision.


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

### 9. Swap / carry awareness — *Proposed* (now part of the Signal v2 plan: carry score + swap cost limit)
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

**Plan written (Oct 14, 2026):** see "Signal v2 plan — draft for review" at the top of this page.


## Done

- **Weekly approval queue, Monday execution, complete records, backtest** — Oct 14, 2026 (#1, #2, #3, #6).
- **Restart + network outage** verified on the real terminal (17/17), Oct 14, 2026.
- **Bridge v2.02 remote control** — claim tokens, pause latch, duplicate guards, 28 backend tests, live demo execution verified (Oct 13, 2026).
