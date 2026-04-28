<p align="center">
  <img src="mortgagemath.svg" alt="mortgagemath logo" width="400">
</p>

# mortgagemath

[![tests](https://github.com/Peach-Homes-LLC/mortgagemath/actions/workflows/tests.yml/badge.svg)](https://github.com/Peach-Homes-LLC/mortgagemath/actions/workflows/tests.yml)
[![coverage](./coverage.svg)](./coverage.svg)
[![PyPI](https://img.shields.io/pypi/v/mortgagemath.svg)](https://pypi.org/project/mortgagemath/)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/mortgagemath.svg)](https://pypi.org/project/mortgagemath/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/mortgagemath/month)](https://pepy.tech/project/mortgagemath)

Cent-accurate mortgage amortization schedules for Python — validated against CFPB, Fannie Mae, textbooks, and real-world published examples.

## Ideal For

- Fintech / mortgage software
- Loan calculators
- Real-estate underwriting tools
- Audit / reconciliation workflows
- Financial educators
- Anyone frustrated by 1-cent discrepancies

## Why This Package?

Existing Python mortgage packages produce amortization schedules that drift
from what banks actually charge. Rounding errors in payment computation,
interest calculation, and balance tracking compound over the life of a loan,
resulting in off-by-one-cent discrepancies in interest and principal that grow
more noticeable over time.

**mortgagemath** takes a different approach: instead of trusting the math alone,
we validate against a test suite of fixtures drawn from published sources —
CFPB regulatory examples, open-licensed finance textbooks, and synthetic
loans constructed to exercise specific rounding boundaries (half-cent interest,
ceiling-vs-half-up payments). Each fixture declares its provenance.

The library uses iterative balance tracking with configurable rounding
conventions, adjusts the final payment to land the balance at exactly zero,
and guarantees that `principal + interest = payment` for every installment.

## Installation

```
pip install mortgagemath
```

Requires Python 3.11+. Zero runtime dependencies -- only the standard library
(`decimal`, `dataclasses`, `enum`).

## Quick Start

```python
from decimal import Decimal
from mortgagemath import LoanParams, monthly_payment, amortization_schedule

loan = LoanParams(
    principal=Decimal("131250"),
    annual_rate=Decimal("4.25"),
    term_months=360,
)

pmt = monthly_payment(loan)          # Decimal("645.68")
sched = amortization_schedule(loan)
print(sched[104].principal)          # Decimal("260.27")
print(sched[104].interest)           # Decimal("385.41")
```

## Rounding Conventions

Banks round the monthly payment and each month's interest to the nearest cent,
but the rounding convention varies by lender. `mortgagemath` makes this explicit
and configurable:

```python
from mortgagemath import LoanParams, PaymentRounding

loan = LoanParams(
    principal=Decimal("131250"),
    annual_rate=Decimal("4.25"),
    term_months=360,
    payment_rounding=PaymentRounding.ROUND_UP,       # default
    interest_rounding=PaymentRounding.ROUND_HALF_UP,  # default
)
```

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `payment_rounding` | `ROUND_UP` | Monthly payment rounded up to nearest cent (ceiling) |
| `interest_rounding` | `ROUND_HALF_UP` | Monthly interest rounded to nearest cent (standard) |

Supported rounding modes for either field: `ROUND_UP` (ceiling), `ROUND_HALF_UP`,
and `ROUND_HALF_EVEN` (banker's rounding). The defaults match the conventions
used in the CFPB sample disclosures and most US residential mortgage servicers
we have validated against. If your lender uses a different convention, you can
override them per-loan.

## Day Count Conventions

US residential mortgages use 30/360 (each month is treated as 30 days, each
year as 360); US commercial loans often use Actual/360 (interest accrues
on the actual calendar days in each month, divided by 360).

```python
from datetime import date
from mortgagemath import DayCount

residential = LoanParams(
    principal=Decimal("200000"),
    annual_rate=Decimal("6"),
    term_months=360,
    day_count=DayCount.THIRTY_360,   # default
)

commercial_balloon = LoanParams(             # 10-yr SARM on 30-yr amort
    principal=Decimal("25000000"),
    annual_rate=Decimal("5.5"),
    term_months=120,                          # 10 years of payments
    amortization_period_months=360,           # closed-form on 30-yr basis
    day_count=DayCount.ACTUAL_360,
    start_date=date(2018, 12, 1),
)
```

`monthly_payment()` works identically for both day-counts: the level
monthly P&I is the standard closed-form annuity value. Fannie Mae's
Multifamily Selling and Servicing Guide §1103 calls this the
"calculated actual/360 fixed rate payment" and uses the same formula —
no 365/360 rate bump (validated against the §1103 worked example:
$25M / 5.5% / 30yr → $141,947.25).

`amortization_schedule()` produces different per-row figures by mode:

| Mode | Period interest | Balance tracking |
|---|---|---|
| `THIRTY_360` (default) | `balance × rate / 12` (constant) | round-each-balance |
| `ACTUAL_360` | `balance × rate × days_in_month / 360` (variable) | full-precision internal, displayed values rounded to cents |

`ACTUAL_360` requires `start_date` (the issue date / first
interest-accrual period). Period 1 covers the calendar month containing
that date; the first payment is due on the same day-of-month one month
later. This matches the Fannie Mae §1103 example: issue date
`2018-12-01` → period 1 spans December 2018 (31 days) → first payment
January 1, 2019. Validated against §1103's published aggregate
principal over 120 payments ($4,114,494.17, equivalent to a balance of
$20,885,505.83 at row 120).

For commercial loans where the term is shorter than the amortization
period — e.g. a 10-year SARM on a 30-year amortization basis — set
`amortization_period_months` to the longer value. The closed-form
payment is computed against `amortization_period_months`; the
schedule produces `term_months` rows, and the final row's `balance`
is the **balloon** the borrower owes alongside the last regular
payment. Per the Fannie Mae §1103 example, $25M / 5.5% / `term_months
= 120` / `amortization_period_months = 360` / `start_date =
2018-12-01` produces a $141,947.25 monthly P&I for 120 months and a
balloon of $20,885,505.83 at term — both validated to the cent.

## Schedule Guarantees

Every schedule produced by `amortization_schedule()` satisfies these invariants,
enforced by the test suite across many loan configurations:

- `principal + interest == payment` for every installment
- Final balance is exactly `Decimal("0.00")`
- Balance decreases monotonically
- Sum of all principal payments equals the original loan amount
- `total_interest` accumulates correctly across all payments

## API Reference

### `LoanParams`

Frozen dataclass defining a fixed-rate mortgage.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `principal` | `Decimal` | required | Original loan amount |
| `annual_rate` | `Decimal` | required | Annual interest rate as percent (e.g. `Decimal("4.25")` for 4.25%) |
| `term_months` | `int` | required | Loan term in months |
| `day_count` | `DayCount` | `THIRTY_360` | Day count convention |
| `payment_rounding` | `PaymentRounding` | `ROUND_UP` | How to round the monthly payment |
| `interest_rounding` | `PaymentRounding` | `ROUND_HALF_UP` | How to round each month's interest |

### `monthly_payment(loan: LoanParams) -> Decimal`

Calculate the monthly principal and interest payment.

### `amortization_schedule(loan: LoanParams) -> list[Installment]`

Generate the full amortization schedule. Returns a list of `Installment`
objects from payment 0 (initial state) through the final payment.

### `Installment`

Frozen dataclass for a single payment.

| Field | Type | Description |
|-------|------|-------------|
| `number` | `int` | Payment number (0 = initial state) |
| `payment` | `Decimal` | Total payment amount |
| `interest` | `Decimal` | Interest portion |
| `principal` | `Decimal` | Principal portion |
| `total_interest` | `Decimal` | Cumulative interest paid through this payment |
| `balance` | `Decimal` | Remaining balance after this payment |

## Test Suite

The test suite has three layers:

1. **Payment unit tests** -- edge cases, both day-count methods, rounding modes
2. **Schedule invariants** -- structural properties verified across 8 different
   loan configurations ($50k--$500k, 3%--8.5%, 10--30yr terms)
3. **Authoritative-source fixtures** -- paired TOML (loan parameters) + CSV
   (payment schedule) fixtures, auto-discovered by pytest. Each fixture
   declares its `source.kind`: regulatory examples (CFPB sample disclosures),
   open-licensed textbook worked examples, calculator output, synthetic
   boundary loans, or bank statements.

See `tests/schedules/README.md` for the full schema and the list of supported
`kind` values.

### Validated Against

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
[`docs/future-work.md`](docs/future-work.md).

## Comparison with Other Python Implementations

Existing Python packages take three approaches, none of which produces
cent-accurate schedules that match how lenders actually print
amortization tables.

### `numpy_financial.pmt` / `ipmt` / `ppmt`

Float-based; no rounding control. The function returns a negative
floating-point value (cash-flow convention) and leaves rounding entirely
to the caller. Two issues for cent-accurate work:

1. **Float drift.** Long-term schedules accumulate sub-cent error in the
   payment value itself; the typical user fix is `round(abs(npf.pmt(...)), 2)`
   which uses Python's banker's-rounding (`HALF_EVEN`) regardless of what
   the lender actually does.
2. **No support for `ROUND_UP`.** The OpenStax §6.8 examples explicitly
   document the US-residential convention "payment to lenders is always
   rounded up to the next penny." `numpy_financial` + `round()` does not
   produce that — it gives the wrong cent on **5 of 15** source-attributed
   fixtures in this suite.

   Concrete example (OpenStax §6.8 car loan, $28,500 / 3.99% / 5yr):

   ```python
   import numpy_financial as npf
   round(abs(npf.pmt(0.0399/12, 60, 28500)), 2)   # → 524.74  (wrong)
   ```

   The textbook value is **$524.75** because the section explicitly uses
   ROUND_UP. To get this with `numpy_financial`, the user must skip
   Python's `round()` and apply Decimal-based ceiling rounding manually.
   `mortgagemath` puts that mode in the type system:

   ```python
   from decimal import Decimal
   from mortgagemath import LoanParams, monthly_payment
   monthly_payment(LoanParams(
       principal=Decimal("28500"), annual_rate=Decimal("3.99"), term_months=60
   ))                                              # → Decimal("524.75")
   ```

### `mortgage` (PyPI)

Uses `Decimal` (good), but does not round per-row. The schedule's
`payment`, `interest`, `principal`, and `balance` are 25+-digit Decimals;
the final balance lands at something like `-3.4E-21` rather than exactly
`$0.00`, and the per-row invariant `principal + interest == payment`
holds only at full precision, not at the cent level a real bank
statement prints.

### `amortization` (PyPI)

Float-based, single-function: `calculate_amortization_amount` returns a
single rounded float. No schedule generation, no rounding control. On
the OpenStax car loan above it returns `524.74` — the same wrong cent
as `numpy_financial`.

### What `mortgagemath` does differently

- **`Decimal` end-to-end.** No floats anywhere in the payment or schedule
  computation. Everything quantizes to two decimal places at explicitly
  declared rounding-mode boundaries.
- **Rounding mode is a type, not a convention.** `PaymentRounding.ROUND_UP`,
  `ROUND_HALF_UP`, `ROUND_HALF_EVEN` are first-class enum values; the
  fixtures table above shows precisely which mode each cited source uses.
- **Final-payment adjustment guarantees zero balance.** `principal + interest
  == payment` holds in every row; final balance is exactly `Decimal("0.00")`.
- **No design borrowed from these packages.** Each one falls short of the
  invariants this library is meant to provide; `mortgagemath` was written
  to fill that gap. The closed-form annuity formula it shares with
  `numpy_financial` is standard finance, not a borrowed pattern.

### Contributing Test Fixtures

To add a verified loan, create two files in `tests/schedules/`:

**`example_30yr_50_150000.toml`** (loan parameters):
```toml
[loan]
principal = "150000.00"
annual_rate = "5.0"
term_months = 360
day_count = "30/360"
payment_rounding = "ROUND_UP"
interest_rounding = "ROUND_HALF_UP"

[source]
kind = "regulatory_example"
country = "US"
label = "30yr_conventional_5pct_150k"
url = "https://example.gov/path/to/published/example"

[expected]
monthly_payment = "805.24"
```

**`example_30yr_50_150000.csv`** (full or partial schedule):
```csv
payment,payment_amount,principal,interest,balance
1,805.24,180.24,625.00,149819.76
2,805.24,180.99,624.25,149638.77
```

Do not include property addresses, lender names, or other PII. For
`statement`-kind fixtures, also include `verified_by` and `verified_date`.

## License

MIT

If this saved you time, please star the repo ⭐
