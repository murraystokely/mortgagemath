"""Amortization schedule generation."""

import calendar
import decimal
import warnings
from decimal import Decimal

from mortgagemath._payment import monthly_payment
from mortgagemath._types import (
    DayCount,
    EarlyPayoffWarning,
    Installment,
    LoanParams,
    PaymentRounding,
)

_PENNY = Decimal("0.01")
_ZERO = Decimal("0.00")

_ROUNDING_MAP = {
    PaymentRounding.ROUND_UP: decimal.ROUND_UP,
    PaymentRounding.ROUND_HALF_UP: decimal.ROUND_HALF_UP,
    PaymentRounding.ROUND_HALF_EVEN: decimal.ROUND_HALF_EVEN,
}


def amortization_schedule(loan: LoanParams) -> list[Installment]:
    """Generate a full amortization schedule.

    For 30/360 loans the schedule uses bank-style round-each-balance
    accounting:

    1. The monthly payment is computed once and rounded.
    2. Each month's interest is computed on the (rounded) remaining
       balance and rounded to the cent.
    3. Principal is the difference: ``payment - interest``.
    4. The final payment is adjusted so the balance lands exactly at zero.

    For Actual/360 loans the schedule uses Fannie Mae §1103 conventions:

    1. ``loan.start_date`` is required; period 1 covers the calendar
       month containing the start date.
    2. The unrounded closed-form payment is carried internally; each
       month's interest is computed in full Decimal precision as
       ``balance * annual_rate * days_in_month / 360``.
    3. Display values (``payment``, ``interest``, ``principal``) are
       rounded to the cent; the running balance internally is unrounded.
    4. The final payment is adjusted to land balance at exactly zero.

    Both modes guarantee ``principal + interest == payment`` for every
    installment and a final balance of exactly ``$0.00``.

    For very small principals the cent-rounded monthly payment can
    overpay the closed-form value by enough that the loan amortizes
    before the requested term.  In that case the schedule is truncated
    at the actual payoff month and an :class:`EarlyPayoffWarning` is
    emitted; ``len(schedule)`` will be smaller than ``term_months + 1``.

    Args:
        loan: Loan parameters.

    Returns:
        A list of :class:`Installment` objects from payment 0 (initial
        state showing the starting balance) through the final payment.

    Raises:
        ValueError: If principal or term_months is not positive, the
            day_count is unsupported, or ACTUAL_360 is requested without
            a start_date.

    Warns:
        EarlyPayoffWarning: When 30/360 round-each-balance accounting
            amortizes the loan before ``term_months`` due to monthly
            payment overpayment from rounding.
    """
    if loan.day_count == DayCount.THIRTY_360:
        return _schedule_thirty_360(loan)
    if loan.day_count == DayCount.ACTUAL_360:
        if loan.start_date is None:
            raise ValueError(
                "ACTUAL_360 schedule requires loan.start_date "
                "(the issue date / first interest-accrual period)"
            )
        return _schedule_actual_360(loan)
    raise ValueError(f"unsupported day_count: {loan.day_count}")  # pragma: no cover


def _schedule_thirty_360(loan: LoanParams) -> list[Installment]:
    pmt = monthly_payment(loan)
    interest_rounding = _ROUNDING_MAP[loan.interest_rounding]
    monthly_rate = loan.annual_rate / Decimal("1200")
    balance = loan.principal
    total_interest = _ZERO
    fully_amortizing = loan.amortization_period_months is None or (
        loan.amortization_period_months == loan.term_months
    )

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
        interest = (balance * monthly_rate).quantize(_PENNY, rounding=interest_rounding)

        is_scheduled_final = i == loan.term_months and fully_amortizing
        # Round-each-balance accounting can pay off a tiny loan early.
        # Example: $20 / 4.4% / 30yr.  The closed-form payment is $0.10018,
        # ROUND_UP rounds it to $0.11.  That extra $0.0098/month
        # accumulates over the schedule; balance crosses zero at month 301
        # instead of 360.  Without the guard below the schedule kept
        # generating $0.11 payments against a now-negative balance.  When
        # the standard payment would amortize the remaining balance in
        # this row, we treat it as an early payoff: pay exactly the
        # remaining balance + interest, land balance at $0, truncate.
        will_pay_off_early = (not is_scheduled_final) and (pmt - interest >= balance)

        if is_scheduled_final or will_pay_off_early:
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

        if will_pay_off_early:
            warnings.warn(
                f"Loan paid off at month {i} of term_months={loan.term_months}; "
                f"schedule truncated. The {loan.payment_rounding.value} monthly "
                f"payment of {pmt} overpays the closed-form value enough to "
                f"amortize the loan early. For very small principals, consider "
                f"PaymentRounding.ROUND_HALF_UP.",
                EarlyPayoffWarning,
                stacklevel=2,
            )
            break

    return schedule


def _schedule_actual_360(loan: LoanParams) -> list[Installment]:
    """Day-counted Actual/360 schedule with full-precision balance.

    Validated against Fannie Mae Multifamily Selling and Servicing Guide
    §1103: $25M / 5.5% / 30yr / Actual/360, issue date 2018-12-01,
    aggregate principal over first 120 payments = $4,114,494.17 (exact).
    """
    interest_rounding = _ROUNDING_MAP[loan.interest_rounding]
    annual_rate = loan.annual_rate / Decimal("100")  # percent → fraction

    # Validate via monthly_payment (which enforces rate/term/amort guards)
    # and reuse its rounded display value.
    pmt_disp = monthly_payment(loan)

    # Unrounded closed-form payment, carried internally; displayed value rounded.
    # Uses the amortization period (which may be larger than term_months for
    # balloon loans) — see the LoanParams docstring.
    r = loan.annual_rate / Decimal("1200")
    n = loan._amort_periods
    factor = (1 + r) ** n
    pmt_raw = (loan.principal * r * factor) / (factor - 1)

    fully_amortizing = loan.amortization_period_months is None or (
        loan.amortization_period_months == loan.term_months
    )

    balance = loan.principal  # full-precision Decimal
    total_interest_disp = _ZERO

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

    # Public dispatch in amortization_schedule() guarantees start_date is set
    # for ACTUAL_360; assert documents the invariant for the type checker.
    assert loan.start_date is not None
    sd = loan.start_date
    for i in range(1, loan.term_months + 1):
        # Period i covers the calendar month at offset (i-1) from start_date
        period_year = sd.year + (sd.month - 1 + i - 1) // 12
        period_month = (sd.month - 1 + i - 1) % 12 + 1
        days = calendar.monthrange(period_year, period_month)[1]

        interest_raw = balance * annual_rate * Decimal(days) / Decimal(360)
        interest_disp = interest_raw.quantize(_PENNY, rounding=interest_rounding)

        if i == loan.term_months and fully_amortizing:
            # Final payment of a fully amortizing loan: zero balance exactly.
            principal_disp = balance.quantize(_PENNY, rounding=interest_rounding)
            actual_pmt = principal_disp + interest_disp
            balance = _ZERO
            balance_disp = _ZERO
        else:
            actual_pmt = pmt_disp
            principal_disp = pmt_disp - interest_disp
            balance -= pmt_raw - interest_raw  # carry full precision
            balance_disp = balance.quantize(_PENNY, rounding=interest_rounding)

        total_interest_disp += interest_disp

        schedule.append(
            Installment(
                number=i,
                payment=actual_pmt,
                interest=interest_disp,
                principal=principal_disp,
                total_interest=total_interest_disp,
                balance=balance_disp,
            )
        )

    return schedule
