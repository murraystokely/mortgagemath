"""Cent-accurate mortgage amortization for Python.

Validated against published CFPB and Fannie Mae examples.
Zero runtime dependencies — only the standard library.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

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

try:
    __version__ = _version("mortgagemath")
except PackageNotFoundError:  # pragma: no cover - editable/sdist edge case
    __version__ = "0+unknown"
del _version, PackageNotFoundError

__all__ = [
    "BalanceTracking",
    "DayCount",
    "EarlyPayoffWarning",
    "Installment",
    "LoanParams",
    "PaymentRounding",
    "__version__",
    "amortization_schedule",
    "monthly_payment",
]
