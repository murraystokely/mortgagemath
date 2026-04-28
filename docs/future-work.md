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

- **Various Canadian textbook examples** (Maksim's Apartment, the
  Olivers, the Chans, Kerry's Toyota Rav4). Use the semi-annual
  compounding required by Canadian mortgage law (the periodic rate is
  derived from a semi-annually-compounded nominal rate, not from
  monthly compounding). The library uses monthly compounding only.
- **Kerry's Toyota Rav4** specifically also chose a non-actuarial
  whole-dollar payment ($2,691 instead of the closed-form $2,690.05),
  which puts the loan outside the closed-form annuity model.
- **William Hart, *Mathematics of Investment*** (1924, archive.org)
  — worked example uses mill-precision (3 decimals), incompatible with
  the library's cent-rounding.

## Possible future work

- Investigate whether a configurable `BalanceTracking.CARRY_PRECISION`
  mode could be designed to match the LibreTexts dishwasher schedule
  (or any other authoritative source whose algorithm is fully
  specified). Past investigation rejected this — the textbooks we
  could read used per-line reconciliations we could not pin down — but
  if a new source emerges with a fully reproducible carry-precision
  algorithm, the design should be reconsidered.
- Investigate semi-annual / annual compounding to support Canadian
  mortgages and certain bond/annuity examples.
- See "Actual/360 commercial loans" below.

## Actual/360 commercial loans

`monthly_payment` supports `DayCount.ACTUAL_360`, validated against the
Fannie Mae Multifamily Selling and Servicing Guide §1103. Schedule
generation (`amortization_schedule`) is still deferred — the
`LoanParams` dataclass does not yet carry a `start_date`, and the
library's amortizing-loan contract (final balance == 0) does not
match commercial loans where the term is shorter than the amortization
period (a balloon residual remains at term).

This section explains the conventions, what the §1103 worked example
told us, and the design questions still open for full schedule support.

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

  **Library reproduces $141,947.25 exactly via the standard closed-form
  annuity formula** — that is the value validated by the
  `fanniemae_mf_1103_25m_550_360mo` fixture. A standalone Decimal
  simulation also reproduces $4,114,494.17 to the cent (period 1 = Dec
  2018, full-precision payment, full-precision day-counted interest);
  this validates Convention A's schedule mechanics, but the library
  cannot ship that schedule until `LoanParams` carries a `start_date`
  field and `amortization_schedule` accepts a non-zero terminal balance
  (balloon).
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

### Design questions still open for schedule generation

1. **Calendar dates on `LoanParams`.** Convention A's schedule requires
   knowing the actual days in each month, which requires either a
   `start_date` field on `LoanParams` or per-period day arrays. The
   Fannie Mae §1103 example used issue date Dec 1, 2018 and first
   payment Jan 1, 2019 — period 1 covers December 2018 (the issue-date
   month).
2. **Terminal-balance handling.** Commercial Actual/360 loans typically
   amortize on a longer schedule than their term (e.g., 30-year
   amortization with 10-year term and balloon). The library's current
   `Installment`-based contract assumes balance ends at exactly $0.00 —
   needs to either accept a balloon residual or require the user to
   declare the intended resolution.
3. **Schedule API surface.** `amortization_schedule` currently produces
   a complete amortizing schedule. For commercial use the library may
   need to produce one of: full amortizing schedule (all payments, zero
   balance at amortization period), term-only schedule (payments through
   loan term, balloon at end), or both modes.
4. **Validated test fixture for the schedule.** We have an internally
   validated standalone simulation that reproduces Fannie Mae's
   aggregate principal $4,114,494.17 to the cent. Once schedule
   generation ships, the §1103 example becomes the corresponding
   row-level fixture.

If a reader knows of a federal regulator, GSE, or commercial-banking
textbook publication that provides a fully numbered Actual/360
amortization schedule (calendar dates plus per-month interest, principal,
and balance values, with explicitly stated terminal balance), please
open an issue with the link.
