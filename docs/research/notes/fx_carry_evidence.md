# FX Carry Trade Evidence: G10/Developed Currencies (long-run returns, crash risk, overlays, post-2008, retail implementation, data)

## 1. Original academic evidence: returns, Sharpe ratios, skewness (in-sample, mostly pre-2010)

### Takeaway
Carry has positive returns in every major paper, but each paper's sample ends between 2006 and 2013. For developed or G10 currencies, in-sample Sharpe ratios run from about 0.3 to 0.9 depending on construction, and returns are reliably negatively skewed. Results for broad "all countries" samples are higher than developed-only results because they include emerging-market currencies.

### Cited Findings
**Lustig, Roussanov & Verdelhan (LRV), "Common Risk Factors in Currency Markets" (NBER w14082 version; published RFS 2011)**
- Sample: monthly, Nov 1983 – Mar 2008. 37 currencies, with a developed subsample of 15 countries. Six portfolios sorted on forward discount (interest differential). — [NBER w14082](https://www.nber.org/papers/w14082.pdf)
- HML_FX (high minus low forward-discount portfolio), all countries, net of bid-ask spreads: 483 bp per year ("4.8 percent per annum"), annualized Sharpe ratio 0.54. — [NBER w14082](https://www.nber.org/papers/w14082.pdf)
- HML_FX, developed countries (15), net of bid-ask: Sharpe ratio 0.39. The extracted text did not report the mean or SD. — [NBER w14082](https://www.nber.org/papers/w14082.pdf)
- Dollar factor (RX, the average excess return of all foreign currencies vs USD): sample mean 136 bp per year. — [NBER w14082](https://www.nber.org/papers/w14082.pdf)
- HML_FX explains about 70% of the variation in average excess returns across the six portfolios. Two principal components (dollar plus carry) explain more than 80% of the variation in portfolio returns. — [NBER w14082](https://www.nber.org/papers/w14082.pdf)
- During the Aug 2007 episode, JPY rose "up to 1.7 percent in one day" and NZD and AUD fell "up to 2.3 percent in one day." — [NBER w14082](https://www.nber.org/papers/w14082.pdf)
- Note: the published RFS 2011 version reportedly extends the sample to 2009. I did not verify its numbers. The figures above come from the NBER working paper.

**Burnside, Eichenbaum, Kleshchelski & Rebelo, "Do Peso Problems Explain the Returns to the Carry Trade?" (NBER w14054; RFS 2011)**
- Equally weighted carry, up to 20 currencies (includes non-G10, so it is not a pure G10 sample), USD base, Feb 1976 – Jul 2009, no transaction costs: mean 4.82% per year, SD 5.3%, Sharpe 0.911, skewness −0.648, excess kurtosis 5.81. Over the same period the US stock market had a Sharpe of 0.373 (mean 5.82%, SD 15.6%). — [NBER w14054](https://www.nber.org/system/files/working_papers/w14054/w14054.pdf)
- Options-hedged sample: Feb 1987 – Apr 2009, six G10 currencies (AUD, CAD, EUR, JPY, CHF, GBP). Unhedged: mean 2.96%, SD 6.2%, Sharpe 0.476, skew −0.708. Hedged with near-the-money options: mean 1.58%, SD 3.5%, Sharpe 0.449, skew +0.722. — [NBER w14054](https://www.nber.org/system/files/working_papers/w14054/w14054.pdf)
- Peso-problem conclusion: in the "peso state," unhedged carry payoffs are modest (about −2.16% per month). The puzzle is explained by a very high stochastic discount factor in that state (M0/E(M) ≈ 92.9), not by large losses. — [NBER w14054](https://www.nber.org/system/files/working_papers/w14054/w14054.pdf)
- Transaction costs, earlier version (Jan 1976 – Jan 2008): with a GBP base, the Sharpe of equally weighted carry fell from 0.234 to 0.167 after bid-ask spreads. With a USD base (Jan 1997 – Jan 2008), it fell from 0.306 to 0.250. This version reports no G10-only results. — [NBER w14054 rev0](https://www.nber.org/system/files/working_papers/w14054/revisions/w14054.rev0.pdf)

**Brunnermeier, Nagel & Pedersen, "Carry Trades and Currency Crashes" (NBER w14473; NBER Macro Annual 2008)**
- Sample: 1986–2006, eight developed currencies vs USD (AUD, CAD, JPY, NZD, NOK, CHF, GBP, EUR), 3-month interbank rates. — [NBER w14473](https://www.nber.org/papers/w14473.pdf)
- Equal-weighted 3-long/3-short carry: annualized Sharpe 0.747 (weekly) and 0.784 (quarterly), skewness −0.695 (weekly) and −0.977 (quarterly). 1-long/1-short: Sharpe 0.704 (weekly), skew −0.717. Skewness does not diversify away as more currencies are added. — [NBER w14473](https://www.nber.org/papers/w14473.pdf)
- A higher interest differential predicts more negative skewness. The cross-sectional R² is 81%, and the time-series coefficient of skewness on the differential is −23.92 (SE 3.87) at t+1, decaying only slowly. "Exchange rates go up by the stairs and down by the elevator" for investment currencies, and the reverse holds for funding currencies such as JPY. — [NBER w14473](https://www.nber.org/papers/w14473.pdf)
- Signed weekly ΔVIX coefficient on carry return: −0.43 (SE 0.11) contemporaneous, −0.03 (SE 0.11, insignificant) the next week. For the diversified portfolio: −0.94 contemporaneous and −0.07 the next week. Carry trades are unwound when VIX rises. — [NBER w14473](https://www.nber.org/papers/w14473.pdf)
- Signed VIX predicts higher carry returns several quarters later: coefficient 0.53 (SE 0.23) at t+3 and t+4. — [NBER w14473](https://www.nber.org/papers/w14473.pdf)

**Menkhoff, Sarno, Schmeling & Schrimpf, "Carry Trades and Global FX Volatility" (JF 2012)**
- Sample: Nov 1983 – Aug 2009. 48 currencies, with a 15-country developed subsample (10 currencies after the euro). — [City Univ. repository](https://openaccess.city.ac.uk/id/eprint/3391/1/CTVOL_R3_v4_paper.pdf)
- High-minus-low carry, net of bid-ask. All countries: mean 7.23, SD 9.81, Sharpe 0.74. Developed countries: mean 5.72, SD 10.24, Sharpe 0.56. — [City Univ. repository](https://openaccess.city.ac.uk/id/eprint/3391/1/CTVOL_R3_v4_paper.pdf)
- Innovations in global FX volatility explain "more than 90%" of the cross-section of carry portfolio returns. Carry returns fall monotonically from low-volatility-innovation states to high ones for developed countries. Volatility dominates liquidity proxies in joint tests. — [City Univ. repository](https://openaccess.city.ac.uk/id/eprint/3391/1/CTVOL_R3_v4_paper.pdf)

**Daniel, Hodrick & Lu, "The Carry Trade: Risks and Drawdowns" (Critical Finance Review 2017) — G10 only**
- Sample: Feb 1976 – Aug 2013 (451 months). G10 currencies: AUD, GBP, CAD, EUR/DEM, JPY, NZD, NOK, SEK, CHF, USD. AUD and NZD start Oct 1986. — [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)
- USD base, annualized results:

| Strategy | Mean | SD | Sharpe | Skew |
|---|---|---|---|---|
| Equal-weight (EQ) | 3.96% | 5.06% | 0.78 | −0.49 |
| Spread-weighted (SPD) | 6.60% | 7.62% | 0.87 | −0.31 |
| EQ risk-rebalanced | 5.44% | 5.90% | 0.92 | −0.37 |
| SPD risk-rebalanced | 6.18% | 6.08% | 1.02 | −0.44 |
| Mean-variance optimized (OPT) | 2.10% | 2.62% | 0.80 | −0.89 |

  Worst months: −6.01% (EQ) and −7.26% (SPD). — [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)
- With non-USD base currencies, EQ means range from 2.42% (CHF base) to 4.70% (NZD base). The USD base has the highest Sharpe. — [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)
- After controlling for the LRV FX factors, the EQ alpha falls to 1.47% (t = 1.73, insignificant). Alphas against equity, bond, and variance-swap factors stay significant. — [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)

**Jurek, "Crash-Neutral Currency Carry Trades" (JFE 2014) — G10**
- Sample: 1990:1 – 2012:6, G10 with 45 cross pairs. Unhedged spread-weighted carry: 5.21% per year (t = 2.62). Equal-weighted: 3.36% per year (t = 2.39). Sharpe ratios are "between 0.40–0.55." — [Jurek PDF](https://www.johnhcochrane.com/s/Jurek_currency_new.pdf)

**Lustig & Verdelhan (2007, AER) — not retrieved**
- I did not fetch this paper. No numbers from it are reported here (see Gaps).

### Inferences
- For a developed-only, USD-based sample, a fair in-sample range is a Sharpe of about 0.4–0.9 before costs, with mean returns of about 3–7% per year at 5–10% volatility. All of these samples end in 2006–2013, before most of the poor post-GFC decade (see section 4).
- Negative skew does not diversify away inside G10. Adding currencies (1×1 to 3×3) left skewness around −0.7 to −1.0 (Brunnermeier, Nagel & Pedersen). An 8-currency system cannot diversify it away either.
- Broad "all countries" results (LRV 0.54, Menkhoff 0.74) are inflated relative to G10 by emerging-market currencies. Use the developed figures (LRV 0.39, Menkhoff 0.56) as benchmarks.

### Gaps
- Lustig & Verdelhan (2007, AER) numbers were not retrieved.
- LRV 2011 HML_FX standard deviation and developed-country mean were not in the extracted text, and the published RFS 2011 sample extension was not verified.
- Burnside et al. publish no clean G10-only equally weighted series. Their 20-currency series includes emerging markets.

## 2. Dollar carry trade: Lustig, Roussanov & Verdelhan (2014), "Countercyclical Currency Risk Premia"

### Takeaway
Timing the USD against a basket of all foreign currencies, using the average forward discount, produced a higher Sharpe in developed currencies (0.66, 1983–2010) than cross-sectional HML carry (about 0.3). Daniel, Hodrick & Lu confirm on G10 that much of carry's return comes from the dollar component, not the dollar-neutral cross-section.

### Cited Findings
- Sample: Nov 1983 – Jun 2010. Dollar carry trade, developed currencies: mean 5.60% per year, Sharpe 0.66. All currencies: 4.28%, Sharpe 0.56. — [NBER w16427](https://www.nber.org/papers/w16427.pdf)
- Same paper and period, HML cross-sectional carry: about 3% and Sharpe about 0.3 for developed currencies (5 portfolios), and about 4.4% and Sharpe about 0.5 for all currencies. Country-level carry was about 0.5% and not significant. — [NBER w16427](https://www.nber.org/papers/w16427.pdf)
- Dollar carry and HML carry are "essentially zero" correlated unconditionally. The exchange-rate component of developed-currency dollar carry averages 3.77% per year (bootstrap SE 1.67%). — [NBER w16427](https://www.nber.org/papers/w16427.pdf)
- SD values were not given in the extracted text. The fetch tool's implied estimate (mean ÷ Sharpe) is about 8.5% for developed currencies. — [NBER w16427](https://www.nber.org/papers/w16427.pdf)
- G10 decomposition (1976–2013), Daniel, Hodrick & Lu:
  - Dollar-neutral component (EQ-0$): 1.61% mean, SD 3.28%, Sharpe 0.49, skew −0.47, worst month −3.92%.
  - Dollar component (EQ-$): 2.35%, SD 3.85%, Sharpe 0.61.
  - Dynamic-dollar strategy (EQ-D$): 5.54%, SD 8.18%, Sharpe 0.68, skew −0.11, worst month −8.27%.
  
  — [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)
- Downside risk sits in the dollar-neutral piece. EQ-0$ loads on Jurek's downside-risk index (slope 0.18, t = 5.14), and its alpha falls to 0.10% (t = 0.13). EQ-D$ keeps a 5.37% alpha (t = 2.83) and a 4.52% alpha after all factors combined. — [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)

### Inferences
- In a G8 universe that includes USD, a dollar-carry leg is a natural, separately testable component: long or short USD vs the other 7 based on average foreign rate minus US rate. The literature says it carries less skew than cross-sectional carry. It is also a separate return source, roughly uncorrelated with HML carry.
- The dollar-neutral cross-section of G10 is where the crash risk sits, and in Daniel, Hodrick & Lu it earns only about 1.6% per year before costs. That is small relative to retail swap markups (see section 5).

### Gaps
- No verified out-of-sample (post-2010) Sharpe was found for the dollar carry trade.

## 3. Crash risk, drawdowns, and risk-management overlays

### Takeaway
Measured 2008 drawdowns depend heavily on construction:
- About −11% for an equal-weighted, broad, unlevered basket (Burnside et al.).
- 12–22% maximum drawdowns for G10 EQ and SPD over 1976–2013 (Daniel, Hodrick & Lu).
- About −35% for a spread-weighted G10 portfolio in 2008 (Jurek).

Volatility scaling based on carry's own volatility has support. Equity-VIX timing and fixed-delta option hedges have weak or negative evidence.

### Cited Findings
**Drawdowns**
- Burnside et al., 20-currency equal-weighted carry: cumulative payoff fell 10.7% from Jul 2008 to Feb 2009. Over the same window the US stock market fell 51.6% (Oct 2007 – Feb 2009). Worst months: −4.2% (Sep 2008), −3.9% (Aug 2008), −3.7% (Jan 2009). Their largest drawdown came outside the crisis: −8.9% in Mar 1991. — [NBER w14054](https://www.nber.org/system/files/working_papers/w14054/w14054.pdf)
- Jurek, G10: the unhedged spread-weighted carry portfolio had about a 35% peak-to-trough drawdown in 2008. — [Jurek PDF](https://www.johnhcochrane.com/s/Jurek_currency_new.pdf)
- Daniel, Hodrick & Lu, G10, 1976–2013:
  - EQ maximum drawdown 12.0% over 94 days, peak to trough. The authors say "this large drawdown was not a crash."
  - EQ second-worst drawdown 10.8% over 107 days.
  - SPD maximum drawdown 21.5% over 163 days, and each of SPD's 10 worst drawdowns lasted more than 50 days.
  - Risk-rebalancing "cuts the largest drawdown in half" for SPD.
  - Large drawdowns come from sequences of losses (time-varying autocorrelation), not single jumps.
  
  — [NBER w20433](https://www.nber.org/system/files/working_papers/w20433/w20433.pdf); [CFR 2017 PDF](https://business.columbia.edu/sites/default/files-efs/pubfiles/6378/Daniel.Hodrick.Lu.Carry%20Trade.Critical%20Finance%20Review.2017.pdf)
- Conflict: the 2008 drawdown estimates (−10.7%, about −35%, and Daniel, Hodrick & Lu's 12% and 21.5% full-sample maxima) are not comparable. They differ in currency set, weighting (equal vs spread-weighted), leverage, and base currency. The excerpts did not give calendar dates for the Daniel, Hodrick & Lu maxima.

**Option crash hedges (Jurek; Burnside et al.)**
- Crash-hedged G10 carry with 10-delta puts, 1999–2012, still earned 5.27–5.36% per year (t ≈ 2.1). The crash risk premium is 0.20–0.50% per year (<10% of the return) without option costs, or 1.3–1.6% per year (about 20–31%) with an assumed option cost. Conclusion: "crash risk premia account for at most one-third of the excess return." — [Jurek PDF](https://www.johnhcochrane.com/s/Jurek_currency_new.pdf)
- The hedged portfolios also suffered a "nearly 35%" drawdown in Fall 2008. Fixed-delta puts were struck further out-of-the-money as implied vol rose, so the hedge barely limited losses. Cross-rate-hedged versions did recover most of their shortfall during Fall 2008. — [Jurek PDF](https://www.johnhcochrane.com/s/Jurek_currency_new.pdf)
- Burnside et al., 1987–2009: an at-the-money option hedge cut the mean from 2.96% to 1.58% and the SD from 6.2% to 3.5%. Skew flipped from −0.71 to +0.72, while the Sharpe barely moved (0.476 → 0.449). — [NBER w14054](https://www.nber.org/system/files/working_papers/w14054/w14054.pdf)

**Volatility management**
- Moreira & Muir, "Volatility-Managed Portfolios" (NBER w22208; JF 2017):
  - Method: scale monthly returns by the inverse of the previous month's realized variance.
  - For the LRV carry factor (1983–2015, 360 months), volatility-managed alpha is 2.78% per year (SE 1.49), or 2.54% (SE 1.65) controlling for Fama-French factors. Beta is 0.71.
  - The text gives an appraisal ratio of 0.44, which does not quite match the table-implied ≈0.38. No Sharpe is reported for carry.
  
  — [NBER w22208](https://www.nber.org/system/files/working_papers/w22208/w22208.pdf)
- Important caveat from the same paper: timing carry with a common, mostly equity-based volatility factor turns its alpha to −1.28, insignificant. Carry's volatility behaves differently from equity volatility, so "timing this factor with a common volatility factor from (mostly) equity portfolios will work poorly." — [NBER w22208](https://www.nber.org/system/files/working_papers/w22208/w22208.pdf)
- VIX: VIX increases coincide with carry losses (weekly coefficient −0.43) but do not predict next-week losses (−0.03, insignificant). Rising VIX predicts higher carry returns 3–4 quarters later (0.53). — [NBER w14473](https://www.nber.org/papers/w14473.pdf)
- Global FX volatility innovations (contemporaneous) price carry. High-volatility-innovation periods are "times when the carry trade performs poorly." — [City Univ. repository](https://openaccess.city.ac.uk/id/eprint/3391/1/CTVOL_R3_v4_paper.pdf)

**Multi-signal optimization (Barroso & Santa-Clara)**
- "Beyond the Carry Trade," JFQA 2015, as summarized by CXO in 2012 from the 2011 working paper:
  - Data: Nov 1960 – Sep 2010, 27 developed economies.
  - Signals: carry, momentum, long-term reversal, current account, and real exchange rate.
  - Out-of-sample (Feb 1996 – Sep 2010) gross Sharpe was 1.40, vs a 0.91 full-sample carry benchmark. The fundamentals were "essentially irrelevant."
  - Returns "fade or disappear after 2005." Net growth of $1 was $11.75, vs $72.87 gross, under 0.1% round-trip costs.
  
  — [CXO Advisory summary](https://www.cxoadvisory.com/strategic-allocation/optimized-currency-trading)

### Inferences
- An equity-VIX "exit when VIX spikes" filter is poorly supported:
  - The VIX move is contemporaneous with the loss, not ahead of it.
  - Spikes predict above-average carry returns over the following quarters.
  - Moreira & Muir found equity-based volatility timing of carry fails.
  
  A rule that de-risks after a spike risks selling near the low. Scaling exposure by the carry portfolio's own trailing realized volatility (or FX volatility) has the better support.
- For a weekly system, inverse-variance scaling of the carry basket using trailing daily returns is cheap and evidence-based (Moreira & Muir, Daniel, Hodrick & Lu risk-rebalancing). It is not crash protection, though: in 2008, losses arrived as a sequence over weeks.
- Option crash hedges are not available on a retail MT4 account. Jurek shows that even professional fixed-delta hedges did not prevent about −35% in 2008.
- Barroso & Santa-Clara's "fades after 2005" is a warning that multi-signal FX optimization has decayed out of sample. It fits with the failed momentum backtest (Sharpe −0.24, 2000–2026).

### Gaps
- Bhansali's work on carry and volatility (carry as short-volatility) was not researched in this pass.
- The Daniel, Hodrick & Lu risk-rebalancing methodology and the full drawdown table with dates (Tables 22–24) were not extracted.
- No source gave a verified G10 carry drawdown for July–August 2024 or for 2020.
- No Sharpe ratio was found for volatility-managed carry alone, as opposed to alpha.

## 4. Post-2008 performance: DBV / DB G10 Currency Harvest, the zero-rate era (2009–2021), and the 2022–2026 rate divergence

### Takeaway
Out-of-sample G10 carry was poor after 2008. A Citi strategist said in May 2026 that developed-market carry "hasn't made any money" since the GFC. The main retail G10 carry ETF (DBV) was liquidated in March 2023 for lack of assets. The 2022–2026 rate divergence brought a revival funded mainly in JPY and CHF. That revival was interrupted by the August 2024 yen unwind, and Citi's G10 carry basket was up about 4% year-to-date by mid-May 2026.

### Cited Findings
**DBV (PowerShares, later Invesco, DB G10 Currency Harvest Fund)**
- DBV tracked the "Deutsche Bank G10 Currency Future Harvest Index – Excess Return." — [SEC 424B3, Jan 2023](https://www.sec.gov/Archives/edgar/data/1354730/000119312523013247/d407214d424b3.htm)
- Index construction (as described by CXO): long futures on the three highest-yielding G10 currencies and short the three lowest. DBV's first available monthly return is Sep 2006. — [CXO Advisory, May 2013](https://www.cxoadvisory.com/?p=20800)
- CXO, Sep 2006 – Apr 2013 (79 months): DBV had a "low positive average return with relatively low volatility." Adding it to a nine-asset portfolio "mostly degrades cumulative value." Its average correlation with the other assets was 0.45. — [CXO Advisory, May 2013](https://www.cxoadvisory.com/?p=20800)
- Liquidation:
  - Announced Jan 23, 2023.
  - Creations stopped after Feb 24, 2023.
  - Last trading day (Cessation Date) Mar 3, 2023, NYSE Arca.
  - Liquidating distribution on or about Mar 10, 2023.
  
  Reason given: continuing was "unreasonable and imprudent" given the fund's net assets relative to its operating expenses. — [SEC 424B3](https://www.sec.gov/Archives/edgar/data/1354730/000119312523013247/d407214d424b3.htm); [SEC POS AM, Mar 2023](https://www.sec.gov/Archives/edgar/data/1354730/000119312523077468/d477628dposam.htm)

**Zero-rate era and the 2022–2026 revival**
- Citi's Kristjan Kasikov (Reuters, May 15, 2026): "Since the global financial crisis it (a developed market carry trade) hasn't made any money, so this uptick that we have seen is unusual." Carry was unattractive "during the COVID-19 pandemic when rates were near zero globally." — [Reuters via MarketScreener](https://www.marketscreener.com/news/carry-on-trading-rate-based-g10-currency-bets-make-a-comeback-ce7f5bd2da8bf327)
- Same article: Citi's unleveraged G10 basket (long the 5 highest-rate G10 currencies, short the 5 lowest) "would have returned just over 4% so far this year" (2026 to mid-May).
  - Year-to-date moves: AUD up "almost 9%" vs USD, NOK up 10%, GBP up 1%, JPY weaker.
  - Policy rates: Australia and Norway above 4%, UK just below, Japan under 1%, Switzerland 0%.
  - 3-month EUR/USD implied vol about 5.6%, vs >9% in Apr 2025 (tariff shock) and >12% in Jun 2022.
  
  — [Reuters via MarketScreener](https://www.marketscreener.com/news/carry-on-trading-rate-based-g10-currency-bets-make-a-comeback-ce7f5bd2da8bf327)
- The same article notes investors were "burned in 2024 when a sudden yen surge in a quiet summer wiped out carry trades." — [Reuters via MarketScreener](https://www.marketscreener.com/news/carry-on-trading-rate-based-g10-currency-bets-make-a-comeback-ce7f5bd2da8bf327)

**August 2024 yen carry unwind**
- BIS Bulletin 90 (Aug 27, 2024): FX carry trades "were hit hard by the deleveraging pressures." The rough midpoint estimate of carry trade size going into the event was ¥40 trillion ($250 billion), "if anything, biased down due to data gaps." Unwinding leveraged positions amplified the reaction to weak US macro data. — [BIS Bulletin 90](https://www.bis.org/publ/bisbull90.htm)
- AMRO (Dec 2024):
  - JPY rose about 5.6% vs USD from Jul 30 to Aug 5, 2024, after rising since mid-July.
  - Triggers: the BOJ hike to 0.25% (Jul 31) and weak US payrolls (Aug 2).
  - Over Jul 30 – Aug 5, MXN fell about 3.2%, BRL about 2.5%, and ZAR about 2% (emerging-market targets, not G10).
  - Yen-denominated loans were about ¥41 trillion as of Jun 2024, up from ¥27 trillion in Mar 2021.
  
  — [AMRO Analytical Note](https://amro-asia.org/wp-content/uploads/2024/12/20241219-Analytical_Note_Carry_Trade.pdf)
- BOJ policy context: the BIS policy-rate documentation records that, from Sep 24, 2026, the BOJ guides the overnight call rate "around 1.25 percent." — [BIS CBPOL documentation](https://www.bis.org/statistics/cbpol/cbpol_doc.pdf)
- FRED's Japan 3-month interbank rate was 1.458% in Jul 2026. The Swiss 3-month interbank rate was −0.045% in Aug 2026. — [FRED JP](https://fred.stlouisfed.org/series/IR3TIB01JPM156N); [FRED CH](https://fred.stlouisfed.org/series/IR3TIB01CHM156N)

### Inferences
- Splitting a 2000–2026 backtest into regimes will likely show three phases:
  1. 2000–2008: strong but crash-prone.
  2. 2009–2021: flat to negative, with near-zero differentials across G10 and USD/EUR/JPY/CHF all near zero at times.
  3. 2022–2026: positive but with sharp unwinds (Aug 2024).
  
  Expect the full-period Sharpe to sit well below the 0.4–0.9 in-sample academic numbers. The best published practitioner evidence (Citi, DBV) suggests close to zero for 2009–about 2021.
- Since 2022, the G8 funding legs have been JPY and CHF, and USD has been a high-yielder for much of the period. The dollar-carry component would have been long USD, so for a USD-based account carry has been a USD-long, JPY/CHF-short trade with concentrated JPY crash risk (Aug 2024).
- MXN and other emerging-market currencies drove much of the 2022–2024 "carry boom" headlines. That evidence does not transfer to a G8 system.

### Gaps
- Annual G10 carry index returns for 2009–2025 (DB G10 Harvest, Citi, or similar) were not found in accessible primary sources. DBV's 2008 drawdown and annual returns were not retrieved, so its 2008 loss is not reported here.
- The DB G10 Harvest index rebalance frequency and exact methodology document were not retrieved.
- No source quantified G10-only (ex-MXN) carry returns for 2022, 2023, 2024, or 2025.
- No AQR, Man, or Robeco note with numeric post-2008 G10 carry results was retrieved in this pass.

## 5. Retail implementation: swap/rollover vs interbank forward points

### Takeaway
Retail FX carry is earned through daily rollover. Brokers base it on tom-next swap rates and adjust it by an admin fee. OANDA's published fee is 1.00% per year on major pairs, a large haircut on G10 differentials that are often 1–4%.

### Cited Findings
- OANDA (US) formula: financing = position value × funding rate × 1/365, charged on positions open at 5 p.m. ET. The funding rate is "a blend of underlying liquidity providers' tom-next swap rates, adjusted by our x% admin fee." — [OANDA financing fees](https://www.oanda.com/us-en/trading/financing-fees/)
- Long and short rates are quoted separately per instrument. — [OANDA financing fees](https://www.oanda.com/us-en/trading/financing-fees/)
- Annualized admin fees: 1.00% on most pairs (including majors), 2.00% on CZK/HUF/SAR/THB/ZAR pairs, 4.00% on TRY pairs. — [OANDA financing fees](https://www.oanda.com/us-en/trading/financing-fees/)
- Wednesday's 5 p.m. charge is typically triple (weekend settlement), and nothing is charged Saturday or Sunday. OANDA's example: long 100,000 EUR/USD at 1.15826 with a long rate of −3.00% costs −9.52 USD per day. — [OANDA financing fees](https://www.oanda.com/us-en/trading/financing-fees/)
- Bid-ask costs alone materially cut academic carry Sharpe ratios. Burnside et al.'s equally weighted carry with a USD base (1997–2008) fell from 0.306 to 0.250 once spreads were included. — [NBER w14054 rev0](https://www.nber.org/system/files/working_papers/w14054/revisions/w14054.rev0.pdf)

### Inferences
- With a 1% per year fee on each position, a pair with a 2% differential would earn roughly 1% net long and pay roughly 3% short. Low-differential G10 pairs (for example, EUR/CHF or USD/CAD at times) can carry negative net swap on both sides.
- In a 3×3 basket implemented as individual pairs, every pair pays the fee. Implementing via USD legs (fewer positions) or via the fewest crosses reduces fee drag.
- The Daniel, Hodrick & Lu dollar-neutral G10 component earned only about 1.6% per year before costs. A 1% per year retail fee could remove most of it.
- Backtests built from FRED 3-month interbank differentials overstate retail carry by roughly the broker's admin fee. They also miss tom-next basis effects. The correct cost model is the broker's actual MT4 long and short swap points per symbol, logged daily.
- MT4 demo-account swaps may not equal live-account swaps. Logging both is worthwhile before trusting demo P&L.

### Gaps
- No systematic study was found comparing retail swap rates with interbank forward points across brokers. Only OANDA's published schedule was verified.
- The MT4 broker's actual swap table (MidasFX or whichever demo broker is used) was not checked. It should be exported from the platform (Symbol → Specification → Swap long/short).

## 6. Interest-rate data needed and free sources

### Takeaway
FRED's OECD 3-month interbank series (IR3TIB01xxM156N) and the BIS central bank policy-rate dataset cover the G8. Coverage differs by country: Japan's FRED 3-month series starts only in April 2002, which matters for a backtest from 2000. Update lags also differ (UK and euro area latest Jan 2026, Japan Jul 2026, Switzerland Aug 2026, as of the fetch).

### Cited Findings
**FRED series (monthly, percent, not seasonally adjusted; source OECD Main Economic Indicators)**
- Japan IR3TIB01JPM156N: Apr 2002 – Jul 2026 (latest 1.45845%). Related Japan series:
  - IRSTCI01JPM156N (call money/interbank)
  - IR3TCD01JPM156N (3-month CD)
  - IRSTCB01JPM156N (central bank rate)
  - INTGSTJPM193N (T-bill)
  
  — [FRED JP](https://fred.stlouisfed.org/series/IR3TIB01JPM156N)
- Switzerland IR3TIB01CHM156N: Jul 1999 – Aug 2026 (latest −0.04500%). Related: IRSTCI01CHM156N, IR3TED01CHM156N. — [FRED CH](https://fred.stlouisfed.org/series/IR3TIB01CHM156N)
- United Kingdom IR3TIB01GBM156N: Jan 1957 – Jan 2026 (latest 3.71%, last updated Feb 16, 2026). Related: IR3TTS01GBM156N (3-month Treasury). — [FRED GB](https://fred.stlouisfed.org/series/IR3TIB01GBM156N)
- Euro area (19) IR3TIB01EZM156N: Jan 1994 – Jan 2026 (latest 2.02773%). Related: IRSTCI01EZM156N. — [FRED EZ](https://fred.stlouisfed.org/series/IR3TIB01EZM156N)
- The US, Canada, Australia, and New Zealand series exist on FRED: IR3TIB01USM156N, IR3TIB01CAM156N, and IR3TIB01NZM156N are listed as related series, and IR3TIB01SEM156N (Sweden) is also listed. Their date ranges were not verified. — [FRED CH](https://fred.stlouisfed.org/series/IR3TIB01CHM156N); [FRED GB](https://fred.stlouisfed.org/series/IR3TIB01GBM156N)
- None of the four FRED pages fetched shows a discontinuation notice. Each shows "Next Release Date: Not Available." — [FRED GB](https://fred.stlouisfed.org/series/IR3TIB01GBM156N)

**BIS central bank policy rates**
- More than 40 central banks, published since Sep 2017. Daily data are updated about mid-week; the monthly value is the last business day's rate. History goes back to 1945/46 for several countries. — [BIS CBPOL documentation](https://www.bis.org/statistics/cbpol/cbpol_doc.pdf)
- Policy-rate definitions and start dates:

| Country | Earliest start | Rate definitions |
|---|---|---|
| US | 1 Jul 1954 | Fed funds effective; target-rate midpoint from 19 Dec 1985 |
| Euro area | 5 Jan 1999 | Main refinancing operations (MRO) rate; deposit facility rate from 18 Sep 2024 |
| Japan | 1 Jan 1946 | Official discount rate; later call-rate guidance |
| Switzerland | 1 Jan 1946 | Discount rate; target-range midpoint 2000 – Jun 12, 2019; SNB policy rate from Jun 13, 2019 |
| UK | 1 Jan 1946 | Bank rate; repo rate 1997–2006; official bank rate from Aug 3, 2006 |
| Canada | 27 Jul 1960 | Bank rate; target overnight rate from Jun 1, 1994 |
| Australia | 7 Apr 1976 | Interbank cash rate; cash rate target from Aug 2, 1990 |
| New Zealand | Jan 1985 | Overnight cash rate; OCR from Mar 17, 1999 |
| Germany | pre-1979 | Discount rate, then Lombard rate (1979–84), then repo rate (1985–1998); discontinued Jan 1, 1999 |

  — [BIS CBPOL documentation](https://www.bis.org/statistics/cbpol/cbpol_doc.pdf)
- The BIS data portal topic page is at data.bis.org/topics/CBPOL. It was found in search but not fetched. — [BIS data portal](https://data.bis.org/topics/CBPOL)
- Academic carry studies use 3-month interbank rates (Brunnermeier, Nagel & Pedersen) or forward discounts (LRV; Menkhoff et al.), not policy rates. — [NBER w14473](https://www.nber.org/papers/w14473.pdf); [NBER w14082](https://www.nber.org/papers/w14082.pdf)

### Inferences
- For a weekly G8 backtest from 2000, the BIS daily policy-rate series is the most consistent free source. It has full G8 coverage from before 2000 (euro from Jan 1999) and daily granularity.
- FRED IR3TIB01 monthly series are closer to what the academic papers use but have coverage problems. Japan's 3-month series starts Apr 2002; fill 2000–2002 with IRSTCI01JPM156N or the BIS policy rate. The euro area starts in 1994, so Germany is needed before 1999 if the backtest ever extends earlier.
- Several series end Jan 2026, so a live system needs another current feed. Options: BIS daily, central bank sites, or the broker's own swap rates, which are what is actually paid.
- Ranking currencies on policy rates vs 3-month rates rarely changes the G8 ordering, except around expected hikes or cuts, when 3-month rates lead. That makes the 3-month rate the marginally better signal where available.
- Post-LIBOR, the OECD "interbank" label for GBP, CHF, and JPY may now reflect risk-free-rate-based or other replacement rates. The FRED pages do not say which.

### Gaps
- Date ranges for the US, Canada, Australia, and New Zealand IR3TIB01 series were not verified. Direct CSV download from FRED was blocked by the sandbox proxy.
- The underlying instrument for each country's OECD 3-month "interbank" series after the LIBOR cessation (2021–2023) was not documented on the FRED pages.
- The reason UK and euro area FRED series end in Jan 2026 while JP and CH run to Jul/Aug 2026 (update lag vs restructuring) was not determined.
