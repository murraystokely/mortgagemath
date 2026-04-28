"""mortgagemath — correct mortgage amortization calculations.

Verified against real bank statements. Zero dependencies beyond the
Python standard library.
"""

from mortgagemath._payment import monthly_payment
from mortgagemath._schedule import amortization_schedule
from mortgagemath._types import DayCount, Installment, LoanParams, PaymentRounding

__version__ = "0.1.0"

__all__ = [
    "DayCount",
    "Installment",
    "LoanParams",
    "PaymentRounding",
    "amortization_schedule",
    "monthly_payment",
]
