# FX Value (PPP / Real Exchange Rate) and Multi-Factor FX Combinations (Carry + Momentum + Value): Evidence on Durability and Diversification

Scope note: research notes compiled 2026-10-14 for a small weekly-rebalanced G8 currency system (USD, EUR, JPY, GBP, CHF, CAD, AUD, NZD) whose pure momentum signal backtested at Sharpe -0.24 (2000-2026, before costs). All Sharpe ratios are annualized unless marked "monthly". "In-sample" = the period the original authors studied; "post-publication / out-of-sample" is labelled explicitly. EM = emerging-market currencies are flagged wherever a result depends on them.

---

## 1. Menkhoff, Sarno, Schmeling & Schrimpf (2017) "Currency Value" (RFS): measurement, returns, Sharpe, horizon, G10 vs broad

### Takeaway
A raw value signal (5-year change in the real exchange rate) earns a Sharpe of roughly 0.44-0.51 (1976-2014, 22 USD pairs incl. EM, quarterly rebalance, no transaction costs); adjusting the real exchange rate for fundamentals (productivity, export quality, net foreign assets, output gap) raises the Sharpe to about 0.79-0.91, mostly by cutting volatility, and extends predictability from about 1 year to about 2 years. The paper does not report a developed-only (G10) result.

### Cited Findings
- Publication: Menkhoff, Sarno, Schmeling & Schrimpf, *Review of Financial Studies* 2017, vol. 30(2), pp. 416-441; working paper CEPR DP11324 (2016) — [IDEAS/RePEc](https://ideas.repec.org/p/cpr/ceprdp/11324.html)
- Abstract claim: "real exchange rates have predictive power for the cross-section of currency excess returns"; adjusting real exchange rates for productivity, export quality, net foreign assets and output gaps better isolates the currency risk premium; the adjusted value measure's predictive information is distinct from carry and momentum — [IDEAS/RePEc](https://ideas.repec.org/p/cpr/ceprdp/11324.html)
- Data: quarterly, 1970Q1-2014Q1; returns analysis 1976Q1-2014Q1; 23 economies (advanced and emerging), i.e., 22 USD-quoted exchange rates. No separate developed-only results; a leave-one-currency-out check (Table A.III) gives similar results — [Currency Value, CEPR/City open-access version](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Raw value signal = 5-year log change in the real exchange rate, Δ(5y)q. Adjusted value = residual from quarterly cross-sectional regressions of Δ(5y)q on real GDP per capita (Balassa-Samuelson), export quality, net foreign assets/GDP and the output gap; "expected fundamentals" proxied by EWMA, country VAR and panel VAR — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Portfolio construction: quartile portfolios (P1-P4), HML = long P4/short P1, plus rank-weighted and linear-weighted long-short versions; rebalanced quarterly — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Raw value results (Table 4, annualized excess returns): HML 3.89% mean, 8.93% vol, Sharpe 0.44; rank 3.65% / 7.27% / 0.50; linear 2.32% / 4.57% / 0.51 — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Fundamentals-adjusted value (Table 5, panel VAR): rank 4.67% / 5.19% / Sharpe 0.90; linear 2.43% / 2.68% / Sharpe 0.91. Across the four expectation methods adjusted Sharpe ≈ 0.79-0.91 vs ≈ 0.53-0.60 for the raw signal in the same table (note: this raw range differs from Table 4's 0.44-0.51; likely different portfolio weighting/sample per panel). Gains come mainly from lower volatility, not higher mean returns — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Horizon/persistence: predictive slope on Δ(5y)q is 0.027 (t = 2.89) baseline, 0.039 (t = 4.00) with all fundamentals (~40% larger); predictability lasts about two years with fundamentals controls vs about one year without — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Turnover (quarterly): adjusted panel-VAR value ≈ 21%, standard value ≈ 18%, carry ≈ 10%, momentum ≈ 60%. Transaction costs are NOT modelled — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Implementation-lag robustness (two-quarter lag, Table A.V): adjusted linear Sharpe falls to ≈ 0.48-0.61; raw linear ≈ 0.31 — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Spanning: adjusted-value alphas ≈ 2.1-4.7% p.a. (information ratios 0.53-0.91) after controlling for other currency factors; adjusted value gets a larger tangency-portfolio weight than carry. The authors describe the expectation proxies as recursively built (1970-1975 initialization), i.e., "out-of-sample" in the signal-construction sense, though the 1976-2014 period is their study sample — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)

### Inferences
- Value is a slow signal (quarterly rebalance, ~18-21% quarterly turnover, 1-2 year predictive horizon). A weekly rebalance adds trading without adding signal; monthly or quarterly is consistent with the evidence.
- The fundamentals adjustment is mostly a volatility reducer. For a retail G8 implementation, the raw 5-year real-exchange-rate change (Sharpe ~0.45-0.5 gross in a 22-currency incl.-EM universe) is the realistic baseline; the 0.8-0.9 adjusted figure requires productivity / export-quality / NFA data and is unverified post-2014.
- Because the sample includes EM currencies and no G10-only split is reported, G8 results should be expected to be weaker/noisier (fewer currencies in the cross-section).

### Gaps
- No developed-only (G10) result, no transaction-cost-adjusted Sharpe, and no post-2014 performance are reported in the version reviewed.
- Correlations of the value factor with carry, momentum and the dollar factor were not reported in the text extracted (only spanning alphas).

---

## 2. Asness, Moskowitz & Pedersen (2013) "Value and Momentum Everywhere": currency value measure, Sharpe of value/momentum/50-50 combo, value-momentum correlation

### Takeaway
AMP use 10 developed currencies (1979-2011), value = negative 5-year change in the (real/interest-adjusted) exchange rate, momentum = 12-1 month return. The only currency-specific numbers I could verify are from the 2008 NBER draft appendix (value measure lagged an extra year, 1980-2008): value Sharpe 0.57, momentum 0.45, 50/50 combo 0.56, value-momentum correlation -0.02. Across non-stock asset classes the average value-momentum correlation is about -0.54; the all-asset value+momentum combo has Sharpe 1.42 (in-sample, gross).

### Cited Findings
- Currency universe: 10 currencies — Australia, Canada, Germany (spliced with euro), Japan, New Zealand, Norway, Sweden, Switzerland, UK, US; sample January 1979 to July 2011; at least 7 currencies available at any time, all 10 after 1980 — [AMP 2013, published-version PDF](https://www.johnhcochrane.com/s/Value-and-Momentum-Everywhere.pdf)
- Currency value = negative of the 5-year change in the exchange rate adjusted for interest (local 3-month LIBOR); described as a 5-year deviation from uncovered interest parity, equivalent to a 5-year change in purchasing power parity. Momentum = past 12-month return skipping the most recent month — [AMP 2013 PDF](https://www.johnhcochrane.com/s/Value-and-Momentum-Everywhere.pdf)
- All-asset-class (incl. stocks) 50/50 value-momentum combination: Sharpe 1.42 (gross, in-sample) — [AMP 2013 PDF](https://www.johnhcochrane.com/s/Value-and-Momentum-Everywhere.pdf)
- Average value-momentum correlation across non-stock asset classes ≈ -0.54 — [AMP 2013 PDF](https://www.johnhcochrane.com/s/Value-and-Momentum-Everywhere.pdf)
- 2008 NBER Summer Institute draft, Table A2 (value lagged an extra year, constant ex-ante volatility scaling), currency selection, 08/1980-02/2008: Value Sharpe 0.57 (t = 3.02), Momentum 0.45 (t = 2.35), 50/50 Combo 0.56 (t = 2.95); Cor(Value, Momentum) = -0.02 — [AMP NBER 2008 draft](https://conference.nber.org/confer/2008/si2008/AP/pedersen.pdf)
- AQR's follow-on "Investing with Style" (JOIM 2015), 1990-June 2013, 16 currencies (includes EM: Brazil, Korea, Mexico, Russia, Singapore, Turkey from April 1997), gross of costs: currency value Sharpe 0.28, momentum 0.20, carry 0.55. Value defined there as the real exchange rate level (nominal rate / price-level ratio, Rogoff 1996 style); momentum = 12-month return without skipping a month; carry = 3-month local cash rate — [Asness, Ilmanen, Israel, Moskowitz, "Investing with Style," JOIM 2015](https://www.hhs.se/contentassets/64dc92c6b6354b36acee1543a5d8bae0/investing-with-style-joim-2015-finalpublished.pdf)
- Same paper: the 7-asset-class, 4-style composite has a gross simulated Sharpe of 1.74 with 10% vol and -0.12 correlation to equities; authors caution it is likely too optimistic in practice — [JOIM 2015](https://www.hhs.se/contentassets/64dc92c6b6354b36acee1543a5d8bae0/investing-with-style-joim-2015-finalpublished.pdf)

### Inferences
- The famous strongly negative value-momentum correlation (≈ -0.5) is a cross-asset average; in currencies specifically the verified draft figure is near zero (-0.02). The diversification payoff of value+momentum in G10 FX is therefore smaller than in equities.
- Currency momentum and value each delivered Sharpe ~0.2-0.6 depending on sample and definition; both are much weaker in the 1990-2013 AQR sample (0.20 / 0.28) than in the 1980-2008 draft (0.45 / 0.57).

### Gaps
- Could not extract AMP 2013 published Table I/II currency-specific mean, volatility, Sharpe and value-momentum correlation (table values not machine-readable in the PDF fetched). Report-writer should not quote specific published-version currency Sharpe numbers from these notes.

---

## 3. Kroencke, Schindler & Schrimpf (2014) "International Diversification Benefits with FX Investment Styles" (Review of Finance)

### Takeaway
Over 1985-2009, carry, momentum and value each earned positive returns in both a 24-currency broad set and a 9-currency G10 set; style returns are nearly uncorrelated with each other (G10: carry-mom 0.07, carry-value -0.01, mom-value -0.09). Adding FX styles to an international stock/bond portfolio significantly raises Sharpe even after transaction costs, with the 3-style combination giving the largest improvement. G10 gains are smaller and statistically weaker than the broad (EM-inclusive) set.

### Cited Findings
- Sample: January 1985 - December 2009 (300 months). Broad set 24 currencies (incl. EM: Brazil, Hungary, India, Indonesia, Mexico, Poland, Russia, Singapore, South Africa, South Korea, Taiwan); G10 subset = 9 currencies (AUD, CAD, DEM/EUR, JPY, NZD, NOK, SEK, CHF, GBP) — [Kroencke, Schindler & Schrimpf, CREATES WP 2011-10](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Construction: monthly rebalancing; long/short the top/bottom 2/9 quantile, equal-weighted legs. Carry = forward discount; momentum = past 3-month return (1- and 12-month as robustness); value = long currencies whose real exchange rate fell most over the past 5 years (cumulative 5-year change in log RER using CPI and a Heston-Summers-Aten PPP level for 2000) — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Gross returns, broad set: carry 9.1% p.a. (vol 10.1%, monthly skew -0.84, monthly Sharpe 0.26); momentum 5.9% (monthly SR 0.17); value 4.7% (monthly SR 0.16, skew -0.09) — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Gross returns, G10 set: carry 6.8% p.a. (monthly SR 0.18, skew -0.90); momentum 4.8% (monthly SR 0.13); value 4.8% (monthly SR 0.13, skew +0.15) — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Transaction costs (quoted bid-ask, deemed conservative): carry loses ≈ 0.6% p.a. (to ≈ 8.5%), momentum ≈ 1.4% p.a. (to ≈ 4.4%), value a small amount (to ≈ 4.3%). Net monthly Sharpe (broad): carry 0.24, momentum 0.13, value 0.15 — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Style correlations, broad (net): carry-momentum 0.08, carry-value 0.13, momentum-value -0.12. G10: carry-momentum 0.07, carry-value -0.01, momentum-value -0.09 — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Mean-variance spanning (net of costs, monthly Sharpe): benchmark international stocks 0.29 (unhedged) / 0.33 (hedged). Broad set added to hedged benchmark: carry 0.41, value 0.36, momentum 0.35, all three 0.44. G10 set added to hedged benchmark: carry 0.36, momentum 0.35, value 0.35, all three 0.39 — significance at 10% in all G10 cases except the HAC-robust value test — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Out-of-sample (120-month rolling window): Sharpe gains persist for naive and optimized rules, largest for carry, then momentum and value (exact Table 7 values not extracted) — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf)
- Journal version: Review of Finance (2014) — [Review of Finance listing](https://revfin.org/?p=712); won the BlackRock Research Award 2011 — [ZEW](https://zew.de/AM4046-1)

### Inferences
- Annualizing the monthly Sharpe ratios (× √12, my conversion): G10 gross carry ≈ 0.62, momentum ≈ 0.45, value ≈ 0.45; broad net carry ≈ 0.83, momentum ≈ 0.45, value ≈ 0.52. Momentum is the most cost-sensitive style (≈ 1.4% p.a. drag at monthly rebalance; weekly would be worse).
- Pairwise correlations near zero across all three styles in G10 mean an equal-weight combo should have volatility roughly 1/√3 of a single style, roughly doubling Sharpe if each style has a similar standalone Sharpe — consistent with the practitioner combo results in Section 6.
- Value has positive skew in G10 (+0.15) vs carry's strong negative skew (-0.90): value is a natural hedge for carry crashes.

### Gaps
- Published-version (Review of Finance 2014) numbers may differ slightly from the 2011 working paper used here; out-of-sample Table 7 values not extracted.

---

## 4. Barroso & Santa-Clara (2015) "Beyond the Carry Trade: Optimal Currency Portfolios" (JFQA)

### Takeaway
In a parametric portfolio over up to 27 developed currencies (1960-2010), carry (forward discount), momentum (3-month) and long-term reversal (5-year real return reversal, i.e., a value-type signal) all add value, while the real exchange rate level and current account do not. The out-of-sample (1996-2010) optimal portfolio reported a gross Sharpe of 1.40, but returns faded after 2005, and costs and data-snooping are material caveats.

### Cited Findings
- Abstract: carry, momentum and reversal contribute to portfolio performance; the real exchange rate and current account do not; the optimal portfolio beats the carry trade in a 16-year out-of-sample test; adding currencies raises diversified-portfolio Sharpe by "0.5 on average" and reduces crash risk; the authors interpret currency returns as an anomaly gradually being corrected as hedge fund capital grows — [Exeter repository, JFQA 2015](https://ore.exeter.ac.uk/repository/handle/10871/14068)
- Publication: *Journal of Financial and Quantitative Analysis* 50(5), 2015, pp. 1037-1056 — [IDEAS/RePEc](https://ideas.repec.org/a/cup/jfinqa/v50y2015i05p1037-1056_00.html)
- Data: November 1960-September 2010, 27 developed economies, 7,197 monthly currency returns, 13-21 currencies per year; out-of-sample February 1996-September 2010 with annual re-estimation after 240 months — [CXO Advisory summary](https://www.cxoadvisory.com/strategic-allocation/optimized-currency-trading)
- Signals: forward discount (contributes most), momentum = normalized last-3-month returns, long-term reversal = normalized inverse real currency returns over the previous five years excluding the latest three months; current account and real exchange rate "essentially irrelevant" — [CXO Advisory](https://www.cxoadvisory.com/strategic-allocation/optimized-currency-trading)
- Sharpe (gross, annual): benchmark carry trade (full sample, as reported by CXO) 0.91; U.S. stocks 0.41; optimal currency portfolio out-of-sample 1.40; stock+bond portfolio 0.39 rising to 1.47 when the optimal currency strategy is added (out-of-sample) — [CXO Advisory](https://www.cxoadvisory.com/strategic-allocation/optimized-currency-trading)
- With 0.1% round-trip friction: outperforms benchmark carry by 8.7% p.a. on average (leveraged to U.S.-stock volatility); returns fade or disappear after 2005 — [CXO Advisory](https://www.cxoadvisory.com/strategic-allocation/optimized-currency-trading)

### Inferences
- The "value" that works here is the 5-year real-return reversal (the same family as AMP / KSS / Menkhoff's Δ(5y)q), not the PPP level. This supports using a change-in-real-exchange-rate signal rather than a static PPP-level gap for a small G8 system.
- The 1.40 out-of-sample Sharpe is leveraged, optimized, gross, and pre-2010; the CXO note that returns faded after 2005 makes it the least reliable guide to current performance among the papers reviewed.

### Gaps
- Exact net-of-cost Sharpe and in-sample optimal Sharpe not available from the sources fetched; full JFQA text not accessed. The 0.91 "full sample" carry Sharpe is a secondary-source figure.

---

## 5. Jordà & Taylor (2012) "The Carry Trade and Fundamentals: Nothing to Fear but FEER Itself"

### Takeaway
Conditioning G10 carry on the deviation of the real exchange rate from its long-run mean (a PPP-based "FEER") plus momentum turned a naive carry Sharpe of 0.59 with -1.9 monthly skew into ~1.27 with positive skew in-sample (1987-2008, 9 currencies vs USD); out-of-sample (2004-2008, only 5 years) the conditional pooled strategy had Sharpe 0.92 vs -1.01 for naive carry. The DB index combining carry, momentum and valuation was roughly flat in 2008 while naive carry lost ~30%.

### Cited Findings
- Abstract: naive carry has low Sharpe and negative skew; "The critical conditioning variable, we argue, is the fundamental equilibrium exchange rate (FEER)"; once FEER is incorporated "negative skewness is purged" and VIX is uncorrelated with returns; the sophisticated strategy's Sharpe is "very high," suggesting inefficiency — [NBER WP 15518](https://www.nber.org/papers/w15518)
- Published: *Journal of International Economics* 88(1), 2012, pp. 74-90 — [IDEAS/RePEc](https://ideas.repec.org:443/a/eee/inecon/v88y2012i1p74-90.html)
- Data: monthly, January 1986-December 2008; in-sample tables 1987-2008, out-of-sample 2004-2008 (recursive); 9 currencies vs USD: AUD, CAD, DEM, JPY, NOK, NZD, SEK, CHF, GBP (all G10) — [NBER WP 15518 PDF](https://www.nber.org/papers/w15518.pdf)
- FEER proxied by the long-run mean of the log real exchange rate (weak PPP); estimated reversion ≈ 2-3% per month, half-life ≈ 36 months; out-of-sample FEER allowed to drift (productivity effects) — [NBER PDF](https://www.nber.org/papers/w15518.pdf)
- Naive equal-weight carry (Table 6): Sharpe 0.59, monthly skew ≈ -1.9. Conditional (TECM, carry + FEER + momentum) equal-weight: Sharpe 1.27, skew ≈ +1.07, mean 57 bp/month. Pooled in-sample (Table 11): Sharpe 2.42, skew 0.34. Pooled out-of-sample 2004-2008: conditional Sharpe 0.92 (skew 0.64) vs naive -1.01 (skew -1.00) — [NBER PDF](https://www.nber.org/papers/w15518.pdf)
- 2008: the naive Deutsche Bank carry index fell ≈ 10% in Q3 2008 and a further ≈ 20% in October (erasing ≈ 4.5 years of gains); the augmented carry+momentum+valuation index was roughly flat in 2008 — [NBER PDF](https://www.nber.org/papers/w15518.pdf)
- Follow-on: "Dodging the steamroller: Fundamentals versus the carry trade" (J. Int. Financial Markets, Institutions & Money 42, 2016) — [IDEAS/RePEc](https://ideas.repec.org/a/eee/intfin/v42y2016icp115-131.html)

### Inferences
- The strongest G10-only evidence for "value improves carry" is crash protection: value/FEER conditioning mainly removes the left tail (skew from -1.9 to positive). This is the most relevant mechanism for a small account that cannot survive a -30% drawdown.
- The out-of-sample window (2004-2008) is short and includes the 2008 carry crash, which flatters a conditioning strategy; the 2.42 in-sample pooled Sharpe should be treated as overfit.

### Gaps
- No post-2008 out-of-sample evidence from the authors was found in this research pass.

---

## 6. Practitioner evidence: DBCR and sub-indices, AQR, Russell, Simplify; documented 2010-2026 performance of FX style indices

### Takeaway
Practitioner indices confirm the academic pattern before 2010 (DBCR+ 2000-2010 Sharpe 1.11 from combining carry 0.86, valuation 0.57, momentum 0.24) but show weak post-2010 results: a G10 carry index earned ~0% p.a. over the 10 years to March 2020, and Russell's carry/value/trend backtest (1999-2024) shows low single-factor returns (2.7-4.0% p.a.) with the combination's return/vol (~0.9) far above any single factor (~0.4-0.5). AQR's century-long data show currency value held up post-publication (Sharpe 0.69 vs 0.72 original) while currency momentum decayed (0.40 to 0.08).

### Cited Findings
**Deutsche Bank Currency Returns (DBCR / DBCR+)**
- DBCR (original): equal one-third weights to Carry (long 3 highest-yielding / short 3 lowest-yielding G10 currencies on 3-month rates, reviewed quarterly), Momentum (long 3 / short 3 by 12-month spot return vs USD) and Valuation (long 3 most undervalued / short 3 most overvalued by PPP). GBP-hedged DBCR 2000-2010: 8.2% annualized return, 5.5% volatility — [DWS/db x-trackers Currency Returns newsletter, 2010](https://etf.dws.com/en-gb/AssetDownload/Index/dd4c3935-e9a9-4b80-ab2f-350acc851cf3/Newsletter-Currency-Returns.pdf)
- DBCR+ (2010 SEC filing): one-third each Balanced Currency Harvest (carry; quarterly; 2 G10 + 3 EM currencies per side, i.e., EM-dependent), Momentum (monthly; 12-month spot return; 3 long / 3 short) and Valuation (quarterly; 3-month average spot ÷ latest OECD PPP; 3 long / 3 short); implemented with forwards — [SEC FWP, DBCR+ 2010](https://sec.gov/Archives/edgar/data/1159508/000095010310002326/dp18772_fwp-dbcrplus.htm)
- Live dates: Carry live from December 2005; Momentum and Valuation from March 2007; DBCR+ from February 2008; earlier data simulated — [SEC FWP](https://sec.gov/Archives/edgar/data/1159508/000095010310002326/dp18772_fwp-dbcrplus.htm)
- January 2000-June 2010 (excess returns, mostly simulated): DBCR+ 6.27% return / 5.65% vol / Sharpe 1.11 / max DD -9.2%; Carry 10.09% / 11.75% / 0.86 / -28.2%; Momentum 2.67% / 11.11% / 0.24 / -21.5%; Valuation 4.89% / 8.57% / 0.57 / -15.1%. Live DBCR+ Feb 2008-June 2010: 4.71% p.a., Sharpe 0.86 — [SEC FWP](https://sec.gov/Archives/edgar/data/1159508/000095010310002326/dp18772_fwp-dbcrplus.htm)
- Annual returns showing diversification: 2008 Carry -23.35%, Momentum +23.29%, Valuation +12.31%, DBCR+ +3.80%; 2009 Carry +24.13%, Momentum -13.58%, Valuation +10.20%, DBCR+ +6.52% — [SEC FWP](https://sec.gov/Archives/edgar/data/1159508/000095010310002326/dp18772_fwp-dbcrplus.htm)
- Post-2010 G10 carry (DB G10 Currency Future Harvest Index, the index behind Invesco DBV; quarterly rebalance; up to 2:1 notional leverage): index annual returns 2010 +1.67%, 2011 +1.18%, 2012 +10.39%, 2013 -1.98%, 2014 +0.92%, 2015 -7.63%, 2016 +7.60%, 2017 -4.97%, 2018 -0.44%, 2019 +3.54%; annualized to 31 Mar 2020: 1y -8.11%, 3y -3.88%, 5y -1.73%, 10y +0.02% — [SEC FWP, Invesco DB G10 Currency Harvest Fund, 2020](https://www.sec.gov/Archives/edgar/data/1354730/000119312520124811/d903986dfwp.htm)

**AQR — century of evidence (Ilmanen, Israel, Moskowitz et al., JOIM 2021)**
- 20 developed-market currencies, data from August 1971; factors start Feb/Apr 1974. Full-sample: Value 3.2% mean / 5.3% vol / Sharpe 0.60 (t 4.10); Momentum 1.1% / 6.7% / 0.16 (t 1.08); Carry 2.8% / 6.6% / 0.42 (t 2.90); Multifactor 2.3% / 3.8% / 0.62 (t 4.25). Currency value measured as deviation from PPP using Penn World Tables, OECD data and inflation indices — [AQR, "How Do Factor Premia Vary Over Time? A Century of Evidence," JOIM](https://www.aqr.com:443/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf?sc_lang=en)
- Original-study sample vs post-publication Sharpe (Table 2, vol-normalized; column mapping read as Original / Post — verify against table): Value 0.72 → 0.69; Momentum 0.40 → 0.08; Carry 0.33 → 0.51; Multifactor 0.97 → 0.63. Text states currency value's post-sample performance is as large as the original and carry's post-sample exceeds its original — [AQR JOIM PDF](https://www.aqr.com:443/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf?sc_lang=en)
- AQR dataset of these monthly factor returns is published — [AQR Century of Factor Premia dataset](https://www.aqr.com/Insights/Datasets/Century-of-Factor-Premia-Monthly)

**Russell Investments — ARCS (carry + value + trend), backtest 30 Nov 1999-31 Mar 2024, USD base**
- Annualized return / risk: Carry 4.0% / 7.7%; Value 2.7% / 6.7%; Trend 3.3% / 6.8%; ARCS combined 3.4% / 3.7%. Max drawdown: Carry -28.7%, Value -16.5%, Trend -13.4%, ARCS -5.6%. Worst 1-year: Carry -23.5%, Value -14.7%, Trend -12.7%, ARCS -2.9% — [Russell Investments ARCS research update 2024](https://russellinvestments.com/-/media/files/emea/uk/institutional/insights/emea-arcs-research-paper-update-2024.pdf)
- ARCS return-to-volatility 0.90 (text) / 0.92 (Exhibit 10); factor correlations: Carry-Trend -0.06, Carry-Value -0.09, Trend-Value -0.12; Carry correlation with equities/credit/hedge funds ≈ 0.46-0.52, Trend and Value ≈ zero or negative; ARCS vs US equities 0.19 — [Russell 2024](https://russellinvestments.com/-/media/files/emea/uk/institutional/insights/emea-arcs-research-paper-update-2024.pdf)
- Recent value weakness (to 31 Mar 2024): Value 1y -2.5%, 3y -2.4% p.a., 5y -0.3% p.a.; Carry 1y +8.1%, 5y +2.2% p.a.; Trend 5y +1.8% p.a.; ARCS 5y +1.4% p.a. Value based on PPP (data source not named); results are model-based/hypothetical — [Russell 2024](https://russellinvestments.com/-/media/files/emea/uk/institutional/insights/emea-arcs-research-paper-update-2024.pdf)
- Russell publishes Conscious Currency indices (carry/value/trend) with ground rules — [LSEG Russell Conscious Currency ground rules](https://www.lseg.com/content/dam/ftse-russell/en_us/documents/ground-rules/russell-conscious-currency-index-series-ground-rules.pdf)

**Other practitioner / recent academic**
- Simplify (Feb 2025): carry has generated the largest total return since 2005 but with drawdowns in 2008, 2015 and 2020; value gains offset carry shocks and carry and value "frequently move in opposite directions"; trend "has not shown effectiveness in producing consistent long-term returns" (profitable around the post-Covid USD rally). Value uses deviations from relative PPP and effective exchange rates. No numbers given — [Simplify, "Harvesting Foreign Exchange Risk Premia"](https://simplify.us/sites/default/files/fund-insights/2025-02/Simplify-FI-FOXY-Harvesting-Foreign-Exchange-Risk-Premia.pdf)
- Fan, Paseka, Qi & Zhang (2022): carry trade performance declined after the 2008 GFC, mainly due to "the disappearance of the downside risk in the post-crisis carry trade portfolio" (not under-diversification or lower crash risk) — [IDEAS/RePEc, JIFMIM 2022](https://ideas.repec.org/a/eee/intfin/v76y2022ics1042443121001670.html)

### Inferences
- Post-2010, all single G10 FX styles have been weak (G10 carry ≈ 0% p.a. over 2010-2020; currency momentum post-publication Sharpe ≈ 0.08; value negative 2019-2024 in Russell's backtest). The durable element is the combination: near-zero or negative cross-correlations (≈ -0.12 to +0.13 in every source) cut volatility and drawdown far more than return.
- 2008-2009 is the clearest live example: carry and momentum swung ±23% in opposite directions, valuation was positive both years, and the blend was positive both years.
- The user's -0.24 Sharpe for G8 momentum (2000-2026) is consistent with this evidence: currency momentum is the weakest and least durable of the three styles in developed currencies.

### Gaps
- No public DBCR/DBCR+ year-by-year performance after mid-2010 was found (db x-trackers Currency Returns ETF history not retrieved); no Robeco, Pictet or Record Currency Management FX value/carry performance numbers found in this pass.
- AQR's decade-by-decade currency factor Sharpe ratios (2010s) are only in a chart and could not be extracted; the AQR dataset link above would allow direct computation.

---

## 7. Dollar factor and dollar-based strategies (Lustig, Roussanov & Verdelhan 2014; Verdelhan 2018)

### Takeaway
The "dollar carry" trade — long all foreign currencies vs USD when the average foreign short rate exceeds the US rate, short otherwise — earned a net Sharpe of 0.66 in developed currencies (1983-2010), about double cross-sectional HML carry in developed markets (~0.3), with essentially zero unconditional correlation to HML carry and equities. Verdelhan (2018) shows a dollar factor and a carry factor jointly explain 18-80% of monthly bilateral exchange rate variation.

### Cited Findings
- Dollar carry definition: long all foreign currencies when the average foreign interest rate across developed countries exceeds the US short rate, short all foreign currencies otherwise; sample November 1983-June 2010, end-of-month — [Lustig, Roussanov & Verdelhan, "Countercyclical Currency Risk Premia" (MIT open access)](https://dspace.mit.edu/bitstream/1721.1/114867/1/Verdelhan_Countercyclical.pdf)
- After bid-ask costs: developed-country dollar carry ≈ 5.60% p.a., Sharpe 0.66; all-country ≈ 4.28% p.a., Sharpe 0.56. HML carry ≈ 3% (developed, Sharpe ≈ 0.3) and ≈ 4.4% (all, Sharpe ≈ 0.5); country-level FX carry ≈ 0.5% p.a., Sharpe near zero. Dollar carry has "essentially zero correlation (unconditionally)" with HML carry and the stock market — [LRV, MIT PDF](https://dspace.mit.edu/bitstream/1721.1/114867/1/Verdelhan_Countercyclical.pdf)
- Verdelhan (2018, Journal of Finance): two high-minus-low factors (dollar and carry) explain 18% to 80% of monthly bilateral exchange rate movements; a dollar-beta slope factor (long high-dollar-beta, short low-beta currencies) is orthogonal to the HML carry factor — [MIT DSpace, Verdelhan 2018](https://dspace.mit.edu/handle/1721.1/122354)

### Inferences
- For a G8 system quoted against USD, much of each pair's return is a common dollar component. A long-short (dollar-neutral) cross-sectional design isolates carry/value/momentum; a net-long or net-short USD tilt is a separate bet (the dollar factor) with its own evidence. Mixing the two unintentionally can dominate results.

### Gaps
- No post-2010 out-of-sample performance of the dollar carry strategy was found in this pass.

---

## 8. Data requirements for FX value: PPP / real effective exchange rates — free sources, frequency, history

### Takeaway
A free, monthly, long-history value input is available: BIS real effective exchange rates on FRED (narrow index monthly from January 1964, broad from January 1994, updated to July 2026). Annual PPP levels are available from the World Bank WDI (with OECD/Eurostat-supplied figures for 47 economies). The FRED "Purchasing Power Parity over GDP" series (PPPTTL…) are stale Penn World Table 7.1 data ending in 2010 and should not be used for a live system.

### Cited Findings
- BIS Real Narrow Effective Exchange Rate for US (FRED RNUSBIS): monthly, index 2020=100, source BIS, first observation 1964-01, last 2026-07 — [FRED RNUSBIS](https://fred.stlouisfed.org/data/RNUSBIS); equivalent series exist for the UK (RNGBBIS) — [FRED RNGBBIS](https://fred.stlouisfed.org/data/RNGBBIS) — and the euro area (RNXMBIS) — [FRED RNXMBIS](https://fred.stlouisfed.org/data/RNXMBIS)
- BIS Real Broad Effective Exchange Rate for US (FRED RBUSBIS): monthly, 2020=100, first observation 1994-01, last 2026-07 — [FRED RBUSBIS](https://fred.stlouisfed.org/data/RBUSBIS)
- FRED "Purchasing Power Parity over GDP" (e.g., PPPTTLUSA618NUPN): annual, source University of Pennsylvania Penn World Table 7.1, 1950-2010, last updated 31 Aug 2012, no next release — [FRED PPPTTLUSA618NUPN](https://fred.stlouisfed.org/series/PPPTTLUSA618NUPN)
- World Bank WDI "PPP conversion factor, GDP (LCU per international $)" (PA.NUS.PPP): for 47 high/upper-middle-income economies, figures provided by Eurostat and the OECD; others extrapolated from ICP benchmarks; CSV/API, CC-BY-4.0, mirror last updated 18 Feb 2026 — [DataHub WDI PA.NUS.PPP](https://datahub.io/world-development-indicators/pa.nus.ppp)
- Practitioner/academic usage: DBCR+ Valuation = 3-month average spot ÷ latest OECD PPP — [SEC FWP](https://sec.gov/Archives/edgar/data/1159508/000095010310002326/dp18772_fwp-dbcrplus.htm); AQR value = PPP deviations from Penn World Tables + OECD + inflation indices — [AQR JOIM](https://www.aqr.com:443/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf?sc_lang=en); KSS value = 5-year change in log RER from CPI with a 2000 PPP anchor — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf); Menkhoff et al. use quarterly data from 1970Q1 — [City open-access PDF](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- OECD publishes PPP key tables (annual) — [OECD iLibrary PPP for GDP key table](https://www.oecd-ilibrary.org/economics/purchasing-power-parities-for-gdp-2011_2074384x-2011-table11)

### Inferences
- Simplest robust G8 value signal from free data: the 5-year (60-month) change in each currency's bilateral real exchange rate vs USD = nominal spot change minus the CPI inflation differential (monthly CPI from FRED/OECD), ranked cross-sectionally — this matches the AMP / KSS / Menkhoff "Δ(5y)q" family and needs no PPP level. An alternative is the 5-year change in each currency's BIS real narrow EER (monthly since 1964), which measures value against a trade-weighted basket rather than vs USD.
- A PPP-level signal (DB-style spot ÷ OECD PPP) needs only annual PPP data, but Barroso & Santa-Clara found the RER level "essentially irrelevant" while the 5-year reversal mattered.
- CPI releases lag 2-6 weeks and PPP benchmarks are annual and revised; a backtest must lag inputs (Menkhoff's two-quarter lag test cut raw linear Sharpe to ≈ 0.31) to avoid look-ahead bias.

### Gaps
- IMF (IFS) REER access, frequency and history were not verified in this pass. BIS EER release lag and revision policy not verified. OECD PPP direct-API details (dataset codes) not verified.

---

## 9. Synthesis: which FX signals or combinations have the best long-term G10 evidence (durability and diversification)?

### Takeaway
Across every source, the most durable G10 result is an equal-risk combination of carry and value (with or without a small momentum/trend sleeve): the styles are nearly uncorrelated (-0.12 to +0.13), value hedges carry crashes, and combinations roughly halve volatility and drawdown. Value is the single style with the best post-publication durability (AQR post-sample Sharpe 0.69); momentum is the weakest and least durable (post-sample 0.08). Realistic post-2010 expectations for a G10 combination are modest (≈ 3-4% p.a. at ≈ 4% vol in Russell's backtest), not the pre-2008 Sharpe 1+ figures.

### Cited Findings
- Long-run G10/DM Sharpe ranking (AQR, 1974-2010s, 20 DM currencies): value 0.60 > carry 0.42 > momentum 0.16; multifactor 0.62 at 3.8% vol — [AQR JOIM](https://www.aqr.com:443/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf?sc_lang=en)
- Post-publication durability: value 0.69, carry 0.51, momentum 0.08 (vs original 0.72 / 0.33 / 0.40) — [AQR JOIM](https://www.aqr.com:443/-/media/AQR/Documents/Journal-Articles/JOIM_How-Do-Factor-Premia-Vary-Over-Time.pdf?sc_lang=en)
- Style correlations: KSS G10 (1985-2009) carry-mom 0.07, carry-value -0.01, mom-value -0.09 — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf); Russell (1999-2024) carry-trend -0.06, carry-value -0.09, trend-value -0.12 — [Russell 2024](https://russellinvestments.com/-/media/files/emea/uk/institutional/insights/emea-arcs-research-paper-update-2024.pdf); AMP draft (1980-2008) value-momentum -0.02 — [AMP NBER 2008](https://conference.nber.org/confer/2008/si2008/AP/pedersen.pdf)
- Combination effect: DBCR+ 2000-2010 Sharpe 1.11 vs components 0.86 / 0.57 / 0.24 — [SEC FWP](https://sec.gov/Archives/edgar/data/1159508/000095010310002326/dp18772_fwp-dbcrplus.htm); Russell ARCS return/vol ≈ 0.90 and max DD -5.6% vs single-factor DD -13% to -29% — [Russell 2024](https://russellinvestments.com/-/media/files/emea/uk/institutional/insights/emea-arcs-research-paper-update-2024.pdf)
- Value-conditioned carry removes negative skew (G10, 1987-2008): Sharpe 0.59 → 1.27, skew -1.9 → +1.07 — [Jordà & Taylor NBER PDF](https://www.nber.org/papers/w15518.pdf)
- Cost sensitivity: momentum loses ≈ 1.4% p.a. to costs vs ≈ 0.6% carry and small for value (monthly rebalancing) — [CREATES WP](https://repec.econ.au.dk/repec/creates/rp/11/rp11_10.pdf); quarterly turnover momentum ≈ 60%, value ≈ 18-21%, carry ≈ 10% — [Menkhoff et al.](https://openaccess.city.ac.uk/id/eprint/14851/13/FXVALUE_Rev3_cepr.pdf)
- Post-2010 weakness: DB G10 carry index 10-year annualized +0.02% to March 2020 — [SEC FWP 2020](https://www.sec.gov/Archives/edgar/data/1354730/000119312520124811/d903986dfwp.htm); carry decline after GFC — [Fan et al. 2022](https://ideas.repec.org/a/eee/intfin/v76y2022ics1042443121001670.html); Barroso & Santa-Clara's optimized returns faded after 2005 — [CXO Advisory](https://www.cxoadvisory.com/strategic-allocation/optimized-currency-trading)

### Inferences
- Design implications for the G8 MT4 system (inference, not tested): (1) replace or down-weight pure momentum; (2) build a dollar-neutral cross-sectional portfolio of 7 non-USD currencies + USD with equal-risk sleeves of carry (interest-rate differential) and value (5-year real exchange rate change), optionally a small 12-month trend sleeve; (3) rebalance monthly (value/carry signals change slowly, and weekly turnover adds cost); (4) expect gross Sharpe ≈ 0.4-0.7 for the combination and single-digit annual returns at ≈ 4-6% vol unlevered.
- With 8 currencies, long/short legs are 2-3 currencies each (DB used 3 v 3 from 10 G10 currencies); idiosyncratic noise will be higher than in the 9-27 currency academic samples, so backtest Sharpe will be lower and more period-dependent.
- On a retail MT4 account, carry is earned through broker swap/rollover rates rather than forward points; broker swap markups could consume much of a G10 carry premium that was only ≈ 3% p.a. gross in developed-market HML carry (LRV). This needs to be measured on the actual demo account before trusting a carry sleeve.
- The user's 2000-2026 momentum result (-0.24) falls in the period where the literature shows currency momentum's weakest performance (post-publication Sharpe ≈ 0.08), so it is consistent with the evidence rather than an implementation bug, though the latter cannot be ruled out from these notes.

### Gaps
- No source found that reports a clean, live (non-backtest), G10-only carry+value+momentum track record covering 2010-2026 with year-by-year numbers.
- No Robeco, Pictet, Record or AQR live-fund FX-style performance figures were located in this pass.
