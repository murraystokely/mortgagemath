"""Cent-accurate mortgage amortization for Python.

Validated against published CFPB and Fannie Mae examples.
Zero runtime dependencies — only the standard library.
"""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _version

from mortgagemath._constructors import (
    canada_accelerated_biweekly,
    canada_fixed_j2,
    fixed_payment_mortgage,
    fixed_rate_mortgage,
    us_15_year_fixed,
    us_30_year_fixed,
    us_actual_360_commercial,
)
from mortgagemath._payment import monthly_payment, periodic_payment, principal_quota
from mortgagemath._schedule import amortization_schedule
from mortgagemath._summary import LoanSummary, loan_summary
from mortgagemath._types import (
    AmortizationMethod,
    BalanceTracking,
    Compounding,
    DayCount,
    EarlyPayoffWarning,
    Installment,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
    RateChange,
)

try:
    __version__ = _version("mortgagemath")
except PackageNotFoundError:  # pragma: no cover - editable/sdist edge case
    __version__ = "0+unknown"
del _version, PackageNotFoundError

__all__ = [
    "AmortizationMethod",
    "BalanceTracking",
    "Compounding",
    "DayCount",
    "EarlyPayoffWarning",
    "Installment",
    "LoanParams",
    "LoanSummary",
    "PaymentFrequency",
    "PaymentRounding",
    "RateChange",
    "__version__",
    "amortization_schedule",
    "canada_accelerated_biweekly",
    "canada_fixed_j2",
    "fixed_payment_mortgage",
    "fixed_rate_mortgage",
    "loan_summary",
    "monthly_payment",
    "periodic_payment",
    "principal_quota",
    "us_15_year_fixed",
    "us_30_year_fixed",
    "us_actual_360_commercial",
]
