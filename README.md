<p align="center">
  <img src="mortgagemath.svg" alt="mortgagemath logo" width="400">
</p>

# mortgagemath

Correct mortgage amortization calculations, validated against published
authoritative sources.

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
year as 360). US commercial loans often use Actual/360 (actual days in month,
360-day year), which produces a higher effective rate.

```python
from mortgagemath import DayCount

residential = LoanParams(
    principal=Decimal("200000"),
    annual_rate=Decimal("6"),
    term_months=360,
    day_count=DayCount.THIRTY_360,   # default
)

commercial = LoanParams(
    principal=Decimal("200000"),
    annual_rate=Decimal("6"),
    term_months=240,
    day_count=DayCount.ACTUAL_360,
)
```

Note: `amortization_schedule()` currently supports 30/360 only.
`monthly_payment()` supports both day count conventions.

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

Every published value from these sources is reproduced exactly by the library
(monthly payment, and any per-row or cumulative figures the source attests
to). Sources where the library matched only a subset have been removed; this
list contains only full matches.

**Regulatory and government publications**

- [CFPB sample H-25(B) Closing Disclosure](https://files.consumerfinance.gov/f/201403_cfpb_closing-disclosure_cover-H25B.pdf)
  — $162,000 / 3.875% / 30yr / $761.78 (HALF_UP)
- [Mississippi State University Extension Service Publication P3920, "Paying Off Your Loans: Loan Amortization"](https://extension.msstate.edu/sites/default/files/publications/P3920_web.pdf)
  — $100,000 / 7% / 30yr / $665.30 (HALF_UP)

**Open-licensed textbooks**

- [OpenStax *Contemporary Mathematics*](https://openstax.org/books/contemporary-mathematics/) (CC BY 4.0)
  - § 6.8 "The Basics of Loans" — car loan ($28,500 / 3.99% / 5yr) and home
    loan ($136,700 / 5.75% / 15yr); the section also documents that "payment
    to lenders is always rounded up to the next penny", which matches the
    library's default `ROUND_UP` mode.
  - § 6.12 "Renting and Homeownership", Example 6.110
    ($132,650 / 4.8% / 30yr).
  - Chapter 6 answer key — exercises 6.36, 6.78.1, 6.78.2, 6.100.1, 6.100.2,
    6.110, 6.114.
- [Las Positas College "Math for Liberal Arts" § 8.05 "Amortized Loans"](https://math.libretexts.org/Courses/Las_Positas_College/Math_for_Liberal_Arts/08:_Consumer_Mathematics/8.05:_Amortized_Loans)
  (LibreTexts, CC) — examples 1 ($15,000 / 9% / 5yr) and 3
  ($18,000 / 2% / 5yr).

**Reference / encyclopedic**

- [Wikipedia: Mortgage calculator](https://en.wikipedia.org/wiki/Mortgage_calculator)
  — $200,000 / 6.5% / 30yr / $1,264.14, derived from the closed-form annuity
  formula given in the article.

**Synthetic boundary loans**

Three loans constructed at exact half-cent rounding boundaries to exercise
the three supported rounding modes (`ROUND_UP`, `ROUND_HALF_UP`,
`ROUND_HALF_EVEN`). Constructed from $100,001.25 / 4.80% / 30yr so that
month-1 unrounded interest equals exactly $400.005 — the boundary that
distinguishes `HALF_UP` ($400.01) from `HALF_EVEN` ($400.00).

### Sources tried and rejected

Documented in commit history and noted here for transparency. Each was
rejected because at least one published value could not be reproduced
exactly:

- LibreTexts Business Math (Olivier) "Tamara's dishwasher loan" — published
  rows 2-5 diverge by 1 cent due to the textbook's "carry-precision with
  missing-pennies adjustment" reconciliation we cannot match.
- eCampus Ontario *Mathematics of Finance* Example 4.3.4 — published "balance
  after payment 20" diverges by 1 cent.
- OpenStax Contemporary Math § 6.8 sample table ($10,000 / 4.75% / 20yr) —
  published cumulative interest at month 18 differs by 4 cents.
- OpenStax *Principles of Finance* § 8.3 — published total-interest figures
  differ by 2-12 cents.
- Pima Open Press *Topics in Mathematics* § 6.4 — final-row residual,
  cumulative balance drift.
- Chase consumer-education page — published row 360 diverges from library's
  adjusted final payment.
- Las Positas College § 8.05 examples 2 and 4 — published total-interest /
  total-cost figures differ.
- OpenStax Contemporary Math § 6.12 Examples 6.111 and 6.113 — published
  cumulative-paid and mid-loan principal/balance values differ.
- BCcampus Business Mathematics "Kerry's Toyota Rav4" — textbook chose a
  non-actuarial whole-dollar payment.
- Various Canadian textbook examples (Maksim, Olivers, Chans) — use
  semi-annual compounding required by Canadian mortgage law, incompatible
  with the library's monthly compounding.
- William Hart, *Mathematics of Investment* (1924) — uses mill-precision
  (3 decimals), incompatible with cent-rounding.

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
