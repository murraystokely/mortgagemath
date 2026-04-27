"""Amortization schedule generation."""

import decimal
from decimal import Decimal

from mortgagemath._payment import monthly_payment
from mortgagemath._types import DayCount, Installment, LoanParams, PaymentRounding

_PENNY = Decimal("0.01")
_ZERO = Decimal("0.00")

_ROUNDING_MAP = {
    PaymentRounding.ROUND_UP: decimal.ROUND_UP,
    PaymentRounding.ROUND_HALF_UP: decimal.ROUND_HALF_UP,
}


def amortization_schedule(loan: LoanParams) -> list[Installment]:
    """Generate a full amortization schedule with bank-style rounding.

    The schedule is computed iteratively, matching how banks actually
    process mortgage payments:

    1. The monthly payment is computed once and rounded (see
       :func:`monthly_payment`).
    2. Each month's interest is computed on the remaining balance and
       rounded to the cent.
    3. Principal is the difference: ``payment - interest``.
    4. The final payment is adjusted so the balance lands exactly at zero.

    This ensures that ``principal + interest == payment`` for every
    installment, the final balance is exactly zero, and the sum of all
    principal payments equals the original loan amount.

    Args:
        loan: Loan parameters.

    Returns:
        A list of :class:`Installment` objects from payment 0 (initial
        state showing the starting balance) through the final payment.

    Raises:
        ValueError: If principal or term_months is not positive, or if
            the day_count is not yet supported for schedule generation.
    """
    if loan.day_count != DayCount.THIRTY_360:
        raise ValueError(
            f"amortization_schedule currently supports only 30/360 "
            f"day count, got {loan.day_count.value}"
        )

    pmt = monthly_payment(loan)
    interest_rounding = _ROUNDING_MAP[loan.interest_rounding]
    monthly_rate = loan.annual_rate / Decimal("1200")
    balance = loan.principal
    total_interest = _ZERO

    schedule: list[Installment] = [
        Installment(
            number=0,
            payment=_ZERO,
            interest=_ZERO,
            principal=_ZERO,
            total_interest=_ZERO,
            balance=balance,
        )
    ]

    for i in range(1, loan.term_months + 1):
        interest = (balance * monthly_rate).quantize(
            _PENNY, rounding=interest_rounding
        )

        if i == loan.term_months:
            # Final payment: zero out balance exactly.
            principal_pmt = balance
            actual_pmt = principal_pmt + interest
        else:
            actual_pmt = pmt
            principal_pmt = actual_pmt - interest

        balance -= principal_pmt
        total_interest += interest

        schedule.append(
            Installment(
                number=i,
                payment=actual_pmt,
                interest=interest,
                principal=principal_pmt,
                total_interest=total_interest,
                balance=balance,
            )
        )

    return schedule
