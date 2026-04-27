"""Monthly payment calculation."""

import decimal
from decimal import Decimal

from mortgagemath._types import DayCount, LoanParams, PaymentRounding

_PENNY = Decimal("0.01")

_ROUNDING_MAP = {
    PaymentRounding.ROUND_UP: decimal.ROUND_UP,
    PaymentRounding.ROUND_HALF_UP: decimal.ROUND_HALF_UP,
    PaymentRounding.ROUND_HALF_EVEN: decimal.ROUND_HALF_EVEN,
}


def monthly_payment(loan: LoanParams) -> Decimal:
    """Calculate the monthly principal and interest payment for a loan.

    Uses the standard annuity formula with Decimal arithmetic throughout::

        r = annual_rate / 1200
        payment = P * r * (1+r)^n / ((1+r)^n - 1)

    The result is rounded according to ``loan.payment_rounding``.

    Only the 30/360 day count is currently supported. Actual/360 commercial
    loans require true day-counted schedules (variable days per calendar
    month, calendar dates, balloon-residual handling) that have not yet
    been validated against an authoritative published source — see
    ``docs/future-work.md`` for the conventions analysis.

    Args:
        loan: Loan parameters.

    Returns:
        Monthly P&I payment rounded to the nearest cent.

    Raises:
        ValueError: If principal or term_months is not positive.
        NotImplementedError: If ``day_count`` is ``ACTUAL_360``.
    """
    if loan.principal <= 0:
        raise ValueError(f"principal must be positive, got {loan.principal}")
    if loan.term_months <= 0:
        raise ValueError(f"term_months must be positive, got {loan.term_months}")

    if loan.day_count == DayCount.ACTUAL_360:
        raise NotImplementedError(
            "Actual/360 day count is not yet supported. See "
            "docs/future-work.md for the conventions analysis and the "
            "design questions that must be resolved before adding it."
        )
    if loan.day_count != DayCount.THIRTY_360:
        raise ValueError(f"unsupported day_count: {loan.day_count}")

    rounding = _ROUNDING_MAP[loan.payment_rounding]
    r = loan.annual_rate / Decimal("1200")
    n = loan.term_months
    payment = loan.principal * r * (1 + r) ** n / ((1 + r) ** n - 1)

    return payment.quantize(_PENNY, rounding=rounding)
