# Accuracy Validation

Every loan listed below is reproduced **exactly** by the library — monthly
payment plus any per-row or cumulative figure the source attests to. The
"Pmt rounding" column shows the rounding mode the source's published
payment requires; many sources do not state a mode explicitly, in which
case the cell shows the mode under which the library matches the printed
value (where multiple modes give the same cent, the column says "any").

| Source | Loan | Periodic P&I | Pmt rounding | Int rounding |
|---|---|---|---|---|
| [CFPB H-25(B) sample Closing Disclosure](https://files.consumerfinance.gov/f/201403_cfpb_closing-disclosure_cover-H25B.pdf) | $162,000 / 3.875% / 30yr | $761.78 | `HALF_UP` | `HALF_UP` |
| [Fannie Mae Multifamily Guide §1103, Tier 2 SARM example](https://mfguide.fanniemae.com/node/5286) ³ | $25,000,000 / 5.5% / 10yr term, 30yr amort, Actual/360 | $141,947.25 + $20,885,505.83 balloon | `HALF_UP` | `HALF_UP` |
| [Reg Z, 12 CFR Part 1026, Appendix H, Sample H-14 (Variable-Rate Mortgage)](https://www.ecfr.gov/current/title-12/chapter-X/part-1026/appendix-Appendix%20H%20to%20Part%201026) ⁷ | $10,000 / 17.41% initial / 30yr 1/1 ARM (1-yr CMT + 3pp, 2pp annual cap, 5pp lifetime cap) | $145.90 + 14 annual recasts through year 15 | `HALF_UP` | `HALF_UP` |
| [Geltner et al., *Commercial RE Analysis*, Ch 20 Exhibit 20-6 (CPM)](https://s3-eu-west-1.amazonaws.com/s3-euw1-ap-pe-ws4-cws-documents.ri-prod/9781041076391/online-chapters/9781041081197_Online_content.pdf) ⁴ | $1,000,000 / 12% / 30yr | $10,286.13 | `HALF_UP` | `HALF_UP` (carry-precision) |
| [Goldstein et al., *Finite Mathematics and Its Applications* (12 ed.), §10.3 Ex 1 + Table 1](https://www.pearsonhighered.com/assets/samplechapter/0/1/3/4/0134437764.pdf) ⁵ | $563 / 12% / 5mo | $116.00 | `HALF_UP` | `HALF_UP` (carry-precision) |
| [Olivier *Business Math* §13.4 — Chans first term](https://math.libretexts.org/Bookshelves/Applied_Mathematics/Business_Math_(Olivier)/13:_Understanding_Amortization_and_its_Applications/13.04:_Special_Application_-_Mortgages) ⁶ | $350,100 / j_2 = 4.9% / 3yr term, 20yr amort, monthly | $2,281.73 + balloon $316,593.49 | `HALF_UP` | `HALF_UP` (semi-annual) |
| Olivier *Business Math* §13.4 — Chans renewal ⁶ | $316,593.49 / j_2 = 5.85% / 17yr / monthly | $2,440.73 | `HALF_UP` | `HALF_UP` (semi-annual) |
| [eCampus Ontario *Mathematics of Finance* §4.4.1 — first term](https://ecampusontario.pressbooks.pub/financemath/chapter/4-4-mortgages-formula-approach/) ⁶ | $297,500 / j_2 = 3.8% / 3yr term, 20yr amort, **quarterly** | $5,317.62 + balloon $265,830.61 | `HALF_UP` | `HALF_UP` (semi-annual, quarterly) |
| eCampus Ontario *Mathematics of Finance* §4.4.1 — renewal ⁶ | $265,830.61 / j_2 = 2.5% / 17yr / quarterly | $4,807.70 | `HALF_UP` | `HALF_UP` (semi-annual, quarterly) |
| [MS State Extension P3920](https://extension.msstate.edu/sites/default/files/publications/P3920_web.pdf) | $100,000 / 7% / 30yr | $665.30 | `HALF_UP` | `HALF_UP` |
| [OpenStax *Contemporary Mathematics* §6.8 — car](https://openstax.org/books/contemporary-mathematics/pages/6-8-the-basics-of-loans) ¹ | $28,500 / 3.99% / 5yr | $524.75 | `ROUND_UP` | `HALF_UP` |
| [OpenStax *Contemporary Mathematics* §6.8 — home](https://openstax.org/books/contemporary-mathematics/pages/6-8-the-basics-of-loans) ¹ | $136,700 / 5.75% / 15yr | $1,135.18 | `ROUND_UP` | `HALF_UP` |
| [OpenStax *Contemporary Mathematics* §6.12, Ex 6.110](https://openstax.org/books/contemporary-mathematics/pages/6-12-renting-and-homeownership) | $132,650 / 4.8% / 30yr | $695.97 | any | `HALF_UP` |
| [OpenStax *Contemporary Mathematics* ch6 AK 6.36](https://openstax.org/books/contemporary-mathematics/pages/chapter-6) | $23,660 / 4.76% / 5yr | $443.90 | any | `HALF_UP` |
| OpenStax *Contemporary Mathematics* ch6 AK 6.78.1 | $17,950 / 7.5% / 10yr | $213.07 | any | `HALF_UP` |
| OpenStax *Contemporary Mathematics* ch6 AK 6.78.2 | $33,760 / 4.3% / 20yr | $209.96 | any | `HALF_UP` |
| OpenStax *Contemporary Mathematics* ch6 AK 6.100.1 | $18,325 / 6.75% / 4yr | $436.70 | `ROUND_UP` | `HALF_UP` |
| OpenStax *Contemporary Mathematics* ch6 AK 6.100.2 | $41,633 / 3.9% / 6yr | $649.47 | `ROUND_UP` | `HALF_UP` |
| OpenStax *Contemporary Mathematics* ch6 AK 6.110 | $153,899 / 4.21% / 20yr | $949.72 | any | `HALF_UP` |
| OpenStax *Contemporary Mathematics* ch6 AK 6.114 | $159,195.50 / 5.75% / 30yr | $929.03 | `ROUND_UP` | `HALF_UP` |
| [Las Positas College §8.05, Ex 1](https://math.libretexts.org/Courses/Las_Positas_College/Math_for_Liberal_Arts/08:_Consumer_Mathematics/8.05:_Amortized_Loans) | $15,000 / 9% / 5yr | $311.38 | any | `HALF_UP` |
| Las Positas College §8.05, Ex 3 | $18,000 / 2% / 5yr | $315.50 | any | `HALF_UP` |
| [Wikipedia: *Mortgage calculator*](https://en.wikipedia.org/wiki/Mortgage_calculator) | $200,000 / 6.5% / 30yr | $1,264.14 | any | `HALF_UP` |
| Synthetic — half-cent boundary at month 1 (HALF_UP) | $100,001.25 / 4.8% / 30yr | $524.67 | `HALF_UP` | `HALF_UP` |
| Synthetic — half-cent boundary at month 1 (ROUND_UP) | $100,001.25 / 4.8% / 30yr | $524.68 | `ROUND_UP` | `HALF_UP` |
| Synthetic — half-cent boundary at month 1 (HALF_EVEN) | $100,001.25 / 4.8% / 30yr | $524.67 | `HALF_UP` | `HALF_EVEN` ² |

¹ OpenStax §6.8 explicitly states that "payment to lenders is always
rounded up to the next penny" — this is the convention used by US
residential lenders and corresponds to `ROUND_UP` in `mortgagemath`.

² This synthetic loan is constructed so that month-1 unrounded interest
equals exactly $400.005 — a half-cent boundary that distinguishes
`HALF_UP` ($400.01) from `HALF_EVEN` ($400.00).

³ The Fannie Mae §1103 worked example covers a Tier 2 SARM Loan: $25M
principal, 10-year term, 30-year amortization basis, Actual/360, issue
date 2018-12-01. Fannie Mae publishes a debt service constant
(6.8134680% × $25M ÷ 12 = $141,947.25 monthly P&I) and an aggregate
principal amortization of $4,114,494.17 over the 120-month SARM term —
which implies a balloon of $20,885,505.83 at the end of month 120. The
library reproduces both anchors exactly with `term_months = 120,
amortization_period_months = 360, day_count = ACTUAL_360, start_date =
2018-12-01`. The closed-form annuity formula uses the 30-year basis;
Fannie Mae does **not** apply a 365/360 rate bump — the day-count
convention only affects how the schedule accrues interest each month.

⁴ Geltner et al. is a graduate-level commercial real-estate finance
textbook (lead author MIT-affiliated). Chapter 20 Exhibit 20-6 publishes
9 specific schedule rows for the Constant-Payment Mortgage example;
the library reproduces 7 of them exactly under
`BalanceTracking.CARRY_PRECISION` + `ROUND_HALF_UP`. The 2 unmatched
rows (358 and 360) contain editorial inconsistencies in the textbook
where `principal + interest != payment` by 1 cent — verifiable
arithmetic (`9983.61 + 302.51 = 9983.62 ≠ 10286.13` for row 358;
`10184.28 + 101.84 = 10286.12 ≠ 10286.13` for row 360). The library
returns the mathematically-consistent values; those two rows are
omitted from the fixture CSV but documented in
`tests/test_schedule.py::TestGeltnerCPM`.

⁵ Goldstein et al. is a widely-adopted college-level *Finite
Mathematics and Its Applications* textbook (Pearson, 12th edition).
Section 10.3 opens with a 5-row amortization "Table 1" before any
formulas are introduced, so every cell of the schedule is published
explicitly — interest, principal, and unpaid balance for each of the
5 months. The library reproduces all 15 cells exactly (plus the
$116.00 monthly payment and a final balance of zero) under
`BalanceTracking.CARRY_PRECISION`, the same Excel-default mode that
matches Geltner above. Section 10.3 Example 2 (a $112,475 / 9% / 30yr
mortgage with $905.00 monthly P&I) matches the library's monthly
payment exactly, but its published balances are computed via the
closed-form annuity present-value formula with the rounded $905
payment, which drifts a few cents from any row-by-row schedule (3¢ on
the balance after payment 312); for that reason the per-row anchors
are not committed.

⁷ Reg Z (12 CFR Part 1026 Appendix H Sample H-14) is a regulatory
worked example of an Adjustable-Rate Mortgage. Per $10,000 the table
publishes 15 years of historical rate adjustments under actual
1-year CMT values from 1982–1996; the periodic 2pp annual cap binds
at years 2 and 4 (1983, 1985), and the 5pp symmetric lifetime cap
binds from year 5 onward (1986–1996). The library reproduces all
published anchors — year-1 P&I $145.90, year-end balances
$9,989.37 / $9,969.66 / $9,945.51 / $9,903.70 / $9,848.94, and the
year-15 terminal balance $8,700.37 — exactly under
``BalanceTracking.ROUND_EACH`` + ``ROUND_HALF_UP``. The
year-by-year recast formula matches Reg Z's annual-payment-
adjustment language, including the years where the lifetime cap
holds the rate fixed but the payment still recasts on the new
remaining balance. The fixture's ``[[loan.rate_schedule]]`` entries
encode the post-cap rates explicitly; the cap-derivation table is
documented in the fixture TOML's ``notes`` field. A separate
``IndexedRateSchedule`` API that derives post-cap rates from raw
index history was considered but deferred — only one published
source motivates it today, falling below the project's
complexity-threshold rule for adding new modes.

⁶ The Olivier *Business Math* (CC-BY-NC-SA, LibreTexts) and eCampus
Ontario *Mathematics of Finance* (CC-BY 4.0) Canadian-mortgage worked
examples are reproduced under `Compounding.SEMI_ANNUAL` — the
*Interest Act* §6 convention requiring rates be quoted as
semi-annually compounded. The library derives the periodic (monthly
or quarterly) rate as `(1 + j_2/200)^(2/payments_per_year) - 1` and
the schedule then runs as a standard 30/360 round-each amortization.
The "Chans" pair models the typical Canadian flow: a fixed-term
(3 years) mortgage on a longer amortization basis (20 years), with
the unpaid balance at end of term renewed at a new rate. The
"eCampus 4.4.1" pair is identical in structure but uses **quarterly**
payments, exercising the new `PaymentFrequency.QUARTERLY` cadence.

Sources investigated but rejected (because at least one published value
could not be matched exactly) are documented in
[`future-work.md`](future-work.md).
