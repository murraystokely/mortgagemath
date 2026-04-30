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
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/mortgagemath?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/mortgagemath)

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

To verify a fresh install reproduces the same reference values the test suite
validates, run:

```
python -m mortgagemath
```

This recomputes a CFPB sample Closing Disclosure, the Goldstein §10.3 Example 1
carry-precision schedule, and the Fannie Mae §1103 Tier 2 SARM monthly payment
plus balloon-at-term. Exits 0 if every value matches the published source
exactly, 1 otherwise.

## Quick Start

### From Python

```python
from decimal import Decimal
from mortgagemath import LoanParams, periodic_payment, amortization_schedule

loan = LoanParams(
    principal=Decimal("131250"),
    annual_rate=Decimal("4.25"),
    term_months=360,
)

pmt = periodic_payment(loan)         # Decimal("645.68")
sched = amortization_schedule(loan)
print(sched[104].principal)          # Decimal("260.27")
print(sched[104].interest)           # Decimal("385.41")
```

Returns a cent-accurate payment and lender-style amortization schedule.

> Released v0.2.x called this function `monthly_payment`; that name is
> preserved as a permanent alias.  The new `periodic_payment` name
> reads more clearly when non-monthly cadences (weekly, biweekly,
> quarterly) are used.

### From the command line

A built-in CLI (registered as `mortgagemath`, also available as
`python -m mortgagemath`) computes the same numbers without writing a
script:

```sh
# Just the monthly payment
$ mortgagemath payment --principal 131250 --rate 4.25 --term-months 360
645.68

# Full amortization schedule (table by default; --format csv | json)
$ mortgagemath schedule --principal 131250 --rate 4.25 --term-months 360 | head -5
    #         Payment        Interest       Principal         Total Int           Balance
    0            0.00            0.00            0.00              0.00        131,250.00
    1          645.68          464.84          180.84            464.84        131,069.16
    2          645.68          464.20          181.48            929.04        130,887.68
    3          645.68          463.56          182.12          1,392.60        130,705.56
```

Pipe `--format csv` to a file or `--format json` to `jq` for
downstream tooling.  See `mortgagemath --help` and the per-subcommand
help (`mortgagemath schedule --help`) for the full flag surface,
including Canadian semi-annual compounding (`--compounding`),
non-monthly payments (`--payment-frequency`), Actual/360 commercial
loans (`--day-count`, `--start-date`), and ARMs
(`--rate-change EFFECTIVE_PMT:NEW_RATE`).

### Canadian and other non-monthly loans

Canadian *Interest Act* §6 mortgages and any other loan with a
non-monthly compounding or payment frequency:

```python
from mortgagemath import (
    LoanParams, Compounding, PaymentFrequency,
    PaymentRounding, periodic_payment,
)

# Canadian mortgage: $350,100 at j_2 = 4.9%, 3-year term on a
# 20-year amortization, monthly payments.
loan = LoanParams(
    principal=Decimal("350100"),
    annual_rate=Decimal("4.9"),
    term_months=36,
    amortization_period_months=240,
    compounding=Compounding.SEMI_ANNUAL,
    payment_frequency=PaymentFrequency.MONTHLY,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
)
print(periodic_payment(loan))         # Decimal("2281.73") — Olivier §13.4
```

### Adjustable-rate mortgages (ARMs)

Pass a `rate_schedule` of `RateChange` entries.  Each declares the
1-indexed payment at which a new rate takes effect:

```python
from mortgagemath import LoanParams, RateChange, PaymentRounding, amortization_schedule

# 5/1 ARM: $200,000 at 5.7%, term 30 years, with a single rate
# change at month 61 to 7.2%.  recast=True (the default) recomputes
# the level payment over the remaining 300 payments.
loan = LoanParams(
    principal=Decimal("200000"),
    annual_rate=Decimal("5.7"),
    term_months=360,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
    rate_schedule=(
        RateChange(effective_payment_number=61, new_annual_rate=Decimal("7.2")),
    ),
)
sched = amortization_schedule(loan)
print(sched[60].payment)              # Decimal("1160.80") — initial level payment
print(sched[61].payment)              # Decimal("1334.16") — recast at month 61
```

### CLI examples for the harder loan types

```sh
# Canadian j_2 mortgage (semi-annual compounding per Interest Act §6)
$ mortgagemath payment --principal 300000 --rate 5 --term-months 300 \
    --compounding semi_annual \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP
1747.45

# 5/1 ARM with a rate change at month 61
$ mortgagemath schedule --principal 200000 --rate 5.7 --term-months 360 \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP \
    --rate-change 61:7.2 --format csv > arm-schedule.csv

# Fannie Mae §1103 SARM with balloon at term 120
$ mortgagemath schedule --principal 25000000 --rate 5.5 \
    --term-months 120 --amortization-period-months 360 \
    --day-count actual/360 --start-date 2018-12-01 \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP \
    --format json | jq '.[-1].balance'
"20885505.83"
```

`mortgagemath --help` and `mortgagemath <subcommand> --help` document
the full flag surface.  `mortgagemath` with no arguments runs the
post-install self-check (also `mortgagemath selfcheck`).

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
