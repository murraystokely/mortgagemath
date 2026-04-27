# mortgagemath

Correct mortgage amortization calculations, verified against real bank statements.

## Installation

```
pip install mortgagemath
```

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
