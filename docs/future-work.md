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

`DayCount.ACTUAL_360` exists in the public enum but every entry point
that takes a `LoanParams` raises `NotImplementedError` if it sees it.
This section explains why and lays out the design questions that must
be answered before the feature can ship.

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

### Why we don't ship a single canonical formula

Several conventions coexist in the wild for the **monthly payment**
that goes with an Actual/360 schedule:

| Convention | Payment formula | Schedule | Result at term |
|---|---|---|---|
| **A. 30/360-equivalent payment** | Closed-form with `r = annual / 12` | Each month uses actual days × rate / 360 | Loan **does not** fully amortize; small balloon residual remains at term (≈1.39% × residual interest accrual annually) |
| **B. Bumped-rate payment** | Closed-form with `r = annual × 365/360 / 12` | Each month uses actual days × rate / 360 | Loan amortizes approximately, with sub-cent residual reconciled into the final payment (depends on how leap years align with the term) |
| **C. Constant-day approximation** | Closed-form with `r = annual × 365/360 / 12` | Each month uses 30 days × rate / 360 (i.e. 30/360 with bumped rate) | Loan fully amortizes deterministically (no calendar dependency) |

Convention C is the simplest and is what the library's previous
implementation of `monthly_payment` for Actual/360 used. We removed it
because we could not find an authoritative published example whose
quoted payment matched that formula. The example most often cited
(PropertyMetrics, $2.5M / 4% / 10yr, monthly $25,311.28) uses
Convention A — its quoted payment equals the 30/360 closed-form value
to the cent, and its quoted total interest of $547,154.46 implies a
~$9,800 residual balloon at month 120.

### Sources investigated

- [Wikipedia: *Day count convention*](https://en.wikipedia.org/wiki/Day_count_convention)
  — defines the formula `DayCountFactor = ActualDays(Date1, Date2) / 360`
  but gives no full worked amortization example with a monthly payment.
- [PropertyMetrics: "30/360 vs Actual/360 vs Actual/365"](https://propertymetrics.com/blog/30-360-vs-actual-360-vs-actual-365/)
  — only worked example with concrete cents-level numbers found
  ($2.5M / 4% / 10yr / $25,311.28 monthly, month-1 interest $8,611.11
  for January). Convention A. Doesn't disclose the calendar start date
  or the residual balance after month 120.
- [Adventures in CRE: "30/360, Actual/365, and Actual/360"](https://www.adventuresincre.com/lenders-calcs/)
  — extensive comparison prose; the side-by-side numerical table was
  not extractable from the page render.
- [Fannie Mae Multifamily Guide §204.02 A — Actual/360](https://mfguide.fanniemae.com/node/7941)
  — references the methodology in its table of contents but the
  rendered page did not surface specific worked-example numbers.
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

### Design questions to answer before implementing

1. **Which payment-derivation convention?** A, B, or C? An authoritative
   published source must demonstrate the chosen formula with reproducible
   numerics.
2. **Calendar dates on `LoanParams`.** Conventions A and B require knowing
   the actual days in each month, which requires either a `start_date`
   field or per-period day arrays. Convention C does not.
3. **Terminal-balance handling.** Convention A produces a balloon residual.
   Should the schedule end with that residual, or should the final
   payment absorb it, or should we require the user to declare the
   intended resolution?
4. **Leap years.** Convention B's amortization is exact only in
   non-leap years. Real schedules straddle leap years — does the final
   payment absorb the leap-year extra interest?
5. **Validation.** No fixture lands in the suite until we identify a
   published worked example whose every numeric value (payment, every
   per-month interest, every balance, totals, terminal balance) the
   library reproduces exactly. Without such a source, we should not
   ship Actual/360 support.

If a reader knows of a federal regulator, GSE, or commercial-banking
textbook publication that provides a fully numbered Actual/360
amortization schedule (with calendar dates and either no residual or
an explicitly stated balloon), please open an issue with the link.
