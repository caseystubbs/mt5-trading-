# FX Momentum Evidence in G10 / Developed Currencies (cross-sectional and time-series), with emphasis on post-2000 performance

Research note compiled 2026-10-14. Context: our weekly-rebalanced G8 cross-sectional momentum system (28-pair strength series, 15/30/35/20% weights on vol-normalised 1/3/6/12-month returns, long strongest / short weakest in 2 pairs) backtested on Fed H.10 daily spot rates 2000-2026 at -6.5%/yr before costs, Sharpe -0.24, negative in 2000-2012 and 2013-2026, every single horizon Sharpe <= 0.

Labels used below: **[IN-SAMPLE]** = results in the original paper's own sample; **[POST-PUB / OOS]** = evidence after the publication or sample end of the original work; **[EM-DEPENDENT]** = results that rely on emerging/minor currencies.

---

## Q1. Menkhoff, Sarno, Schmeling & Schrimpf (2012), "Currency Momentum Strategies" (JFE 106(3), 660-684): returns, Sharpe, sample, role of minor currencies, costs, decay

### Takeaway
The headline figures are large (about 9.5%/yr, Sharpe 0.95 for 1-month formation/1-month holding), but they come from a broad sample of up to 48 currencies (1976-2010). The authors themselves report that for developed-country currencies alone, momentum returns are "much smaller and basically non-existent after transaction costs". Profits sit in high-idiosyncratic-volatility, high-country-risk currencies, and they decline steadily as the formation and holding periods lengthen.

### Cited Findings
- **[IN-SAMPLE, EM-DEPENDENT]** Sample: Jan 1976 to Jan 2010 and 48 countries, with the effective cross-section "never exceed[ing] 40 currencies". There are 9,403 currency-month observations — [BIS WP 366 (working-paper version)](https://www.bis.org/publ/work366.pdf)
- **[IN-SAMPLE]** Table 1, Panel A, annualised excess returns for holding period h=1 month: formation f=1: 9.46%; f=3: 9.40%; f=6: 8.54%; f=9: 7.18%; f=12: 6.16% — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- **[IN-SAMPLE]** With h=12 months the returns are much lower: f=1: 5.75%; f=3: 4.43%; f=6: 3.14%; f=9: 3.24%; f=12: 1.89%. The paper notes "a monotone decline in average excess returns" as the holding period lengthens — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- **[IN-SAMPLE]** Table 1, Panel B, Sharpe ratios for h=1: f=1: 0.95; f=3: 0.88; f=6: 0.79; f=9: 0.67; f=12: 0.61 — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- **[IN-SAMPLE]** Transaction costs (Table 7): MOM(1,1) falls to 3.92% net with full quoted bid-ask spreads, versus 5.28% at 75% of quoted spreads and 6.64% at 50%. The best strategy drops "from nearly 10% to about 4% p.a." — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- **[IN-SAMPLE]** Turnover "can be extremely high, reaching values of more than 70% per month" for the f=h=1 strategy — [BIS WP 366](https://www.bis.org/publ/work366.pdf)
- **[IN-SAMPLE, developed-only]** When the cross-section is limited to 15 developed countries, "momentum returns are much smaller and basically non-existent after transaction costs". The authors conclude "the profitability of momentum strategies depends on whether smaller and presumably less liquid currencies are included" — [BIS WP 366](https://www.bis.org/publ/work366.pdf)
- **[IN-SAMPLE]** The paper also says that the most minor currencies (likely subject to capital controls) "do not drive the lion's share of our result". The effect is spread across non-major currencies rather than coming only from capital-controlled ones — [BIS WP 366](https://www.bis.org/publ/work366.pdf)
- **[IN-SAMPLE]** Idiosyncratic volatility sort (f=1): high-IVOL currencies earn about 8.09% p.a. versus 3.97% p.a. for low-IVOL. Momentum is significantly positive in high-country-risk currencies and not significant in low-risk ones — [BIS WP 366](https://www.bis.org/publ/work366.pdf)
- **[IN-SAMPLE]** Momentum versus carry: carry Sharpe is 0.82 against 0.95 for MOM(1,1). The high-minus-low correlations are 0.04 (f=1), 0.01 (f=6) and 0.07 (f=12). Carry is negatively skewed and momentum slightly positively skewed. In Jul 2007 to Jun 2009 the correlation was as low as -31% — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf); [BIS WP 366](https://www.bis.org/publ/work366.pdf)
- **[IN-SAMPLE, time variation]** Momentum was "much more profitable (after transaction costs) in the later part of the sample". Net returns were about 2% per month in 2000-2005, and net MOM(1,1) returns exceeded 7% p.a. over Jan 1992 to Jan 2010 (all currencies, not developed-only) — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- **[IN-SAMPLE]** Post-formation returns rise for about 8-12 months and then reverse over horizons up to 36 months — [BIS WP 366](https://www.bis.org/publ/work366.pdf)
- Authors' summary in Cass/City press coverage: "most momentum profits came from less liquid emerging-market currencies, such as the Brazilian real, South African rand, and Philippine peso, not from major currencies like the US dollar, euro, or sterling". G10-only ETFs are where "the effect is much less apparent". Trades between two exotic currencies can cost ten times as much as trades between majors, and about a third of returns is lost to costs. A Deutsche Bank momentum ETF underperformed a blended ETF in 2009 and 2011 — [Cass Knowledge, "Swept along by currencies" (2013)](https://www.cass.city.ac.uk/faculties-and-research/research/cass-knowledge/inbusiness/2013/swept-along-by-currencies)
- Trade-press summary of the same paper: illiquid currencies account for "up to 50% of momentum returns", turnover is about 60-70% per month, and "major-currency-only momentum lost money over the sample's last 10 years" (roughly 2000-2010). I could not verify this last statement in the working-paper text — [Hedgeweek, 8 Jun 2012](https://www.hedgeweek.com/fx-trading-doldrums-due-muted-volatility-cass-research-paper-highlights-merits-mom/)

### Inferences
- In this paper the 1-month signal is the strongest. Our system puts only 15% weight on 1-month and 55% on 6/12-month. Even in Menkhoff's broad sample, 12-month formation earns about one-third of the 1-month return (6.16% vs 9.46% at h=1; 1.89% at h=12).
- The rise in profitability after 2000 that Menkhoff reports is driven by the broad (EM-inclusive) cross-section. It says nothing positive about G8 majors over 2000-2010. The developed-only result, plus the unverified "lost money over the last 10 years" press summary, points the other way.
- Their portfolios are excess returns from forward contracts, which include the interest differential. Ours are spot-only H.10 returns, so the results are not like-for-like (see Q8).

### Gaps
- I could not extract the exact numeric developed-country subsample results (Internet Appendix Table A.12) from the available text. The "major-currency momentum lost money in the last 10 years" claim comes only from Hedgeweek's summary and is not confirmed verbatim in the paper.

---

## Q2. Asness, Moskowitz & Pedersen (2013), "Value and Momentum Everywhere" (JF): currency momentum in G10-type sample

### Takeaway
In a 10-currency developed-market universe (1979 to Jul 2011), currency momentum (12-1 month) earned only about 3.0-3.5%/yr with a Sharpe of 0.32-0.34. That was not significant at 5% even in-sample. Its value comes mostly from its -0.42 correlation with currency value, which lifts a 50/50 combination to a Sharpe of about 0.69.

### Cited Findings
- **[IN-SAMPLE]** The universe has 10 currencies: AUD, CAD, DEM/EUR, JPY, NZD, NOK, SEK, CHF, GBP and USD. The sample runs Jan 1979 to Jul 2011, with at least 7 currencies at any time and all 10 after 1980. Returns come from forwards (or spot plus Libor), so they include the interest differential — [AMP 2013 paper PDF](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)
- **[IN-SAMPLE]** The momentum signal is the past 12-month return skipping the most recent month (MOM2-12). The paper skips the last month "to maintain uniformity across asset classes" — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)
- **[IN-SAMPLE]** Table I, Panel B, currencies: momentum P3-P1 mean 3.5%/yr, t=1.90, SD 10.3%, Sharpe 0.34. Momentum factor mean 3.0%, t=1.77, SD 9.6%, Sharpe 0.32 — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)
- **[IN-SAMPLE]** Currency value P3-P1: 3.3%, Sharpe 0.34; value factor 3.9%, Sharpe 0.44. The 50/50 value/momentum factor earns 5.6%, t=3.89, SD 8.0%, Sharpe 0.69 — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)
- **[IN-SAMPLE]** The value-momentum correlation in currencies is -0.42 (P3-P1) and -0.43 (factors). The average across non-stock asset classes is -0.49 — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf)

### Inferences
- Even in-sample, standalone G10 momentum had a t-stat below 2 and a Sharpe of about 0.3. With a Sharpe that low, a 20-25 year window can easily show a negative realised Sharpe by chance alone. Add the post-sample decay documented in Q6 and a G8 result of -0.24 is not surprising.
- AMP use tercile spreads or rank weights across 10 currencies, not a 2-pair extreme bet, and they rebalance monthly (see Q8).

### Gaps
- I did not obtain AQR's updated (post-2011) currency momentum factor series, so I cannot give AQR's own post-publication number for this exact factor.

---

## Q3. Time-series momentum / trend in FX: Moskowitz, Ooi & Pedersen (2012); Hurst, Ooi & Pedersen; Baltas & Kosowski; post-2009 trend performance

### Takeaway
Time-series momentum in currency forwards was strongly significant in 1985-2009, with a 12-month lookback t-stat of 3.41 and a 3-month lookback t-stat of 3.90. Multi-asset trend-following then went nearly flat after 2009: SG Trend Index Sharpe 0.05 in 2010-2018, and Baltas-Kosowski TSMOM Sharpe 0.01 gross in 2009-2013. Out-of-sample G10 currency TSMOM was negative and insignificant for 2010-2020 (see Q6).

### Cited Findings
- **[IN-SAMPLE]** MOP (2012) evaluation period: Jan 1985 to Dec 2009. The currency universe is described as "12 cross-currency pairs (from nine underlying currencies)", though the appendix lists ten exchange rates — [MOP 2012 JFE PDF](https://fairmodel.econ.yale.edu/ec439/jpde.pdf)
- **[IN-SAMPLE]** For currencies with a 1-month hold, the 12-month lookback t-stat is 3.41 (Table 2, Panel E). The 3-month lookback has the highest t-stat at 3.90 — [MOP 2012](https://fairmodel.econ.yale.edu/ec439/jpde.pdf)
- **[IN-SAMPLE]** Returns continue for about 12 months and then "partially reverse". For the 12-month lookback, alpha t-stats at 24-, 36- and 48-month holds are -0.29, -1.01 and -1.67. For the 24-month lookback they are -1.15, -1.88 and -2.27. The diversified multi-asset TSMOM Sharpe is "greater than one" — [MOP 2012](https://fairmodel.econ.yale.edu/ec439/jpde.pdf)
- **[IN-SAMPLE, long history]** Hurst, Ooi & Pedersen cover Jan 1880 to Dec 2016 across 67 markets, including 12 currency pairs (the appendix lists 10 currencies). Their signal is an equal-weighted 1/3/12-month TSMOM with volatility-scaled positions, 10% target vol and monthly rebalancing. The strategy was positive in every decade. The average single-market Sharpe is about 0.4 gross. Currency data start 1989 for most currencies, 1992 for CAD and 1996 for NZD — [Hurst, Ooi & Pedersen, "A Century of Evidence on Trend-Following Investing"](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)
- **[POST-2008]** In Hurst et al., cross-market correlations rose "meaningfully from late 2008 to mid-2014" during "risk-on/risk-off" trading. With constant risk targets, that shrinks position sizes and lowers returns — [Hurst, Ooi & Pedersen](https://fairmodel.econ.yale.edu/ec439/hurst.pdf)
- **[POST-2009]** AQR's analysis (summarised Dec 2019) puts the SG Trend Index Sharpe at **0.05 for 2010-2018**, against 0.28 since 2000. AQR attributes this mainly to "muted market moves" and explicitly rejects crowding or loss of diversification as causes — [AQR "You Can't Always Trend When You Want", summary](https://theideafarm.com/alternative-investment/you-cant-always-trend-when-you-want/)
- **[POST-2009]** Baltas & Kosowski cover 1984-2013 across 56 futures, including only 6 currencies. Their default TSMOM has a pre-cost Sharpe of 1.15 over the full period, but only **0.01 before costs and -0.09 after costs in 2009-2013**. They attribute this partly to correlations that "dramatically increased" post-GFC. "Currency and commodity futures have insignificant mean returns with only a few exceptions" — [Baltas & Kosowski, "Demystifying Time-Series Momentum Strategies"](https://www.cmegroup.com/education/files/demystifiing-time-series-momentum-strategies.pdf)
- Baltas & Kosowski on implementation: default monthly turnover is about 170%. A "TREND" rule (t-stat-scaled exposure capped at +/-1) cuts turnover by about 24% with no statistically significant Sharpe loss. Trading costs are about 163 bp/yr on 16.12% gross — [Baltas & Kosowski](https://www.cmegroup.com/education/files/demystifiing-time-series-momentum-strategies.pdf)

### Inferences
- Time-series currency momentum held up better than cross-sectional momentum in-sample. Both look weak after 2009-2010 in majors (Q6). Our system is cross-sectional, which is the weaker of the two in G10 post-2010 according to Hutchinson et al. (Q6).
- MOP's strongest currency lookback is 3 months. That is consistent with our 30% weight on 3-month, but the same horizon failed out-of-sample after 2010 (Q6).

### Gaps
- I did not find currency-specific Sharpe ratios from Hurst/Ooi/Pedersen or Baltas/Kosowski, because the exhibits were not extractable. I also did not find a public SG Trend Index FX sub-sector series or a Man AHL note giving exact FX-sector trend returns for 2010-2026.

---

## Q4. Burnside-Eichenbaum-Rebelo; Filippou-Gozluklu-Taylor; technical-rule decay (Olson 2004; Neely, Weller & Ulrich 2009; Schulmeister)

### Takeaway
1-month FX momentum on 20 major currencies earned a Sharpe of 0.62 in 1976-2010, but the average single currency trade had a Sharpe of only 0.43. Diversifying across currencies matters. Separately, a long line of evidence shows technical and trend rules on major dollar pairs were profitable in the 1970s-80s and decayed to roughly zero by the 1990s-2000s, which fits the Adaptive Markets Hypothesis.

### Cited Findings
- **[IN-SAMPLE]** Burnside, Eichenbaum & Rebelo (NBER w16942, 2011) use 20 major currencies (not a G10-only set) over 1976-2010. Their momentum rule buys or sells each currency forward according to the sign of last month's return, which is time-series-style versus USD. Portfolio: mean 4.5%, SD 7.3%, **Sharpe 0.62**. Average individual momentum trade: mean 4.9%, SD 11.3%, **Sharpe 0.43**. Carry portfolio Sharpe 0.89. A 50/50 carry-momentum mix has Sharpe 0.98 — [NBER w16942](https://www.nber.org/papers/w16942.pdf)
- **[IN-SAMPLE]** Momentum gained about 24% in Aug-Nov 2008, its best four-month run in the sample. From late Aug 2000 to Dec 2010 it returned 76.1% cumulatively, against 93.9% for carry. The paper does not test momentum net of bid-ask spreads — [NBER w16942](https://www.nber.org/papers/w16942.pdf)
- **[IN-SAMPLE]** Filippou, Gozluklu & Taylor (JFQA 53(5), 2018) find that "political risk is priced in the cross section of currency momentum". Momentum winners typically carry exposure to global (mainly US-driven) political risk. The result is robust to transaction costs, reversals and other limits to arbitrage — [WRAP repository record](https://wrap.warwick.ac.uk/96779/); [IDEAS/RePEc](https://ideas.repec.org/a/cup/jfinqa/v53y2018i05p2227-2259_00.html)
- **[DECAY]** Neely, Weller & Ulrich (JFQA 2009; St. Louis Fed WP 2006-046) re-test published FX technical rules after their original samples:
  - Levich-Thomas MA/filter rules on DEM, JPY, CHF, GBP: the 1% filter averaged 8.47% net in 1976-1990 and -1.14% in 1991-2005:6. The uniform-portfolio Sharpe fell from 0.90 to -0.02. MA(5,20) was the best rule at 9.09% in the original period. Equal means are rejected in 21 of 36 cases.
  - Sweeney filter rules on ten currencies: the uniform portfolio's Sharpe fell from 0.84 (1973-1980) to 0.41 (1981-2005).
  - Channel rules: mean net return fell from 5.74% to 1.91%, and trades per year from 20.51 to 6.00.
  - Genetic-programming rules: Sharpe fell from 0.36 to 0.02 after Oct 1995.
  - Structural breaks for filter/MA rules fall mostly in 1989-1993, and Levich-Thomas rules show trend declines of 24-42 bp/yr. The authors conclude that profits in popular filter/MA rules "had largely disappeared by the mid-1990s".
  - Sources: [St. Louis Fed WP 2006-046](https://files.stlouisfed.org/files/htdocs/wp/2006/2006-046.pdf); [JFQA record](https://gpbib.pmacs.upenn.edu/gp-html/Neely_2009_JFQA.html)
- **[DECAY]** Schulmeister (WIFO WP 325, 2008) averages 1,024 MA and momentum models on yen/dollar in four-year blocks. Gross returns were 13.95% (1976-79), 9.79% (1980-83), 14.96% (1984-87), 5.59% (1988-91), 7.51% (1992-95), 3.16% (1996-99), **-0.21% (2000-03) and 0.47% (2004-07)**. About half the models lost money in each 2000s block. Euro/dollar earned 3.8%/yr in 2000-2004 with the same models — [Schulmeister, WIFO WP 325](https://wifo.ac.at/wp-content/uploads/upload-1881/WP_2007_325.pdf)
- Olson (2004), "Have trading rule profits in the currency markets declined over time?", J. Banking & Finance 28(1), 85-105, is cited by later work as documenting a decline in MA-rule profits in currency markets — [IDEAS/RePEc record](https://ideas.repec.org:443/a/eee/jbfina/v28y2004i1p85-105.html); cited as such in [Schulmeister](https://wifo.ac.at/wp-content/uploads/upload-1881/WP_2007_325.pdf)
- **[DECAY, practitioner]** Levich (NYU Stern, 2012) regresses the Barclay Currency Traders Index on a trend factor. The trend beta fell from 1.44 (1990-2000) to 0.77 (2001-2006) — [Levich, "Patterns in Currency Hedge Fund Returns and Trading Styles"](https://www.stern.nyu.edu/sites/default/files/assets/documents/con_034487.pdf)

### Inferences
- In Burnside et al., the portfolio Sharpe (0.62) is about 44% higher than the average single trade (0.43). That is direct evidence that concentrating in 1-2 positions costs a lot of risk-adjusted return, relevant to our 2-pair design.
- Burnside's 2000-2010 momentum gains came from a 20-currency, carry-inclusive, USD-based (time-series) design. They do not contradict a losing G8 cross-sectional spot-only result for the same years.
- The technical-rule decay literature places the death of simple trend rules on major USD pairs at roughly 1989-2000. The negative G8 result over 2000-2026 is consistent with that timeline.

### Gaps
- I could not access Olson (2004)'s abstract or numbers because ScienceDirect blocked the fetch and RePEc has no abstract. I could not extract the exact return numbers or sample from Filippou et al. (2018).

---

## Q5. Do short-horizon (around 1-week to 1-month) returns in majors show reversal rather than momentum?

### Takeaway
The evidence is mixed. In broad (EM-inclusive) samples, 1-month momentum is the strongest signal. In major currencies there is evidence of weak 1-week reversal, and 1-week momentum is economically nil. After 2010, G10 cross-sectional momentum at 3-month formation and 1-month hold turned significantly negative, which in effect is a reversal regime.

### Cited Findings
- **[IN-SAMPLE, EM-DEPENDENT]** Menkhoff et al. find 1-month formation strongest (9.46%/yr, Sharpe 0.95) across up to 48 currencies, 1976-2010 — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf)
- **[IN-SAMPLE, EM-DEPENDENT]** Raza, Marshall & Visaltanachoti (J. Int'l Money & Finance 45, 2014) test weekly momentum in 63 currencies, Nov 1997 to Jul 2013. MOM(1,1) (1-week formation, 1-week hold) earned 1.84%/yr, Sharpe 0.206, t=0.848, not significant. MOM(3,1) earned 8.13%, Sharpe 0.913. In 2005-2013 MOM(1,1) earned 0.011% (t=0.231). Breakeven one-way costs range from about 2 bp for MOM(1,1) to 97 bp for MOM(4,4), and the authors conclude short-term versions are unlikely to survive costs — [Massey University repository PDF](https://mro.massey.ac.nz/bitstreams/8d7c87d0-7a19-46ab-b2ad-fa49a8176b48/download); [IDEAS record](https://ideas.repec.org/a/eee/jimfin/v45y2014icp38-60.html)
- **[IN-SAMPLE]** In Raza et al., *excluding* the major currencies in the Deutsche Bank carry ETF (e.g., AUD, EUR, JPY, CHF) *raises* MOM(4,4) from 8.60% to 12.64%. Weekly momentum is stronger outside the majors — [Massey PDF](https://mro.massey.ac.nz/bitstreams/8d7c87d0-7a19-46ab-b2ad-fa49a8176b48/download)
- **[IN-SAMPLE, majors]** Della Corte & Kosowski ("Market Closure and Short-Term Reversal", incomplete WP Nov 2015) study 9 CME currency futures (AUD, GBP, CAD, DEM, EUR, JPY, MXN, NZD, CHF), Jul 1982 to Dec 2014:
  - A weekly close-to-close short-term reversal strategy earns 0.071%/week, t=2.00, Sharpe 0.36.
  - At daily frequency close-to-close reversal is insignificant over the full sample (Sharpe 0.17), but 0.536 (t=1.66) in 2007-2014.
  - The strongest effect is overnight close-to-open reversal (daily Sharpe 1.26), which the authors tie to market closure order imbalances.
  - [CICF conference paper](https://www.cicfconf.org/sites/default/files/paper_357.pdf)
- **[POST-PUB / OOS, G10]** Hutchinson et al. (2022) find "no relationship between past and future returns" out-of-sample (post-2010) in G11 pooled regressions. Cross-sectional MOM (3-month formation, 1-month hold) earned a significantly negative -3.51%/yr — [Hutchinson et al., IRFA 2022 (repository PDF)](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- MOP (2012) report continuation up to about 12 months and reversal beyond that, rather than at 1 month, for currency TSMOM in 1985-2009 — [MOP 2012](https://fairmodel.econ.yale.edu/ec439/jpde.pdf)

### Inferences
- For majors, the weekly horizon is at best noise (Raza MOM(1,1) not significant even with EM) and at worst mildly mean-reverting (Della Corte-Kosowski weekly reversal t=2.0 in mostly-G10 futures). A weekly rebalance that reacts to a vol-normalised 1-month return (15% weight) is likely trading noise or reversal.
- I found no clean primary source establishing 1-month *reversal* in G10 spot over 2000-2026 specifically. The closest is Hutchinson's significantly negative OOS 3m/1m cross-sectional result.

### Gaps
- I found no primary paper isolating G10-only 1-month cross-sectional reversal with exact numbers for 2000-2026. Della Corte & Kosowski is an incomplete working paper that includes MXN and uses futures, not spot.

---

## Q6. Post-publication / out-of-sample evidence (2010-2026): has FX momentum decayed in G10?

### Takeaway
Yes. The strongest direct evidence is Hutchinson, Kyziropoulos, O'Brien, O'Reilly & Sharma (2022). In the 10 most liquid currencies, cross-sectional momentum earned **-3.51%/yr gross, Sharpe -0.68 (t=-2.20)** out-of-sample from Feb 2010 to Apr 2020, or **-3.95%/yr, Sharpe -0.77** net. Across 123 cross-sectional momentum variants the average OOS Sharpe was -0.42. They date a structural break in G11 momentum to **Aug 2001**. Our G8 result (Sharpe -0.24 over 2000-2026, negative in both halves) is in line with, and actually milder than, this published evidence.

### Cited Findings
- **[POST-PUB / OOS, G10]** Hutchinson et al., "Are carry, momentum and value still there in currencies?", Int'l Review of Financial Analysis 83 (2022) 102245:
  - The "G11" universe is the 10 most liquid non-USD currencies vs USD (DEM pre-1999), Jan 1980 to Apr 2020.
  - Cross-sectional MOM uses 3-month formation and 1-month hold (Menkhoff spec). TSM uses a 12-month lookback and 1-month hold (MOP spec).
  - The MOM in-sample window is Jan 1980 to Jan 2010 and the out-of-sample window Feb 2010 to Apr 2020. For TSM, OOS starts Jan 2010.
  - [repository PDF](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download); [IDEAS record](https://ideas.repec.org/a/eee/finana/v83y2022ics1057521922002058.html)
- Hutchinson et al., G11 cross-sectional MOM, gross: full sample 1.13%/yr (t=1.18), Sharpe 0.18 (not significant). In-sample 2.75% (t=2.44), Sharpe 0.43. **Out-of-sample -3.51% (t=-2.54), Sharpe -0.68 (t=-2.20)**. Net of costs OOS: -3.95%, Sharpe -0.77 — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- Hutchinson et al., G11 time-series momentum, gross: full sample 3.01%, Sharpe 0.43. In-sample 3.37%, Sharpe 0.45. **OOS -0.99%, Sharpe -0.16** (insignificant); net OOS -1.10%, Sharpe -0.18. Carry OOS Sharpe -0.10; value OOS Sharpe +0.30 (insignificant) — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- Hutchinson et al., 252 specification variants (gross): average Sharpe fell from +0.39 in-sample to -0.32 OOS. For cross-sectional MOM (123 variants) it fell from 0.32 to **-0.42**, and for TSM (123 variants) from 0.46 to -0.23 — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- Hutchinson et al., structural breaks (CUSUM of squares): momentum **Aug 2001**, value Sep 2007, carry Jun 2013. The authors attribute the decline to arbitrage after academic publication and note "no serial correlation during the recent period" — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- **[POST-PUB / OOS, EM-inclusive]** In 24 "peripheral" (mostly EM) currencies, OOS cross-sectional MOM earned +0.70% (t=0.46), Sharpe 0.14, and TSM Sharpe 0.02. Neither is significant, but both are less negative than G11. The combined 34-currency MOM Sharpe was -0.14 — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- **[POST-PUB / OOS, 2010-2025]** An Aalto University bachelor's thesis tested 32 global currencies, Jan 2010 to Jan 2025, with 25 long-short portfolios (formation and holding of 1/3/6/9/12 months). None earned statistically significant excess returns, and it concludes momentum returns "have largely disappeared since the Global Financial Crisis". This is student work with lower evidentiary weight — [Aalto thesis record, "Momentary loss: The disappearance of cross-sectional currency momentum"](https://aaltodoc.aalto.fi/items/0db57fa9-e5c6-4b7d-9dd8-1ae15a8940c6)
- **[LONG HISTORY]** Chen ("Currency Investing Throughout Recent Centuries", SSRN 4692257, rev. 2024) covers 21 currencies from 1788. Momentum earned positive returns "only during the latter half of the sample", and panel regressions "do not detect a robust currency momentum effect". He raises data snooping or "some time-varying underlying mechanism" as explanations — [Quantpedia summary](https://quantpedia.com/fx-carry-value-momentum-strategies-over-their-200-year-history/)
- **[MECHANISM]** Zhang ("Dissecting Currency Momentum", SSRN 2021) covers up to 48 currencies, Mar 1976 to Nov 2020. He finds "factor momentum not only outperforms the cross-sectional and time-series momentum but also explains them". In other words, currency momentum is largely autocorrelation in the carry and dollar factors. The momentum-carry correlation is 0.356 after three months of carry gains and -0.62 after three months of carry losses — [IBKR Campus / Alpha Architect summary](https://ibkrcampus.com/campus/ibkr-quant-news/is-currency-momentum-factor-momentum/)

### Inferences
- Our G8 Sharpe of -0.24 over 2000-2026 sits between Hutchinson's G11 full-sample (+0.18) and OOS (-0.68) figures. Given their Aug 2001 break date, a negative 2000-2012 and a negative 2013-2026 are exactly what this literature predicts for majors. **The headline result does not by itself indicate a coding flaw.**
- If Zhang is right that currency momentum is mostly carry and dollar factor momentum, a spot-only strength ranking misses the carry leg. Our G8 ranking against a 28-pair basket also largely nets out the dollar factor (USD is just one of 8). That leaves little of the economically meaningful part of the signal.
- The pattern "losers in majors, flat in EM" suggests the premium that existed in majors was arbitraged away first. That fits Hutchinson's publication-arbitrage story and Menkhoff's limits-to-arbitrage story.

### Gaps
- I found no peer-reviewed G10-only study extending the out-of-sample window through 2023-2026. Hutchinson stops at Apr 2020 and the 2010-2025 study is a bachelor's thesis covering 32 global currencies. Hutchinson's full journal version could not be fetched directly from ScienceDirect, which blocked robots; the numbers above come from the author repository PDF.

---

## Q7. Practitioner evidence: Deutsche Bank FX momentum indices, FX trend indices, currency managers (2010-2026)

### Takeaway
Practitioner records broadly agree: FX-specific managers and bank FX style indices struggled after about 2010. The Deutsche Bank Currency Returns index (carry + momentum + value) had its worst year in 2011 since 1991, and momentum dragged it again in early 2014. FX macro hedge funds made about zero from end-2010 to early 2021. One counterpoint is Russell's ARCS multi-strategy record, which shows a diversified FX trend sleeve earning +3.3%/yr from Dec 1999 to Mar 2024.

### Cited Findings
- **[PRACTITIONER, 2011]** The Deutsche Bank Currency Returns Index (USD) fell 3.4% in 2011 through late October, "the biggest drop since a 4 percent slide in 1991". Three of four RBS FX strategy indices were down, and the Stark Currency Traders Index was down 8.6% — [Bloomberg, 26 Oct 2011](https://www.bloomberg.com/news/articles/2011-10-26/currency-traders-in-worst-year-since-1991)
- **[PRACTITIONER, 2014]** The DB Currency Returns Index (blend of carry, momentum, valuation) was "dragged down by momentum trading" in early 2014. Currency traders had their worst start to a year since 2010 — [Bloomberg, 21 Feb 2014, "Currency Traders' Strategies Foiled as Trends Go Missing"](https://www.bloomberg.com/news/articles/2014-02-21/currency-traders-strategies-foiled-as-trends-go-missing)
- **[PRACTITIONER]** A Deutsche Bank momentum ETF underperformed a blended currency ETF in 2009 and 2011 — [Cass Knowledge 2013](https://www.cass.city.ac.uk/faculties-and-research/research/cass-knowledge/inbusiness/2013/swept-along-by-currencies)
- **[PRACTITIONER, 2012]** Market commentary in mid-2012: low rates and central bank intervention kept G10 currencies range-bound, the CHF was capped at 1.20 per EUR, and EUR/USD 1-month implied vol was at its lowest since Lehman. Citi's Jones said trend models "haven't done that well", and Man AHL scales back in range-bound markets — [Hedgeweek, 8 Jun 2012](https://www.hedgeweek.com/fx-trading-doldrums-due-muted-volatility-cass-research-paper-highlights-merits-mom/)
- **[PRACTITIONER, 2010-2021]** The HFRI Macro Currency Index produced "roughly zero profit since the end of 2010". Currency-focused hedge funds peaked at about 145 in 2008 and were below 50 by early 2021. Rate spreads between majors and the USD converged, and FX vol declined after the 1990s — [Verdad, "Whatever Happened to FX?" (2021)](https://verdadcap.com/archive/whatever-happened-to-fx)
- **[PRACTITIONER, trend 2010-2018]** SG Trend Index Sharpe was 0.05 for 2010-2018 (multi-asset, not FX-only) — [AQR summary](https://theideafarm.com/alternative-investment/you-cant-always-trend-when-you-want/)
- **[PRACTITIONER, counterpoint]** Russell Investments' ARCS (carry/value/trend currency strategy), Dec 1999 to Mar 2024 in USD:
  - Trend: 3.3%/yr annualised, 6.8% risk, worst 1-year -12.7%, max drawdown -13.4%, 5-year trailing 1.8% p.a.
  - Carry: 4.0% / 7.7%. Value: 2.7% / 6.7%.
  - The document does not state the currency universe or whether these are live or simulated. Russell notes trend "performs best when markets evidence a persistent trend and worst when markets are choppy in range-bound conditions".
  - [Russell Investments ARCS research update 2024](https://russellinvestments.com/-/media/files/emea/uk/institutional/insights/emea-arcs-research-paper-update-2024.pdf)

### Inferences
- The Russell trend sleeve (about 0.49 return/risk by my calculation) is time-series trend, diversified, and possibly includes non-G10 currencies. It is not evidence for a 2-pair G8 cross-sectional design. It does suggest that diversified, lower-turnover FX trend held up better than concentrated cross-sectional momentum.

### Gaps
- I found no public series or exact annual returns for the Deutsche Bank FX Momentum index (G10 12-month momentum), the SG Trend Index FX sub-sector, Credit Suisse or Barclays FX trend indices, or recent Man AHL/AQR FX-sector trend attributions for 2010-2026. Bloomberg's own pages were only partially extractable.

---

## Q8. Why might a weekly-rebalanced, 2-pair, concentrated G8 cross-sectional momentum portfolio underperform the academic long-short portfolios? Does our -6.5%/yr (Sharpe -0.24) match the literature or suggest a flaw?

### Takeaway
The result matches the literature's direction. G10 cross-sectional momentum was weak even in-sample (Sharpe 0.18-0.43) and significantly negative out-of-sample after 2010 (Sharpe -0.68). Several design choices would make our version worse than the academic portfolios:
- extreme concentration (2 of 28 pairs versus terciles or rank weights)
- weekly rebalancing in a market where 1-week returns show no momentum or mild reversal
- a spot-only (no carry) return definition
- a signal tilted to 6/12-month horizons, which were the weakest even in Menkhoff

The size of the loss is worth one sanity check: -6.5% at Sharpe -0.24 implies about 27% annualised volatility.

### Cited Findings
- **Concentration:** Burnside et al.'s diversified momentum portfolio Sharpe was 0.62 against 0.43 for the average single-currency trade, 1976-2010 — [NBER w16942](https://www.nber.org/papers/w16942.pdf). AMP's G10 momentum is a tercile spread or rank-weighted factor across 10 currencies — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf). Hutchinson's G11 MOM is also a portfolio sort over 10 currencies — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- **Where the premium lives:** momentum is concentrated in high-IVOL (8.09% vs 3.97%) and high-country-risk currencies, and developed-only momentum is "basically non-existent after transaction costs" — [BIS WP 366](https://www.bis.org/publ/work366.pdf). Excluding majors raises weekly momentum returns from 8.60% to 12.64% — [Raza et al. PDF](https://mro.massey.ac.nz/bitstreams/8d7c87d0-7a19-46ab-b2ad-fa49a8176b48/download). Momentum winners carry political-risk exposure — [Filippou et al. 2018](https://wrap.warwick.ac.uk/96779/)
- **Turnover and costs:** f=h=1 turnover exceeds 70% per month — [BIS WP 366](https://www.bis.org/publ/work366.pdf). 1-week-lookback weekly momentum has breakeven one-way costs of about 2 bp — [Raza et al.](https://mro.massey.ac.nz/bitstreams/8d7c87d0-7a19-46ab-b2ad-fa49a8176b48/download). Monthly TSMOM turnover is about 170%, and smoothing the signal ("TREND" rule) cuts turnover about 24% with no significant Sharpe loss — [Baltas & Kosowski](https://www.cmegroup.com/education/files/demystifiing-time-series-momentum-strategies.pdf)
- **Horizon:** returns decline monotonically with holding period, and 12-month formation earns 6.16% (h=1) and 1.89% (h=12) against 9.46% for 1-month formation (broad sample) — [JFE version PDF](https://faculty.washington.edu/ss1110/IF/Sarno%20Currency%20Momentum%20JFE%20%281%29.pdf). Weekly 1-week momentum is not significant (t=0.85), and in the 2005-2013 subsample it is about zero — [Raza et al.](https://mro.massey.ac.nz/bitstreams/8d7c87d0-7a19-46ab-b2ad-fa49a8176b48/download). Weekly reversal appears in mostly-G10 currency futures (t=2.00) — [Della Corte & Kosowski](https://www.cicfconf.org/sites/default/files/paper_357.pdf)
- **Return definition:** the academic studies use excess returns that include the interest differential (forwards, or spot plus Libor) — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf); [BIS WP 366](https://www.bis.org/publ/work366.pdf). Momentum's correlation with carry is regime-dependent (+0.356 / -0.62 conditional) — [Zhang 2021 summary](https://ibkrcampus.com/campus/ibkr-quant-news/is-currency-momentum-factor-momentum/)
- **Regime and environment:** after 2008, range-bound G10 currencies under central bank intervention — [Hedgeweek 2012](https://www.hedgeweek.com/fx-trading-doldrums-due-muted-volatility-cass-research-paper-highlights-merits-mom/). Higher cross-market correlations shrank risk-targeted trend positions, 2008-2014 — [Hurst et al.](https://fairmodel.econ.yale.edu/ec439/hurst.pdf); [Baltas & Kosowski](https://www.cmegroup.com/education/files/demystifiing-time-series-momentum-strategies.pdf). On the cause there is a conflict: AQR attributes weak 2010-2018 trend to "muted market moves" and rejects crowding — [AQR summary](https://theideafarm.com/alternative-investment/you-cant-always-trend-when-you-want/) — while Hutchinson et al. attribute the FX momentum decline to post-publication arbitrage — [Hutchinson et al. 2022](https://repository.adu.ac.ae/bitstreams/4912355c-88d1-434c-a489-e44e6ba6494b/download)
- **Volatility benchmark:** academic G10 momentum portfolios run at about 9.6-10.3% annualised volatility — [AMP 2013](https://w4.stern.nyu.edu/facdir/lpederse/papers/ValMomEverywhere.pdf). Burnside's portfolio runs at 7.3% — [NBER w16942](https://www.nber.org/papers/w16942.pdf)

### Inferences
- **Direction matches the literature.** A negative pre-cost Sharpe for G8 cross-sectional momentum over 2000-2026, negative in both halves and at every horizon, is consistent with:
  - Hutchinson's Aug 2001 break and OOS Sharpe of -0.68 (G11, 2010-2020)
  - their -0.42 average across 123 cross-sectional momentum variants
  - AMP's in-sample G10 momentum t-stat of only 1.77-1.90
  - Menkhoff's finding that developed-only momentum disappears after costs
  - the technical-rule decay in USD majors since the 1990s (Neely-Weller-Ulrich; Schulmeister's yen/dollar averaging -0.21% and 0.47% in 2000-03 and 2004-07)
- **Magnitude check.** -6.5%/yr divided by Sharpe 0.24 implies about 27% annualised vol, roughly 2.5-3.5x the academic portfolios (7-10%). Sharpe is scale-free, so this is not a sign error. Still, verify position sizing and leverage (two full-notional pairs plus vol normalisation applied to positions rather than just to signals?) and whether return compounding or log-vs-simple aggregation inflates vol.
- **Suggested validation tests (to separate "no edge" from "bug"):**
  1. Replicate Hutchinson's spec on the same H.10 data: G8 vs USD, 3-month formation, 1-month hold, top-third minus bottom-third, monthly. Expect roughly Sharpe 0.4 for 1980-2009 and a negative figure for 2010-2020. If the engine shows positive pre-2001 and negative post-2001, the code is likely fine. Pre-1999 needs a DEM proxy for EUR; check H.10 historical availability.
  2. Rerun our exact signal with monthly instead of weekly rebalancing, and with terciles or rank weights instead of the single strongest/weakest pair, to measure the drag from concentration and churn.
  3. Add interest differentials (carry-inclusive excess returns) to test whether the spot-only definition is part of the loss.
  4. Treat any "flip the signal" result (short winners / long losers) with suspicion. Hutchinson's OOS negativity is significant, but a reversal strategy mined from the same data needs its own out-of-sample test.
- **Alternative signals with better developed-market evidence:**
  - Combine momentum with currency value. The AMP G10 value-momentum correlation is -0.42, and the 50/50 Sharpe was 0.69 in-sample, although value was also insignificant OOS (+0.30).
  - Use diversified time-series trend with smoothed signals (Baltas-Kosowski; Russell trend sleeve +3.3%/yr, 1999-2024).
  - Economic momentum: Dahlquist & Hasseltoft report a Sharpe of 0.70 over 1976 to Mar 2017 for 21 developed plus EM currencies, with alpha over carry, momentum and value — [Alpha Architect summary](https://alphaarchitect.com/fundamental-momentum-the-carry-trade-and-currency-returns/). That figure is in-sample, and EM is included.

### Gaps
- No source directly tests a 2-pair, weekly-rebalanced, 28-cross "strength meter" design. The concentration, weekly-churn and spot-only effects above are inferred from adjacent evidence, not measured for this exact construction.
- I found no source quantifying how much a multi-horizon (1/3/6/12-month) vol-normalised composite helps or hurts relative to single-horizon G10 momentum after 2010. Hutchinson's 123-variant average (-0.42 OOS Sharpe) suggests specification choice does not rescue it.
