"""Periodic payment calculation."""

import decimal
from decimal import Decimal, localcontext

from mortgagemath._types import Compounding, DayCount, LoanParams, PaymentRounding

_PENNY = Decimal("0.01")
_ONE = Decimal("1")
_TWO = Decimal("2")
_HUNDRED = Decimal("100")
_TWO_HUNDRED = Decimal("200")

_ROUNDING_MAP = {
    PaymentRounding.ROUND_UP: decimal.ROUND_UP,
    PaymentRounding.ROUND_HALF_UP: decimal.ROUND_HALF_UP,
    PaymentRounding.ROUND_HALF_EVEN: decimal.ROUND_HALF_EVEN,
}


def _periodic_rate(loan: LoanParams) -> Decimal:
    """Compute the per-period interest rate as a Decimal fraction.

    Returns the rate per payment period (not per year). For monthly
    compounding with monthly payments this is exactly ``annual_rate / 1200``,
    matching all v0.2.x behavior. For semi-annual compounding (the
    Canadian *Interest Act* §6 convention) this derives the equivalent
    periodic rate via ``(1 + j_2/200)**(2/payments_per_year) - 1``.
    """
    ppy = Decimal(loan.payment_frequency.payments_per_year)
    if loan.compounding == Compounding.MONTHLY:
        # Preserves v0.2.x exactness when ppy=12: annual / (100 * 12) = annual / 1200.
        return loan.annual_rate / (_HUNDRED * ppy)
    if loan.compounding == Compounding.SEMI_ANNUAL:
        # j_2 quoted as percent → semi-annual rate fraction is annual / 200.
        # Periodic rate solves (1+r)^ppy = (1 + j_2/200)^2.
        with localcontext() as ctx:
            ctx.prec = 50
            half_period = _ONE + loan.annual_rate / _TWO_HUNDRED
            return half_period ** (_TWO / ppy) - _ONE
    if loan.compounding == Compounding.ANNUAL:
        # Annual rate is quoted as effective annual.
        with localcontext() as ctx:
            ctx.prec = 50
            return (_ONE + loan.annual_rate / _HUNDRED) ** (_ONE / ppy) - _ONE
    raise ValueError(f"unsupported compounding: {loan.compounding}")  # pragma: no cover


def periodic_payment(loan: LoanParams) -> Decimal:
    """Calculate the periodic principal-and-interest payment for a loan.

    Uses the standard annuity formula with Decimal arithmetic throughout::

        r = periodic interest rate (per payment period)
        n = number of payments over the amortization period
        payment = P * r * (1+r)^n / ((1+r)^n - 1)

    The result is rounded according to ``loan.payment_rounding``.

    The same closed-form formula applies to both 30/360 and Actual/360
    loans: the day-count convention determines how the schedule accrues
    interest each period, not how the level periodic payment is computed.
    Validated against the Fannie Mae Multifamily Selling and Servicing
    Guide §1103 worked example ($25M / 5.5% / 30yr → DSC 6.8134680%
    → monthly P&I $141,947.25).

    For non-monthly compounding (Canadian *Interest Act* §6
    semi-annual quoting; or annual compounding) the periodic rate is
    derived from the quoted annual rate; see :func:`_periodic_rate`.

    Args:
        loan: Loan parameters.

    Returns:
        Periodic P&I payment rounded to the nearest cent.

    Raises:
        ValueError: If principal, term_months, or annual_rate is not
            positive, or the day_count is unsupported.
    """
    if loan.principal <= 0:
        raise ValueError(f"principal must be positive, got {loan.principal}")
    if loan.term_months <= 0:
        raise ValueError(f"term_months must be positive, got {loan.term_months}")
    if loan.annual_rate <= 0:
        raise ValueError(
            f"annual_rate must be positive, got {loan.annual_rate}. "
            f"For zero-interest loans, the closed-form annuity formula "
            f"is undefined; compute principal/term_months yourself."
        )
    if loan.amortization_period_months is not None:
        if loan.amortization_period_months <= 0:
            raise ValueError(
                f"amortization_period_months must be positive when set, "
                f"got {loan.amortization_period_months}"
            )
        if loan.amortization_period_months < loan.term_months:
            raise ValueError(
                f"amortization_period_months ({loan.amortization_period_months}) "
                f"must be >= term_months ({loan.term_months}). A shorter "
                f"amortization basis would over-amortize and drive the "
                f"balance negative before the term ends."
            )
    if loan.day_count not in (DayCount.THIRTY_360, DayCount.ACTUAL_360):  # pragma: no cover
        raise ValueError(f"unsupported day_count: {loan.day_count}")

    rounding = _ROUNDING_MAP[loan.payment_rounding]
    r = _periodic_rate(loan)
    n = loan._amort_payments
    with localcontext() as ctx:
        ctx.prec = 50
        factor = (_ONE + r) ** n
        payment = loan.principal * r * factor / (factor - _ONE)

    return payment.quantize(_PENNY, rounding=rounding)


# Permanent alias preserved from v0.2.x. ``monthly_payment`` is exactly
# ``periodic_payment`` — the historical name reflected the library's
# original monthly-only scope; the rename in v0.3.0 acknowledges that
# the function returns the per-period payment for whatever frequency
# the loan is configured with.
monthly_payment = periodic_payment
