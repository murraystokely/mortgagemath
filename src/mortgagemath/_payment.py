"""Monthly payment calculation."""

import decimal
from decimal import Decimal

from mortgagemath._types import DayCount, LoanParams, PaymentRounding

_PENNY = Decimal("0.01")

_ROUNDING_MAP = {
    PaymentRounding.ROUND_UP: decimal.ROUND_UP,
    PaymentRounding.ROUND_HALF_UP: decimal.ROUND_HALF_UP,
}


def monthly_payment(loan: LoanParams) -> Decimal:
    """Calculate the monthly principal and interest payment for a loan.

    Uses the standard annuity formula with Decimal arithmetic throughout.
    The result is rounded according to ``loan.payment_rounding``.

    For 30/360 loans::

        r = annual_rate / 1200
        payment = P * r * (1+r)^n / ((1+r)^n - 1)

    For Actual/360 loans, the effective monthly rate is adjusted by the
    365/360 factor::

        r = annual_rate / 100 * (365/360) / 12

    Args:
        loan: Loan parameters.

    Returns:
        Monthly P&I payment rounded to the nearest cent.

    Raises:
        ValueError: If principal or term_months is not positive.
    """
    if loan.principal <= 0:
        raise ValueError(f"principal must be positive, got {loan.principal}")
    if loan.term_months <= 0:
        raise ValueError(f"term_months must be positive, got {loan.term_months}")

    rounding = _ROUNDING_MAP[loan.payment_rounding]

    if loan.day_count == DayCount.THIRTY_360:
        r = loan.annual_rate / Decimal("1200")
        n = loan.term_months
        payment = loan.principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    elif loan.day_count == DayCount.ACTUAL_360:
        r = loan.annual_rate * Decimal(str(365 / 360)) / Decimal("1200")
        n = loan.term_months
        payment = loan.principal * r * (1 + r) ** n / ((1 + r) ** n - 1)
    else:
        raise ValueError(f"unsupported day_count: {loan.day_count}")

    return payment.quantize(_PENNY, rounding=rounding)
