# Quickstart

## A 30-year fixed-rate residential mortgage

```python
from decimal import Decimal
from mortgagemath import LoanParams, periodic_payment, amortization_schedule

loan = LoanParams(
    principal=Decimal("300000"),
    annual_rate=Decimal("6.5"),
    term_months=360,
)
pmt = periodic_payment(loan)         # Decimal("1896.21")
sched = amortization_schedule(loan)
print(sched[1].interest)             # Decimal("1625.00")
print(sched[1].principal)            # Decimal("271.21")
print(sched[-1].balance)             # Decimal("0.00") — exact closure
```

Returns a cent-accurate periodic payment and a lender-style
amortization schedule that lands exactly at `$0.00` on the final
payment.

## Canadian semi-annual mortgages

The Canadian *Interest Act* §6 quotes rates as semi-annually
compounded.  Pass `compounding=Compounding.SEMI_ANNUAL`:

```python
from mortgagemath import (
    LoanParams, Compounding, PaymentFrequency,
    PaymentRounding, periodic_payment,
)

# Canadian 5-year-term mortgage on a 25-year amortization basis,
# monthly payments at j_2 = 5%.
loan = LoanParams(
    principal=Decimal("300000"),
    annual_rate=Decimal("5"),
    term_months=300,                       # full amortization horizon
    compounding=Compounding.SEMI_ANNUAL,
    payment_frequency=PaymentFrequency.MONTHLY,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
)
print(periodic_payment(loan))              # Decimal("1747.45")
```

See {doc}`vignettes` for a full Canadian-mortgage walkthrough.

## Adjustable-rate mortgages

ARMs are modelled via a tuple of `RateChange` entries:

```python
from mortgagemath import LoanParams, RateChange, PaymentRounding, amortization_schedule

# 5/1 ARM: $200,000 at 5.7%, single rate change at month 61 to 7.2%.
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
print(sched[60].payment)                   # Decimal("1160.80") — initial
print(sched[61].payment)                   # Decimal("1334.16") — recast
```

`RateChange` also supports an optional `payment_cap_factor` for
payment-capped ARMs with negative amortization.  See the
{doc}`vignettes` page for the full Reg Z H-14 and ProEducate
walkthroughs.

## Commercial Actual/360 with a balloon

```python
from datetime import date
from mortgagemath import DayCount, amortization_schedule

# Fannie Mae §1103 Tier 2 SARM: $25M at 5.5%, 10-year term on a
# 30-year amortization basis, Actual/360 day count.
loan = LoanParams(
    principal=Decimal("25000000"),
    annual_rate=Decimal("5.5"),
    term_months=120,
    amortization_period_months=360,
    day_count=DayCount.ACTUAL_360,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
    start_date=date(2018, 12, 1),
)
sched = amortization_schedule(loan)
print(periodic_payment(loan))              # Decimal("141947.25")
print(sched[120].balance)                  # Decimal("20885505.83") — balloon at term
```

## Pinning the payment (FHLBB 1935 given-payment convention)

Pre-1968 American building-and-loan practice often chose a round
periodic payment (typically 1% of original principal per month)
and accepted whatever final-payment trueup the math produced.
The ``payment_override`` field reproduces this:

```python
from mortgagemath import LoanParams, BalanceTracking, PaymentRounding

# FHLBB Federal Home Loan Bank Review (March 1935) Plan A:
# $3,000 / 6% / payment chosen as 1% = $30 / month.
loan = LoanParams(
    principal=Decimal("3000.00"),
    annual_rate=Decimal("6"),
    term_months=139,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
    balance_tracking=BalanceTracking.CARRY_PRECISION,
    payment_override=Decimal("30.00"),
)
sched = amortization_schedule(loan)
print(sched[138].payment)   # Decimal("30.00")
print(sched[139].payment)   # Decimal("29.27") — final-row trueup
```

## Fee-loaded *annuité* (modern French / CF style)

A ``fee_per_period`` field on ``LoanParams`` adds a flat amount
per period to each ``Installment.payment``. It models the
modern French *tableau d'amortissement* convention of pricing
*assurance emprunteur* as ``taux × original_principal`` paid as
a flat amount per month, and the 1852 Crédit Foncier *annuité*
loading shape (frais d'administration + fonds de réserve +
impôt rolled into a constant per-period amount on top of the
actuarial interest+amortissement):

```python
loan = LoanParams(
    principal=Decimal("240000.00"),
    annual_rate=Decimal("4.0"),
    term_months=60,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
    fee_per_period=Decimal("80.00"),  # 0.40% × original principal annual
)
print(periodic_payment(loan))         # Decimal("4419.97") — pure P+I
sched = amortization_schedule(loan)
print(sched[1].payment)               # Decimal("4499.97") — gross échéance
print(sched[1].fee)                   # Decimal("80.00")
```

The closed-form ``periodic_payment(loan)`` continues to return
the actuarially-pure interest+principal value; the fee rides on
top in ``Installment.payment``, with ``Installment.fee`` exposing
the loading separately.

## Command line

```sh
# Just the periodic payment
mortgagemath payment --principal 131250 --rate 4.25 --term-months 360

# Full schedule as table (default), CSV, or JSON
mortgagemath schedule --principal 131250 --rate 4.25 --term-months 360 \
    --format csv > schedule.csv

# ARM with rate change at month 61
mortgagemath schedule --principal 200000 --rate 5.7 --term-months 360 \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP \
    --rate-change 61:7.2 --format json

# FHLBB 1935 Plan A — pinned payment with final-row trueup
mortgagemath schedule --principal 3000 --rate 6 --term-months 139 \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP \
    --balance-tracking carry_precision --payment-override 30 --format table

# Fee-loaded annuité — modern French / Crédit Foncier style
mortgagemath schedule --principal 240000 --rate 4 --term-months 60 \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP \
    --fee-per-period 80 --format table
```

`mortgagemath --help` and `mortgagemath <subcommand> --help` document
the full flag surface.
