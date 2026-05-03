"""Regression tests for v0.6.1 stabilization fixes.

Each test in this module pins behavior introduced or hardened in
v0.6.1:

1. ``test_*_independent_of_global_decimal_precision`` — schedule
   generation must produce the same cents output regardless of
   the caller's ambient ``decimal.getcontext().prec``.
2. ``test_payment_override_*`` — the carry-precision early-payoff
   guard must catch over-large overrides instead of producing
   negative balances or payments; ``LoanParams.__post_init__``
   must reject invalid override combinations at construction time.
"""

from __future__ import annotations

import decimal
import warnings
from datetime import date
from decimal import Decimal

import pytest

from mortgagemath import (
    BalanceTracking,
    Compounding,
    DayCount,
    EarlyPayoffWarning,
    LoanParams,
    PaymentRounding,
    amortization_schedule,
)

# ---------------------------------------------------------------------------
# 1. Decimal-context-independence regressions


def _with_low_prec(prec: int):
    """Context manager that sets a low Decimal precision and restores it."""

    class _LowPrec:
        def __enter__(self):
            self.original = decimal.getcontext().copy()
            decimal.getcontext().prec = prec

        def __exit__(self, *exc):
            decimal.setcontext(self.original)

    return _LowPrec()


def test_actual_360_independent_of_global_decimal_precision() -> None:
    """Fannie Mae §1103 SARM balloon must match published value regardless of ambient precision."""
    loan = LoanParams(
        principal=Decimal("25000000"),
        annual_rate=Decimal("5.5"),
        term_months=120,
        amortization_period_months=360,
        day_count=DayCount.ACTUAL_360,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
        start_date=date(2018, 12, 1),
    )
    expected_balloon = Decimal("20885505.83")

    # Default ambient precision (Python's 28 digits): must match.
    assert amortization_schedule(loan)[120].balance == expected_balloon

    # Low ambient precision: must still match. Without the v0.6.1
    # localcontext() wrap the result was Decimal("20885505.23") —
    # a 60-cent drift on a $25 M schedule.
    with _with_low_prec(10):
        assert amortization_schedule(loan)[120].balance == expected_balloon


def test_thirty_360_carry_precision_independent_of_global_decimal_precision() -> None:
    """Carry-precision 30/360 schedule must match under low ambient precision (Goldstein § 10.3)."""
    loan = LoanParams(
        principal=Decimal("563.00"),
        annual_rate=Decimal("12"),
        term_months=5,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
        balance_tracking=BalanceTracking.CARRY_PRECISION,
    )
    # Published Goldstein § 10.3 row 1 anchors:
    expected_row_1 = (Decimal("116.00"), Decimal("5.63"), Decimal("110.37"))

    sched = amortization_schedule(loan)
    assert (sched[1].payment, sched[1].interest, sched[1].principal) == expected_row_1

    with _with_low_prec(10):
        sched = amortization_schedule(loan)
        assert (sched[1].payment, sched[1].interest, sched[1].principal) == expected_row_1


def test_thirty_360_round_each_independent_of_global_decimal_precision() -> None:
    """Default round-each 30/360 schedule must match under low ambient precision (CFPB H-25(B))."""
    loan = LoanParams(
        principal=Decimal("162000.00"),
        annual_rate=Decimal("3.875"),
        term_months=360,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
    )
    expected_row_1 = (Decimal("761.78"), Decimal("523.13"), Decimal("238.65"))

    sched = amortization_schedule(loan)
    assert (sched[1].payment, sched[1].interest, sched[1].principal) == expected_row_1

    with _with_low_prec(10):
        sched = amortization_schedule(loan)
        assert (sched[1].payment, sched[1].interest, sched[1].principal) == expected_row_1


# ---------------------------------------------------------------------------
# 2. payment_override regressions


def test_payment_override_overlarge_truncates_with_warning() -> None:
    """Over-large payment_override truncates instead of producing negative balance."""
    loan = LoanParams(
        principal=Decimal("1000"),
        annual_rate=Decimal("5"),
        term_months=12,
        balance_tracking=BalanceTracking.CARRY_PRECISION,
        payment_override=Decimal("500.00"),
    )
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        sched = amortization_schedule(loan)

    early_warnings = [w for w in caught if issubclass(w.category, EarlyPayoffWarning)]
    assert len(early_warnings) == 1, "Expected exactly one EarlyPayoffWarning"

    # Schedule truncated before the scheduled term.
    assert sched[-1].number < loan.term_months
    assert sched[-1].balance == Decimal("0.00")

    # No row exhibits the pre-fix negative-balance / negative-payment behavior.
    assert all(row.balance >= Decimal("0.00") for row in sched), "negative balance"
    assert all(row.payment >= Decimal("0.00") for row in sched), "negative payment"

    # Per-row invariant still holds.
    for row in sched[1:]:
        assert row.principal + row.interest == row.payment


def test_payment_override_must_be_positive() -> None:
    with pytest.raises(ValueError, match="payment_override must be positive"):
        LoanParams(
            principal=Decimal("1000"),
            annual_rate=Decimal("5"),
            term_months=12,
            payment_override=Decimal("0"),
        )


def test_payment_override_must_be_cent_denominated() -> None:
    with pytest.raises(ValueError, match="whole cents"):
        LoanParams(
            principal=Decimal("1000"),
            annual_rate=Decimal("5"),
            term_months=12,
            payment_override=Decimal("99.999"),
        )


def test_payment_override_rejects_balloon_basis() -> None:
    with pytest.raises(ValueError, match="fully-amortizing"):
        LoanParams(
            principal=Decimal("1000"),
            annual_rate=Decimal("5"),
            term_months=120,
            amortization_period_months=360,
            payment_override=Decimal("100.00"),
        )


def test_amortization_period_must_be_at_least_term() -> None:
    """Validation moved to LoanParams.__post_init__ in v0.6.1."""
    with pytest.raises(ValueError, match="must be >= term_months"):
        LoanParams(
            principal=Decimal("1000"),
            annual_rate=Decimal("5"),
            term_months=12,
            amortization_period_months=6,
        )


def test_amortization_period_must_be_positive() -> None:
    with pytest.raises(ValueError, match="positive when set"):
        LoanParams(
            principal=Decimal("1000"),
            annual_rate=Decimal("5"),
            term_months=12,
            amortization_period_months=0,
        )


def test_payment_override_fhlbb_fixture_still_clean() -> None:
    """Sanity check that the early-payoff guard didn't disturb FHLBB 1935."""
    loan = LoanParams(
        principal=Decimal("3000.00"),
        annual_rate=Decimal("6"),
        term_months=139,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
        balance_tracking=BalanceTracking.CARRY_PRECISION,
        payment_override=Decimal("30.00"),
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", EarlyPayoffWarning)
        sched = amortization_schedule(loan)

    assert sched[138].payment == Decimal("30.00")
    assert sched[139].payment == Decimal("29.27")  # FHLBB published trueup
    assert sched[139].balance == Decimal("0.00")


def test_low_precision_does_not_affect_canadian_j2_schedule() -> None:
    """Compounding.SEMI_ANNUAL math must also be precision-context-independent."""
    loan = LoanParams(
        principal=Decimal("350100"),
        annual_rate=Decimal("4.9"),
        term_months=36,
        amortization_period_months=240,
        compounding=Compounding.SEMI_ANNUAL,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
    )
    expected_payment = Decimal("2281.73")
    expected_balloon = Decimal("316593.49")

    sched = amortization_schedule(loan)
    assert sched[1].payment == expected_payment
    assert sched[36].balance == expected_balloon

    with _with_low_prec(10):
        sched = amortization_schedule(loan)
        assert sched[1].payment == expected_payment
        assert sched[36].balance == expected_balloon
