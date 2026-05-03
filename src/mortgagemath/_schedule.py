"""Amortization schedule generation."""

import calendar
import decimal
import warnings
from decimal import Decimal, localcontext

from mortgagemath._payment import _periodic_rate, _periodic_rate_for, periodic_payment
from mortgagemath._types import (
    BalanceTracking,
    DayCount,
    EarlyPayoffWarning,
    Installment,
    LoanParams,
    PaymentRounding,
    RateChange,
)

_PENNY = Decimal("0.01")
_ZERO = Decimal("0.00")
_ONE = Decimal("1")

_ROUNDING_MAP = {
    PaymentRounding.ROUND_UP: decimal.ROUND_UP,
    PaymentRounding.ROUND_HALF_UP: decimal.ROUND_HALF_UP,
    PaymentRounding.ROUND_HALF_EVEN: decimal.ROUND_HALF_EVEN,
}


def _recast_payment_pair(
    balance: Decimal,
    periodic_rate: Decimal,
    remaining_payments: int,
    payment_rounding: PaymentRounding,
) -> tuple[Decimal, Decimal]:
    """Recompute the level payment for a rate change. Returns (raw, rounded).

    Used by both 30/360 schedule paths.  ``balance`` is whatever balance
    flavor the caller is carrying (rounded for round-each, unrounded for
    carry-precision); the formula is the same.  Mirrors the closed-form
    annuity computation in :func:`periodic_payment` but with the new rate
    and the explicit remaining horizon.
    """
    rounding = _ROUNDING_MAP[payment_rounding]
    with localcontext() as ctx:
        ctx.prec = 50
        factor = (_ONE + periodic_rate) ** remaining_payments
        raw = balance * periodic_rate * factor / (factor - _ONE)
    return raw, raw.quantize(_PENNY, rounding=rounding)


def _apply_fee(inst: Installment, fee: Decimal) -> Installment:
    """Return a copy of ``inst`` with ``fee`` added to ``payment``.

    Used to apply ``LoanParams.fee_per_period`` uniformly to every
    schedule row.  The fee is treated as a flat amount in the loan's
    currency; quantize the input to cents so the resulting payment
    has consistent precision.
    """
    fee_cents = fee.quantize(_PENNY)
    return Installment(
        number=inst.number,
        payment=inst.payment + fee_cents,
        interest=inst.interest,
        principal=inst.principal,
        total_interest=inst.total_interest,
        balance=inst.balance,
        fee=fee_cents,
    )


def _next_rate_change(
    rate_schedule: tuple[RateChange, ...], idx: int, payment_number: int
) -> RateChange | None:
    """Return the rate change effective at ``payment_number``, if any.

    ``idx`` is the index of the next unconsumed entry; if it matches,
    the caller should consume it (advance idx past this entry).
    """
    if idx < len(rate_schedule) and rate_schedule[idx].effective_payment_number == payment_number:
        return rate_schedule[idx]
    return None


def amortization_schedule(loan: LoanParams) -> list[Installment]:
    """Generate a full amortization schedule.

    For 30/360 loans the schedule uses bank-style round-each-balance
    accounting:

    1. The periodic payment is computed once and rounded.
    2. Each period's interest is computed on the (rounded) remaining
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

    For very small principals the cent-rounded periodic payment can
    overpay the closed-form value by enough that the loan amortizes
    before the requested term.  In that case the schedule is truncated
    at the actual payoff period and an :class:`EarlyPayoffWarning` is
    emitted; ``len(schedule)`` will be smaller than ``total_payments + 1``.

    Args:
        loan: Loan parameters.

    Returns:
        A list of :class:`Installment` objects from period 0 (initial
        state showing the starting balance) through the final payment.

    Raises:
        ValueError: If principal or term_months is not positive, the
            day_count is unsupported, or ACTUAL_360 is requested without
            a start_date.

    Warns:
        EarlyPayoffWarning: When 30/360 round-each-balance accounting
            amortizes the loan before its scheduled end due to periodic
            payment overpayment from rounding.
    """
    if loan.day_count == DayCount.THIRTY_360:
        sched = _schedule_thirty_360(loan)
    elif loan.day_count == DayCount.ACTUAL_360:
        if loan.start_date is None:
            raise ValueError(
                "ACTUAL_360 schedule requires loan.start_date "
                "(the issue date / first interest-accrual period)"
            )
        sched = _schedule_actual_360(loan)
    else:  # pragma: no cover
        raise ValueError(f"unsupported day_count: {loan.day_count}")

    # Apply the optional per-period fee uniformly to every installment
    # row (row 0 is the initial state and has no payment, so it keeps
    # fee=0).  The fee adds to Installment.payment but does not alter
    # interest, principal, total_interest, or balance: the closed-form
    # arithmetic and balance accounting are untouched.
    fee = loan.fee_per_period
    if fee:
        sched = [sched[0], *(_apply_fee(inst, fee) for inst in sched[1:])]
    return sched


def _schedule_thirty_360(loan: LoanParams) -> list[Installment]:
    if loan.balance_tracking == BalanceTracking.CARRY_PRECISION:
        return _schedule_thirty_360_carry_precision(loan)
    return _schedule_thirty_360_round_each(loan)


def _schedule_thirty_360_round_each(loan: LoanParams) -> list[Installment]:
    pmt = periodic_payment(loan)
    interest_rounding = _ROUNDING_MAP[loan.interest_rounding]
    periodic_rate = _periodic_rate(loan)
    total_payments = loan._total_payments
    balance = loan.principal
    total_interest = _ZERO
    fully_amortizing = loan.amortization_period_months is None or (
        loan.amortization_period_months == loan.term_months
    )
    rate_schedule_idx = 0

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

    payment_rounding = _ROUNDING_MAP[loan.payment_rounding]

    for i in range(1, total_payments + 1):
        # Apply any rate change effective at this payment, before interest accrual.
        rc = _next_rate_change(loan.rate_schedule, rate_schedule_idx, i)
        if rc is not None:
            periodic_rate = _periodic_rate_for(
                rc.new_annual_rate, loan.compounding, loan.payment_frequency
            )
            if rc.recast:
                remaining = total_payments - (i - 1)
                _, pmt_uncapped = _recast_payment_pair(
                    balance, periodic_rate, remaining, loan.payment_rounding
                )
                if rc.payment_cap_factor is not None:
                    cap = (pmt * rc.payment_cap_factor).quantize(_PENNY, rounding=payment_rounding)
                    pmt = min(pmt_uncapped, cap)
                else:
                    pmt = pmt_uncapped
            rate_schedule_idx += 1

        interest = (balance * periodic_rate).quantize(_PENNY, rounding=interest_rounding)

        is_scheduled_final = i == total_payments and fully_amortizing
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
                f"Loan paid off at period {i} of total_payments={total_payments}; "
                f"schedule truncated. The {loan.payment_rounding.value} periodic "
                f"payment of {pmt} overpays the closed-form value enough to "
                f"amortize the loan early. For very small principals, consider "
                f"PaymentRounding.ROUND_HALF_UP.",
                EarlyPayoffWarning,
                stacklevel=2,
            )
            break

    return schedule


def _schedule_thirty_360_carry_precision(loan: LoanParams) -> list[Installment]:
    """30/360 schedule with full-precision balance carried between rows.

    Excel-default convention used by graduate-level CRE finance textbooks:
    the unrounded closed-form payment and unrounded per-row interest are
    carried internally; per-row displayed values are rounded to cents.
    Per-row ``principal + interest == payment`` invariant still holds; the
    final payment may differ from the regular payment by 1-2 cents to
    land balance at exactly $0.00.

    When ``loan.payment_override`` is set, the override is the level
    payment for every full row and the final-row trueup is derived from
    the full-precision ``balance + interest`` rounded once — the
    historical "given-payment, find-term" convention used by the FHLBB
    March 1935 *Review* schedules.
    """
    interest_rounding = _ROUNDING_MAP[loan.interest_rounding]
    periodic_rate = _periodic_rate(loan)
    total_payments = loan._total_payments

    # Validate via periodic_payment (enforces guards) and reuse rounded display.
    pmt_disp = periodic_payment(loan)

    if loan.payment_override is not None:
        # Override: skip the closed-form derivation entirely and use the
        # pinned value as both the displayed and full-precision payment.
        pmt_raw = pmt_disp
    else:
        # Unrounded closed-form payment, carried internally.
        n = loan._amort_payments
        with localcontext() as ctx:
            ctx.prec = 50
            factor = (_ONE + periodic_rate) ** n
            pmt_raw = (loan.principal * periodic_rate * factor) / (factor - _ONE)

    fully_amortizing = loan.amortization_period_months is None or (
        loan.amortization_period_months == loan.term_months
    )

    balance = loan.principal  # full-precision Decimal
    total_interest_disp = _ZERO
    rate_schedule_idx = 0
    payment_rounding = _ROUNDING_MAP[loan.payment_rounding]

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

    for i in range(1, total_payments + 1):
        # Apply any rate change effective at this payment, before interest accrual.
        rc = _next_rate_change(loan.rate_schedule, rate_schedule_idx, i)
        if rc is not None:
            periodic_rate = _periodic_rate_for(
                rc.new_annual_rate, loan.compounding, loan.payment_frequency
            )
            if rc.recast:
                remaining = total_payments - (i - 1)
                pmt_uncapped_raw, pmt_uncapped_disp = _recast_payment_pair(
                    balance, periodic_rate, remaining, loan.payment_rounding
                )
                if rc.payment_cap_factor is not None:
                    cap = (pmt_disp * rc.payment_cap_factor).quantize(
                        _PENNY, rounding=payment_rounding
                    )
                    if cap < pmt_uncapped_disp:
                        # Cap binds: use the cap as both raw and displayed
                        # payment.  The cap is at cents granularity, so
                        # subsequent neg-am math uses the cap value exactly.
                        pmt_disp = cap
                        pmt_raw = cap
                    else:
                        pmt_disp = pmt_uncapped_disp
                        pmt_raw = pmt_uncapped_raw
                else:
                    pmt_disp = pmt_uncapped_disp
                    pmt_raw = pmt_uncapped_raw
            rate_schedule_idx += 1

        interest_raw = balance * periodic_rate
        interest_disp = interest_raw.quantize(_PENNY, rounding=interest_rounding)

        if i == total_payments and fully_amortizing:
            # Final payment of a fully amortizing loan: zero balance exactly.
            if loan.payment_override is not None:
                # FHLBB-style trueup: round the full-precision (balance +
                # interest) sum once to cents, then derive principal.
                # This matches the published source's "round-the-total"
                # convention rather than rounding components independently.
                actual_pmt_raw = balance + interest_raw
                actual_pmt = actual_pmt_raw.quantize(_PENNY, rounding=payment_rounding)
                principal_disp = actual_pmt - interest_disp
            else:
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


def _schedule_actual_360(loan: LoanParams) -> list[Installment]:
    """Day-counted Actual/360 schedule with full-precision balance.

    Validated against Fannie Mae Multifamily Selling and Servicing Guide
    §1103: $25M / 5.5% / 30yr / Actual/360, issue date 2018-12-01,
    aggregate principal over first 120 payments = $4,114,494.17 (exact).

    ACTUAL_360 is restricted (in ``LoanParams.__post_init__``) to monthly
    compounding and monthly payments — day-counted accrual is not
    well-defined for non-monthly cadence, and all worked examples we
    validate against (§1103, §1104, §1106) are monthly + monthly.
    """
    interest_rounding = _ROUNDING_MAP[loan.interest_rounding]
    annual_rate = loan.annual_rate / Decimal("100")  # percent → fraction

    # Validate via periodic_payment (which enforces rate/term/amort guards)
    # and reuse its rounded display value.
    pmt_disp = periodic_payment(loan)

    # Unrounded closed-form payment, carried internally; displayed value rounded.
    # Uses the amortization period (which may be larger than term_months for
    # balloon loans) — see the LoanParams docstring.
    r = loan.annual_rate / Decimal("1200")
    n = loan._amort_periods
    factor = (_ONE + r) ** n
    pmt_raw = (loan.principal * r * factor) / (factor - _ONE)

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
