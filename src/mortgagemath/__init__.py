"""Cent-accurate mortgage amortization for Python.

Validated against published CFPB and Fannie Mae examples.
Zero runtime dependencies — only the standard library.
"""

from mortgagemath._payment import monthly_payment
from mortgagemath._schedule import amortization_schedule
from mortgagemath._types import (
    BalanceTracking,
    DayCount,
    EarlyPayoffWarning,
    Installment,
    LoanParams,
    PaymentRounding,
)

__version__ = "0.1.1"

__all__ = [
    "BalanceTracking",
    "DayCount",
    "EarlyPayoffWarning",
    "Installment",
    "LoanParams",
    "PaymentRounding",
    "amortization_schedule",
    "monthly_payment",
]
