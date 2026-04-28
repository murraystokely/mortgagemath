# Accuracy Validation

Every loan listed below is reproduced **exactly** by the library — monthly
payment plus any per-row or cumulative figure the source attests to. The
"Pmt rounding" column shows the rounding mode the source's published
payment requires; many sources do not state a mode explicitly, in which
case the cell shows the mode under which the library matches the printed
value (where multiple modes give the same cent, the column says "any").

| Source | Loan | Monthly P&I | Pmt rounding | Int rounding |
|---|---|---|---|---|
| [CFPB H-25(B) sample Closing Disclosure](https://files.consumerfinance.gov/f/201403_cfpb_closing-disclosure_cover-H25B.pdf) | $162,000 / 3.875% / 30yr | $761.78 | `HALF_UP` | `HALF_UP` |
| [Fannie Mae Multifamily Guide §1103, Tier 2 SARM example](https://mfguide.fanniemae.com/node/5286) ³ | $25,000,000 / 5.5% / 10yr term, 30yr amort, Actual/360 | $141,947.25 + $20,885,505.83 balloon | `HALF_UP` | `HALF_UP` |
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

Sources investigated but rejected (because at least one published value
could not be matched exactly) are documented in
[`future-work.md`](future-work.md).
