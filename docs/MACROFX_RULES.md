# How MacroFX works

MacroFX is a weekly currency-momentum strategy. Once a week it ranks the eight major currencies from strongest to weakest, then holds up to two trades that bet on the strong ones continuing to beat the weak ones. It runs on a **MidasFX demo account (1041307)** through an MT4 Expert Advisor (EA) connected to this Railway service.

Strategy version: **macrofx-v1.1**. Bridge version: **EA v2.02**.


## 1. The big picture

1. **All week**, the EA on the MT4 terminal sends Railway the account balance, open positions and daily closing prices for 28 currency pairs, every minute.
2. **Every Friday at 9 PM ET** (8 PM ET in winter), Railway runs the model on those prices and writes the **weekly targets**: the list of positions the model says to hold next week.
3. **Trades are placed by command.** Railway sends the EA a specific command such as "close ticket 8984249" or "open NZDUSD short 0.01". The EA claims the command, checks its own safety rules, trades, and reports back.

> **Current status:** EA v2.02 does **not** turn the weekly targets into trades by itself. The *This Week* tab shows the differences between the targets and what is held; someone has to act on them. Automating this, with an approval step, is upgrade #1.


## 2. How a currency is scored

The model works on **currencies, not pairs**. Each day it splits the 28 pair moves into how much each of the eight currencies (USD, EUR, GBP, JPY, CHF, CAD, AUD, NZD) moved on its own. That gives each currency its own "strength" price series.

For each currency it then measures:

| Time period | Trading days | Weight |
|---|---:|---:|
| ~1 month | 21 | 15% |
| ~3 months | 63 | 30% |
| ~6 months | 126 | 35% |
| ~12 months | 252 | 20% |

- Each return is divided by the currency's recent volatility (last 60 days), so a calm currency's steady climb counts as much as a wild currency's bigger swing.
- **Score** = the weighted total. Positive means strong, negative means weak.
- **Agreement** = how many of the four periods point the same way (0–4). A currency up on every timeframe has 4/4.

## 3. How a pair is scored

1. The eight currency scores are standardized (average 0, spread 1).
2. **Gap** = first currency minus second currency. EURAUD uses EUR minus AUD.
3. **Pair score** = `0.50 × gap + direction × (0.35 × agreement + 0.15 × liquidity)`
    - *direction* is +1 if the gap is positive, −1 if negative.
    - *agreement* is the weaker of the two currencies' counts, divided by 4.
    - *liquidity* is 1.0 if the pair contains USD, otherwise 0.8.
4. **Positive pair score = buy (long). Negative = sell (short).**

## 4. How the two trades are picked

A pair is only **eligible** if all of these are true:

- Both currencies have at least **3 of 4** periods agreeing.
- One currency is strong (positive score) and the other is weak (negative score).
- The pair score is at least **0.50** either way.

Then:

1. Sort the eligible pairs by score size, biggest first.
2. Walk down the list and take a pair unless one of its currencies is **already used**.
3. Stop at **2 pairs**.

Every trade is **0.01 lots** (the smallest size).

**Example (week ending Oct 9):** EURAUD (−1.810) was picked first. EURUSD and AUDCHF were next but reused EUR or AUD, so they were skipped. NZDUSD (−1.533) took the second slot, beating USDCHF by 0.0002.

## 5. When a trade closes

There is **no stop loss and no take-profit**. A position closes only when:

- **Next Friday's run drops it** from the targets ("target removed"), or the direction flips ("signal reversed").
- **The drawdown kill switch fires**: account equity falls 10% from its high, and the EA closes every MacroFX position.
- **An operator closes it** by command or by hand.

## 6. Swap

**The model does not look at swap or interest rates at all.** It picks purely on price momentum. Swap is charged or paid by the broker every night a position is held (triple on Wednesdays). It is recorded on every position and closed trade, and shown on the dashboard, but it does not feed back into the picks.

## 7. Safety rules (enforced in two places)

| Rule | Server (Railway) | EA (MT4) |
|---|:---:|:---:|
| Demo account only | ✓ | ✓ |
| Trading OFF by default (`EnableTrading=false`) | | ✓ |
| Remote control OFF by default | ✓ | ✓ |
| Max **2** MacroFX positions | ✓ | ✓ |
| Max **0.01** lots per pair | ✓ | ✓ |
| One position per pair | ✓ | ✓ |
| Only touches its own trades (magic number 26092601) | | ✓ |
| Spread and slippage limits | | ✓ |
| 10% drawdown kill switch | | ✓ |
| Stale connection (no heartbeat for 10 min) blocks commands | ✓ | |
| Commands expire after 5 minutes | ✓ | ✓ |
| Each command runs once, by one chart only | ✓ | ✓ |
| Pausing entries always works, even with trading off | ✓ | ✓ |
| No martingale, grid, averaging down or recovery sizing | ✓ | ✓ |

Remote settings can only make limits **stricter** than the EA's local settings, never looser.

## 8. How a command flows

1. An admin creates a command (e.g. "open EURAUD short 0.01"). It is **PENDING** for 5 minutes.
2. On its next poll (every 60 seconds), the EA sees it and asks to **claim** it. Exactly one EA wins and gets a one-time token.
3. The EA runs its own safety checks, then trades or refuses.
4. It reports back with the token as **ACKED** (done) or **FAILED** (refused, with the reason). Nobody else can overwrite that result.
5. A command that was claimed but never reported back stays **CLAIMED** for a human to review. It is **never retried automatically**, because the order might have gone through.

## 9. Research discipline

- The weekly report is a **feedback loop, not an auto-optimizer**. Nothing changes the rules automatically.
- Never change the time periods or thresholds because of one trade or one bad week.
- Every rule change gets a **new version number** and must be tested on data it wasn't built on before it goes live.
- Track spread, slippage, swap and commission separately from signal quality, so trading costs aren't mistaken for a bad signal.
