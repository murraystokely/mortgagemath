<p align="center">
  <img src="https://raw.githubusercontent.com/murraystokely/mortgagemath/main/mortgagemath.svg" alt="mortgagemath logo" width="400">
</p>

# mortgagemath

[![tests](https://github.com/murraystokely/mortgagemath/actions/workflows/tests.yml/badge.svg)](https://github.com/murraystokely/mortgagemath/actions/workflows/tests.yml)
[![lint](https://github.com/murraystokely/mortgagemath/actions/workflows/lint.yml/badge.svg)](https://github.com/murraystokely/mortgagemath/actions/workflows/lint.yml)
[![coverage](https://raw.githubusercontent.com/murraystokely/mortgagemath/main/coverage.svg)](https://raw.githubusercontent.com/murraystokely/mortgagemath/main/coverage.svg)
[![PyPI](https://img.shields.io/pypi/v/mortgagemath.svg)](https://pypi.org/project/mortgagemath/)
[![Python 3.11+](https://img.shields.io/pypi/pyversions/mortgagemath.svg)](https://pypi.org/project/mortgagemath/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://static.pepy.tech/badge/mortgagemath/month)](https://pepy.tech/project/mortgagemath)

Cent-accurate mortgage amortization for Python — validated against CFPB, Fannie Mae, and published real-world examples.

## Use Cases

- Fintech / mortgage software
- Loan calculators
- Real-estate underwriting tools
- Audit / reconciliation workflows
- Financial educators
- Anyone frustrated by 1-cent discrepancies

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

Returns a cent-accurate payment and lender-style amortization schedule.

If this solves a problem for you, please star the repo ⭐

## Why This Package?

Most mortgage libraries compute formulas.

Few reproduce lender schedules.

That creates:

- 1-cent discrepancies
- incorrect principal / interest splits
- reconciliation headaches
- wrong final balances
- audit friction

**mortgagemath** solves this with configurable lender rounding, exact payoff balances,
and a robust validation suite to compare calculations against published CFPB regulatory examples,
Fannie Mae publications, and financial literature.

## Why Use mortgagemath?

| Feature | mortgagemath | Typical Python packages |
|--------|---------------|--------------------------|
| Decimal math | ✅ | Sometimes |
| Configurable lender rounding | ✅ | Rare |
| Exact zero final balance | ✅ | Rare |
| Published-source validation | ✅ | No |
| Balloon / commercial loans | ✅ | Rare |
| Full amortization schedule | ✅ | Mixed |

## Compared to Typical Alternatives

Many mortgage libraries rely on floats, limited rounding controls, or do not generate lender-style amortization schedules.

mortgagemath focuses on:

- Decimal math end-to-end
- Configurable lender rounding
- Exact zero ending balances
- Full amortization schedules
- Published-source validation

## Accuracy Validation

Validated against published examples from:

- CFPB sample disclosures
- Fannie Mae multifamily guides
- Geltner et al., *Commercial Real Estate Analysis* (graduate CRE finance text)
- OpenStax textbooks
- LibreTexts examples
- Boundary rounding test cases

See [`docs/accuracy.md`](docs/accuracy.md) for the full source table and
cent-accurate results.

## Reporting a discrepancy

Found a published example or a real lender statement that `mortgagemath`
doesn't reproduce to the cent? Two paths:

- **Reporters / users** — open an issue using the
  [Mortgage example doesn't match](.github/ISSUE_TEMPLATE/mortgage-example.yml)
  template. It walks through the loan parameters and any per-row data
  the source publishes; the discrepancy then either lands in the
  validation suite (if reproducible) or in
  [`docs/future-work.md`](docs/future-work.md) (if not). No need to
  run `pytest` locally.
- **Contributors who can run pytest locally** — see
  [Contributing Test Fixtures](#contributing-test-fixtures) below for
  the direct PR path.

For unrelated bugs or feature requests, use the general
[Bug or feature request](.github/ISSUE_TEMPLATE/bug-or-feature.yml)
template.

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

## Balance Tracking

Different sources propagate the running balance between schedule rows
differently. `mortgagemath` supports both common conventions via the
`balance_tracking` field on `LoanParams`:

| Mode | Algorithm | Used by |
|------|-----------|---------|
| `BalanceTracking.ROUND_EACH` (default) | Each row rounds the balance to cents; next row's interest computes from the rounded balance | Most US residential lenders; CFPB sample disclosures |
| `BalanceTracking.CARRY_PRECISION` | Unrounded balance carried internally; per-row values rounded for display only | Excel-default; graduate-level CRE finance textbooks (Geltner, LibreTexts, eCampus) |

For long-horizon loans the two algorithms diverge by single-digit cents
on each row, with the displayed total interest sometimes drifting by a
few dollars over a 30-year term. Both modes preserve `principal +
interest == payment` per row and land balance at exactly $0.00 on the
final row of a fully-amortizing loan.

```python
from mortgagemath import BalanceTracking, LoanParams, PaymentRounding

# A loan to be compared against a Geltner-style worked schedule
loan = LoanParams(
    principal=Decimal("1000000"),
    annual_rate=Decimal("12"),
    term_months=360,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
    balance_tracking=BalanceTracking.CARRY_PRECISION,
)
```

`ACTUAL_360` schedules always use carry-precision internally (day-counted
interest accrual is only meaningful with full balance precision); the
`balance_tracking` field is ignored in that case.

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
monthly P&I is the standard closed-form annuity value. [Fannie Mae's
Multifamily Selling and Servicing Guide §1103](https://mfguide.fanniemae.com/node/5286)
calls this the "calculated actual/360 fixed rate payment" and uses the
same formula — no 365/360 rate bump (validated against the §1103 worked
example: $25M / 5.5% / 30yr → $141,947.25).

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

## Contributing Test Fixtures

This is the direct-PR path. If you can't run `pytest` locally, the
[Mortgage example doesn't match](.github/ISSUE_TEMPLATE/mortgage-example.yml)
issue template is the easier route — paste the published values and a
maintainer will land the fixture for you.

To add a verified loan as a PR, create two files in `tests/schedules/`:

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
