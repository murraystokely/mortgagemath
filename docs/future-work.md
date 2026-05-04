# Future work

## Sources that did not match the library

These sources were investigated as candidate test fixtures but rejected
because at least one published value could not be reproduced exactly by
the library. They are recorded here in case the underlying issue is
worth revisiting later — either because we add a new amortization mode
that does match, or because we want to understand the variance among
published references.

The standing rule (see `tests/schedules/README.md`) is that a fixture
must reproduce **every** value the source attests to, or it does not go
in the test suite. Partial matches are not committed; they bury
divergences that could mask real bugs.

### Textbook sources

- **LibreTexts Business Math** (Olivier), §13.03, "Tamara's dishwasher
  loan" ($895.94 / 5.9% / 6mo). Library matches the monthly payment,
  row 1, and total interest. Rows 2–5 diverge by 1 cent each because
  the textbook applies a per-line "missing-pennies" reconciliation we
  could not reverse-engineer from the published prose.
- **eCampus Ontario** *Mathematics of Finance*, Example 4.3.4
  ($308,000 / 4.62% / 180mo). Library matches the monthly payment and
  row 21. The textbook's published "balance after payment 20"
  ($283,323.39) differs from the library's $283,323.40 by a single cent.
- **OpenStax Contemporary Math** §6.8 sample table
  ($10,000 / 4.75% / 240mo). Library matches monthly payment, month-10
  interest, and month-15 balance. Cumulative-interest at month 18
  differs by 4 cents.
- **OpenStax *Principles of Finance*** §8.3 (auto and home examples).
  Library matches monthly payment and row 1 in both. Total-interest
  figures published with each example differ from the library's by 2
  and 12 cents respectively.
- **Pima Open Press** *Topics in Mathematics* §6.4 (three examples).
  - Short illustration ($500 / 12% / 6mo): textbook lets the schedule
    end at a $0.03 residual, while the library closes balance to zero
    with an adjusted final payment.
  - Two longer mortgages: cumulative balance and total-interest
    figures drift by single-digit cents.
- **OpenStax Contemporary Math** §6.12 Example 6.111
  ($99,596 / 5.35% / 360mo) — published total-paid and financing-cost
  figures differ from the library's by ~$2.
- **OpenStax Contemporary Math** §6.12 Example 6.113
  ($165,900 / 5.61% / 360mo) — payment-175 principal differs by 1
  cent, balance-after-payment-170 differs by 80 cents.
- **Las Positas College** §8.05 Examples 2 and 4 — three fixtures
  rejected because the textbooks publish total-cost or
  total-interest figures that the library does not match (drifts of
  $0.49 to $5.03 over loan life).

### Calculator and consumer-education sources

- **Chase consumer-education page** ($200,000 / 5% / 360mo). Library
  reproduces rows 1–3 exactly (the strongest row-level match in any
  candidate). Row 360 differs because Chase's schedule winds down to a
  small natural residue, while the library adjusts the final payment
  to zero out the balance.

### Sources requiring algorithms the library does not implement

- **Kerry's Toyota Rav4** chose a non-actuarial whole-dollar
  payment ($2,691 instead of the closed-form $2,690.05), which
  puts the loan outside the closed-form annuity model. (As of
  v0.6.0, ``LoanParams.payment_override`` could in principle
  reproduce this if the source published a row-level schedule;
  it does not.)
- **William Hart, *Mathematics of Investment*** (1924, archive.org)
  — worked example uses mill-precision (3 decimals), incompatible with
  the library's cent-rounding.

Note: Canadian *Interest Act* §6 semi-annual compounding shipped
in v0.3.0 (``Compounding.SEMI_ANNUAL``). Multiple Canadian
fixtures (Olivier Chans first term + renewal; eCampus Ontario
§4.4.1 first term + renewal; eCampus §4.3 Erika / Johnetta /
Pearline) are now in the test suite.

## Possible future work

### Deferred library features

These features have been investigated but not shipped, either because
no verifiable published source was found or because the feature is
blocked on source retrieval.

- **`fee_per_period`** — flat per-period loading for Crédit Foncier
  and modern French *assurance emprunteur* schedules. Complete
  implementation exists on the ``fee-per-period-wip`` branch. Blocked
  on finding a row-level published source; see CLAUDE.md for trigger
  sources to watch. (Investigated in v0.6.0 cycle.)
- **Variable / declining-balance fees** — insurance computed on
  remaining balance ("assurance sur le capital restant dû"), stepped
  insurance schedules, or frais de garantie at a different cadence.
  Would require a ``FeeSchedule`` data type. No published source
  found.
- **``IndexedRateSchedule``** (Tier 2 ARM) — library-side derivation
  of post-cap rates from raw index history, margin, periodic cap,
  lifetime cap, and floor. Currently only one source (Reg Z Sample
  H-14) motivates it, which is below the complexity threshold. The
  existing Tier 1 ``rate_schedule`` with hand-computed post-cap
  rates reproduces H-14 exactly.
- **``DayCount.ACTUAL_365``** — Australian convention. API sketched
  but no published cents-level worked example with daily accruals
  found.
- **APR / TAEG validation** — Reg Z Appendix J actuarial-method APR.
  Requires modeling all upfront and ongoing fees; significantly
  larger scope than current library.
- **Graduated payment mortgages** — Reg Z Sample H-15 and FHA
  Section 245 Plan III. Bundles with payment-cap mechanics but no
  second published source found beyond the regulatory examples.
- **Offset mortgages** — common in UK and Australia. Requires
  allowing a variable principal balance input, which adds significant
  complexity to the current pure-math approach.
- **Bausparvertrag / Bauspardarlehen** (Germany/Austria) — complex
  product with a savings-phase transition. The library could handle
  the loan phase, but no specific worked example identified.
- **CLI ``summary`` subcommand** — output total interest, payoff
  date, APR. Low priority; the information is derivable from
  ``schedule`` output.

### Unresolved regional gaps

- **Republic of Ireland** — lender disclosures diverge €0.75–€1.12
  with no documented day-count convention. Deferred until a primary
  source publishes the algorithm.
- **UK reversion-to-SVR multi-rate** — needs Tier 1 ARM rate schedule
  plus a UK-specific verifiable example. None found.
- **Germany / *Pfandbrief* tradition** — conceptually important but
  no specific public worked example identified.
- **Pre-1968 American sources beyond FHLBB 1935** — Bodfish 1931 on
  HathiTrust is JS-walled. A digitized B&L annual report from the
  1880s-1920s with a worked schedule would be a major find.

### European regulatory source leads

These regulatory bodies may publish worked examples suitable as
fixtures, but have not yet been investigated in depth:

- **FCA (UK)** — Annual Percentage Rate of Charge (APRC) calculation
  examples using standard UK practices.
- **Finansinspektionen (Sweden)** — "Amorteringskrav" guidelines on
  how serial or mixed loans must be calculated.
- **BaFin / PAngV (Germany)** — "Preisangabenverordnung" effective
  interest rate (Effektivzinssatz) calculation examples for standard
  "Annuitätendarlehen."

## International fixture research (May 2026)

A broad web search across six countries was conducted to find
published worked amortization examples suitable as test fixtures.
All agents were blocked from fetching page content directly, so
findings come from search result snippets only. **Every source
below requires manual browser verification before creating a
fixture.** No numbers should be treated as verified until a human
visits the URL and confirms the published values per CLAUDE.md
Rule 4 (Source verification).

### Tier 1: Complete or near-complete schedules (verify first)

These sources had most or all rows confirmed across multiple
independent search snippets.

**France — expertfiscal.fr (4-year annual annuity)**

- URL: <https://expertfiscal.fr/pret-amortissable-annuites-constantes-calcul/>
- Parameters: €100,000 / 5% / 4 years / annual payments
- Annuity: €28,201.18
- All 4 rows appeared in search snippets (year 1: interest
  €5,000.00, amort €23,201.18, CRD €76,798.82; through year 4:
  CRD €0). Same example confirmed on public.iutenligne.net and
  jybaudot.fr.
- Source type: commercial educational site. Annual periods, not
  monthly.

**Netherlands — Dutch Wikipedia "Annuïteitenlening" (CC-BY-SA)**

- URL: <https://nl.wikipedia.org/wiki/Annu%C3%AFteitenlening>
- Parameters: €100,000 / 4% / 10 years / annual payments
- Annuity: €12,329.09
- ~8 of 10 rows confirmed in search snippets (year 1: interest
  €4,000.00, repayment €8,329.09, remaining €91,670.91; through
  year 9: remaining €11,853.56).
- CC-BY-SA 4.0 license — strongest licensing of any source found.
  Annual periods, not monthly.

**Denmark — Vestergaard teacher notes PDF (6-year annual annuity)**

- URL: <https://www.matematikfysik.dk/mat/noter_tillaeg/tillaeg_annuitetsregning.pdf>
- Parameters: 25,000 kr / 20% / 6 years / annual payments
- Payment (ydelse): 7,518 kr
- All 6 rows confirmed across multiple search snippets (year 1:
  interest 5,000, afdrag 2,518, restgaeld 22,482; through year 6:
  restgaeld 0).
- Freely downloadable PDF. Rounded to whole kr (no øre). The 20%
  rate is pedagogical, not realistic.

**Italy — University of Cagliari PDF (6-year annual annuity)**

- URL: <https://web.unica.it/static/resources/cms/documents/2Ripassodimatematicafinanziaria_1.pdf>
- Parameters: €100,000 / 5% / 6 years / annual payments
- Payment (rata): €19,701.75
- ~5 of 6 rows confirmed in a search snippet (year 1: quota
  interessi €5,000.00, quota capitale €14,701.75, debito residuo
  €85,298.25; through year 6: debito residuo €0). Same example
  appears in Sapienza University (Palestini) slides at
  <https://memotef.web.uniroma1.it/sites/default/files/file%20lezioni/Slides%20MF%202017%20ammortamento.pdf>.
- Potential 1-cent ambiguity in year 2 quota capitale (15,436.83
  vs 15,436.84 across sources) — needs resolution by reading the
  PDF.

### Tier 2: Monthly schedules (partial row confirmation)

**France — MoneyVox (12-month monthly with assurance)**

- URL: <https://www.moneyvox.fr/credit/tableau-amortissement.php>
- Parameters: €10,000 / 5% / 12 months / monthly; assurance
  0.35% = €2.92/month
- Mensualité hors assurance: €856.07
- 3 full rows confirmed (month 1: interest €41.67, capital amorti
  €814.40, CRD €9,185.60; month 2: interest €38.27, capital
  amorti €817.80, CRD €8,367.80; month 3: interest €34.87, CRD
  €7,546.60). Interest for months 4–7 also confirmed (€31.44,
  €28.00, €24.53, €21.04).
- The assurance column (€2.92/mo on initial capital) is exactly
  the ``fee_per_period`` pattern. If the full 12-row table can be
  confirmed, this could be a trigger source for the
  ``fee-per-period-wip`` branch — though it is a commercial site,
  not a regulator or textbook.

**France — Wikipedia fr "Amortissement (finance)" (CC-BY-SA)**

- URL: <https://fr.wikipedia.org/wiki/Amortissement_(finance)>
- Parameters: €1,000 / 12% / 12 months / monthly
- Mensualité: €88.84; total interest: €66.08
- Only the payment anchor and total interest confirmed via search.
  The page reportedly contains a full 12-row table — needs manual
  verification. CC-BY-SA license.

**Netherlands — Fortus.nl (30-year monthly)**

- URL: <https://fortus.nl/kennisbank/rente-en-aflossing-berekenen/>
- Parameters: €200,000 / 3.5% / 30 years / monthly
- Monthly payment: €898.09
- 3 rows confirmed (month 1: interest €583.33, repayment €314.76,
  remaining €199,685.24; month 3: interest €581.49, remaining
  €199,052.97). Unknown how many rows the page publishes.

**Japan — JHF Flat 35 (30-year monthly, single-anchor)**

- URL: <https://www.flat35.com/hajimete/atoz/04.html>
- Parameters: ¥20,000,000 / 1.5% / 30 years / monthly
- Payment: ¥69,024
- Confirmed across multiple independent sources. Government-
  affiliated (JHF). Unknown whether the page shows a row-level
  schedule or only the summary comparison.

**Japan — Aeon Bank (35-year monthly)**

- URL: <https://www.aeonbank.co.jp/column/mortgageloan/kinri/keisan/>
- Parameters: ¥30,000,000 / 1.5% / 35 years / monthly
- Payment: ¥91,855 (ganri kinto / annuity)
- First-month interest ¥37,500 confirmed. Also shows gankin kinto
  (serial) first month payment ¥108,928.

### Tier 3: Single-anchor / partial data

- **South Korea — Banksalad**: ₩100,000,000 / 5% / 20yr =
  ₩659,956/mo. Months 1 and 16 confirmed. URL:
  <https://www.banksalad.com/articles/%EC%9B%90%EA%B8%88-%EA%B7%A0%EB%93%B1-%EC%83%81%ED%99%98-vs-%EC%9B%90%EB%A6%AC%EA%B8%88-%EA%B7%A0%EB%93%B1-%EC%83%81%ED%99%98-%EB%82%98%EC%97%90%EA%B2%8C-%EB%A7%9E%EB%8A%94-%EB%8C%80%EC%B6%9C%EC%83%81%ED%99%98-%EC%A0%84%EB%9E%B5%EC%9D%80>
- **South Korea — KB Capital**: ₩100,000,000 / 3.8% / 96mo =
  ₩1,209,646/mo. Payment anchor only. URL:
  <https://m.kbcapital.co.kr/aboutus/cmpgdnc/finLifeDtl.kbc?blbdSeqno=107839>
- **Denmark — mfgy.dk / RegneRegler.dk**: 12,000 kr / 5% / 4yr
  annual = 3,384.14 kr. 2 rows confirmed. URLs:
  <https://sites.google.com/mfgy.dk/matematikb-niveau/5-procent-og-penge/5-8-annuitetsl%C3%A5n>
  and <https://regneregler.dk/annuitetslaan/>
- **Italy — andreailmatematico.it**: €50,000 / 10% / 4yr annual
  = €15,773.54. 2 rows confirmed. URL:
  <https://andreailmatematico.it/matematica-finanziaria/piani-ammortamento/piano-di-ammortamento-francese-rata-costante/>
- **Italy — Younited Credit (ammortamento italiano / serial)**:
  €10,000 / 4% / 5yr annual = constant principal €2,000. All 5
  rows confirmed but this is serial amortization. URL:
  <https://it.younited-credit.com/glossario/ammortamento-italiano>

### Tier 4: Promising PDFs needing manual download

These are freely downloadable but could not be fetched by agents.

- **South Korea** — KOCW Hansung University lecture (real estate
  finance): <http://kocw-n.xcache.kinxcdn.com/data/document/2023/hansung/leeyoungman0115/9-1.pdf>
- **Italy** — Sapienza MEMOTEF (Palestini slides):
  <https://memotef.web.uniroma1.it/sites/default/files/file%20lezioni/Slides%20MF%202017%20ammortamento.pdf>
- **Italy** — AssoCTU Excel worked example:
  <https://www.assoctu.it/fileadmin/AssoCTU/upload/eventi/documenti/PATTI_2017/Esempio_ammortamento_alla_francese.xlsx>
- **Denmark** — Auerbach "Renter og annuiteter" (45,000 kr /
  5.6% / 7yr):
  <https://www.mathematicus.dk/matematik/kernestof/Renter_og_annuiteter.pdf>
- **Denmark** — Jakobsen & Svenstrup, Aarhus University (Danish
  bond schedules):
  <http://droek2.svenstrup.net/Notater/cashflow.pdf>
- **France** — IUT en ligne (Paronneau, €12,567 / 5.1% / 7yr):
  <https://public.iutenligne.net/mathematiques/mathematiques-financieres/paronneau/amortissements/Chapitre-4/index.html>

### Rounding conventions by country

| Country | Convention | Source |
|---------|-----------|--------|
| Japan | Truncation (切り捨て / floor) to yen | Flat 35 / bank practice |
| South Korea | Truncation (절사 / floor) below 1 won | FSS calculator documentation |
| France / Italy / Netherlands | Standard rounding to cent (likely ROUND_HALF_UP) | Various |
| Denmark | Varies; some sources round to whole kr, others to øre | Vestergaard (whole kr), mfgy.dk (øre) |

Japan and South Korea both use truncation, not ROUND_HALF_UP. If
these countries become fixture targets, a ``ROUND_DOWN`` / floor
rounding mode may be needed in the library.

### Recommended manual verification priority

1. **Dutch Wikipedia** — CC-BY-SA, likely complete 10-row table,
   trivially verifiable in any browser.
2. **French Wikipedia** — CC-BY-SA, check if the "Amortissement
   (finance)" page has a full 12-month table.
3. **expertfiscal.fr** — all 4 rows already confirmed in search
   snippets; visit page to transcribe exact values.
4. **MoneyVox** — if full 12-row table + assurance column confirmed,
   potential ``fee_per_period`` trigger source.
5. **University of Cagliari PDF** — download and verify 6-row table;
   resolve the 1-cent ambiguity.
6. **Vestergaard Danish PDF** — download and verify 6-row table.
7. **JHF Flat 35 page** — check whether row-level schedule data
   exists (would be first Japanese fixture).

### Other sections

- See "Actual/360 commercial loans" below.
- See "Carry-precision textbooks" below for sources that still don't
  match even with `BalanceTracking.CARRY_PRECISION`.

## Carry-precision textbooks

`BalanceTracking.CARRY_PRECISION` shipped in v0.2 — the unrounded
balance is carried internally between rows and per-row figures are
rounded to cents only for display. This matches how Excel's
`PMT`/`IPMT`/`PPMT` worksheet model and most graduate-level CRE
finance textbooks compute amortization. The library's default
remains `BalanceTracking.ROUND_EACH`, matching how most US
residential lenders' statements are printed.

**Validated against:**

- **Geltner et al., *Commercial Real Estate Analysis for Investment,
  Finance, and Development*** (Routledge, online supplement
  9781041081197, Chapter 20 "Mortgage Basics II"). The graduate-level
  CRE finance textbook (lead author MIT-affiliated). Worked CPM
  example: $1M / 12% / 30yr → monthly P&I $10,286.13 and 7 of 9
  published Exhibit 20-6 rows match exactly with
  `BalanceTracking.CARRY_PRECISION`. The 2 unmatched rows (358 and
  360) contain editorial arithmetic typos in the textbook itself.
  See `tests/schedules/geltner_ch20_cpm_1m_1200_360mo.{toml,csv}`
  and `docs/accuracy.md`.

**Still investigated but not matching even with carry-precision:**

- **LibreTexts Business Math** (Olivier), §13.03 "Tamara's dishwasher
  loan" ($895.94 / 5.9% / 6mo). Carry-precision matches the monthly
  payment and total interest; per-row figures still diverge because
  the textbook's algorithm includes a per-line "missing pennies"
  reconciliation that we could not reverse-engineer from the
  published prose. Not committed as a fixture.
- **eCampus Ontario *Mathematics of Finance*** Example 4.3.4
  ($308,000 / 4.62% / 180mo). Carry-precision matches the monthly
  payment; the published "balance after payment 20" still differs by
  a single cent ($283,323.39 published vs $283,323.40 computed).
  Likely an editorial rounding inside the textbook — close enough
  that the per-row tables would mostly match, but not committed as a
  fixture per the "every published value exact" rule.

## Actual/360 commercial loans

`monthly_payment` and `amortization_schedule` both fully support
`DayCount.ACTUAL_360`, including native balloon loans (term shorter
than amortization period via `LoanParams.amortization_period_months`).
Both monthly P&I and balloon-at-term are validated against the Fannie
Mae Multifamily Selling and Servicing Guide §1103 example.

This section retains the conventions analysis for future readers,
along with the sources investigated along the way.

### Background

Actual/360 (also called "365/360") is the dominant interest-accrual
convention for US commercial real-estate, business, and money-market
loans. The standard formula for the period interest is:

> Interest = Principal × AnnualRate × DaysInPeriod / 360

For monthly amortizing loans, "DaysInPeriod" is the **actual number of
calendar days** between consecutive payment dates — typically 28, 29,
30, or 31. Over a non-leap year, total days are 365 and the effective
rate is 365/360 ≈ 1.39% higher than the stated nominal rate. Over a
leap year, 366/360 ≈ 1.67% higher.

This is fundamentally different from 30/360, which fixes every period
at 30 days and ignores calendar effects.

### The payment formula (now validated): Convention A

The library implements **Convention A** for `monthly_payment`:

> Payment = standard closed-form annuity with `r = annual / 12`, no
> bumped rate. The Actual/360 designation affects only how the schedule
> accrues interest, not how the level monthly payment is computed.

This is what Fannie Mae's §1103 calls the "calculated actual/360 fixed
rate payment". The §1103 worked example ($25M / 5.5% / 30yr → DSC
6.8134680% → P&I $141,947.25) uses exactly this formula. Two earlier
candidate conventions, both rejected:

| Convention | Payment formula | Status |
|---|---|---|
| **A. Closed-form, no bump** ✓ | `r = annual / 12` | Adopted; matches Fannie Mae §1103 and PropertyMetrics |
| **B. Bumped-rate** ✗ | `r = annual × 365/360 / 12` | Rejected — gave $25,377.35 vs PropertyMetrics' $25,311.28 and $143,147.75 vs Fannie Mae's implied $141,947.25 |
| **C. Bumped-rate + 30-day schedule** ✗ | bumped + constant 30-day month | Rejected — same payment value as B; no source matched |

### Sources investigated

- [Wikipedia: *Day count convention*](https://en.wikipedia.org/wiki/Day_count_convention)
  — defines the formula `DayCountFactor = ActualDays(Date1, Date2) / 360`
  but gives no full worked amortization example with a monthly payment.
- [PropertyMetrics: "30/360 vs Actual/360 vs Actual/365"](https://propertymetrics.com/blog/30-360-vs-actual-360-vs-actual-365/)
  — only worked example with concrete cents-level numbers found
  ($2.5M / 4% / 10yr / $25,311.28 monthly, month-1 interest $8,611.11
  for January, total interest over 10 years $547,154.46). Convention A.
  Doesn't disclose the calendar start date or the residual balance.

  **A clean Decimal simulation of Convention A reproduces the monthly
  payment ($25,311.28) and month-1 interest ($8,611.11) exactly, and
  comes within $0.02 on the published total interest ($547,154.48
  computed vs $547,154.46 published) when started in January 2021 (or
  any other calendar year whose first 10-year window contains three
  leap years). The 2-cent gap is internal to the published source: the
  source's own numbers are inconsistent — $120 \times \$25{,}311.28$
  payments minus a $2{,}500{,}000 - X$ principal balance reconciles to
  $547,154.46 only if the implied terminal balloon X is $9,800.86, but
  any clean simulation gives X = $9,800.32. The source likely computed
  in float and accumulated sub-cent drift over 120 rows.**

  This is the closest match in the suite. Per the project's "match
  every published value exactly" rule, it still does not qualify as a
  fixture; if/when a source emerges whose own numbers tie out to the
  cent, that source should be the reference for shipping Convention A.
- [Adventures in CRE: "30/360, Actual/365, and Actual/360"](https://www.adventuresincre.com/lenders-calcs/)
  — extensive comparison prose; the side-by-side numerical table was
  not extractable from the page render.
- [Fannie Mae Multifamily Selling and Servicing Guide §1103 — Actual
  Amortization Calculation](https://mfguide.fanniemae.com/node/5286)
  (Effective April 3, 2026) — Tier 2 SARM Loan worked example with
  $25M principal, 5.5% gross note rate, 10-year term, 30-year
  amortization, issue date Dec 1, 2018, first payment Jan 1, 2019.

  Published values:
  - Debt service constant: 6.8134680% → implied monthly P&I $141,947.25.
  - Aggregate principal amortization over 120 payments: $4,114,494.17.
  - Fixed monthly principal installment (after dividing by 120): $34,287.45.

  **Library reproduces both anchors exactly.** The
  `fanniemae_mf_1103_25m_550_360mo` fixture validates the implied
  monthly P&I ($141,947.25), and a `[[expected.balance_anchor]]` entry
  validates the implied balance after 120 payments ($20,885,505.83 =
  $25M − $4,114,494.17). The schedule itself is generated with
  `start_date = 2018-12-01`, full-precision balance tracking, and
  day-counted interest; the per-row cents-rounded values would only
  approximate the aggregate (sum-of-rounded-rows = $4,114,494.11), but
  the **internal full-precision balance** at row 120 rounds to exactly
  $20,885,505.83, which is the cleanest validation anchor.
- [Fannie Mae Multifamily Guide §204.02 A — Actual/360 Interest
  Calculation Method](https://mfguide.fanniemae.com/node/7941) — sibling
  page; gives the formula text but no numerical example.
- [Bank Iowa 365/360 Loan Calculator](https://bankiowa.bank/additional-resources/calculators/365-360-loan-calculator)
  — confirms in prose that "Interest is calculated monthly at 1/360th
  of the annual rate times the number of days in the month on the
  current outstanding balance" (variable-days convention). No worked
  example.
- [Vorys: "365/360 Interest Calculation: Latest Developments in Ohio
  Case Law"](https://www.vorys.com/publication-365-360-Interest-Calculation-Latest-Developments-in-Ohio-Case-Law-Provide-Guidance-in-Interest-Calculation-Methods)
  — legal analysis confirming the 1.389% effective-rate differential;
  no worked numerical example.
- Chandoo Excel forum — quotes `=PMT(0.06,25,1000000)/12 = $6,518.89`,
  but `PMT` with annual rate and 25 periods is unconventional usage
  and the value is not from any of the three conventions above.

### Status

**Shipped:**
- `monthly_payment` for both 30/360 and Actual/360 (validated against
  Fannie Mae §1103: $141,947.25 monthly P&I).
- `amortization_schedule` for Actual/360 with `start_date` and
  full-precision balance tracking.
- Native balloon loans via `LoanParams.amortization_period_months`
  (validated: §1103 implied balloon of $20,885,505.83 at term 120).

**Possible follow-ups** (not blocking; here for the record):
- Per-row Actual/360 schedule fixture validating each of the first
  several months' interest, principal, and balance against a published
  numbered table. The §1103 example only publishes monthly P&I and
  aggregate principal — not row-level data — so we'd need a different
  source. PropertyMetrics' worked example publishes month-1 interest
  ($8,611.11 for January) but the rest of its schedule is not numbered
  publicly.
- Balloon mortgage examples from CMBS prospectus supplements or other
  CRE finance references with full numbered schedules.
