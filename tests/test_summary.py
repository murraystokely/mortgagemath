"""Tests for loan_summary() and LoanSummary."""

from datetime import date
from decimal import Decimal

from mortgagemath import (
    DayCount,
    LoanParams,
    PaymentRounding,
    loan_summary,
    us_30_year_fixed,
)


def test_fully_amortizing_summary():
    """Standard 30yr fixed: balloon_balance is zero, payoff equals total_paid."""
    s = loan_summary(us_30_year_fixed("300000", "6.5"))
    assert s.periodic_payment == Decimal("1896.21")
    assert s.num_payments == 360
    assert s.balloon_balance == Decimal("0.00")
    assert s.payoff_at_term == s.total_paid
    assert s.total_interest == Decimal("382628.90")
    assert s.total_fees == Decimal("0.00")
    assert s.total_principal == Decimal("300000.00")


def test_balloon_loan_summary():
    """Fannie Mae §1103 SARM: balloon_balance is the unpaid principal at term."""
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
    s = loan_summary(loan)
    assert s.periodic_payment == Decimal("141947.25")
    assert s.num_payments == 120
    assert s.balloon_balance == Decimal("20885505.83")
    assert s.balloon_balance > Decimal("0")
    assert s.payoff_at_term == s.total_paid + s.balloon_balance
    assert s.payoff_at_term > s.total_paid


def test_fee_loaded_summary():
    """Fee-loaded loan: total_fees is non-zero, total_paid includes fees."""
    loan = LoanParams(
        principal=Decimal("10000"),
        annual_rate=Decimal("5"),
        term_months=12,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
        fee_per_period=Decimal("2.92"),
    )
    s = loan_summary(loan)
    assert s.total_fees == Decimal("35.04")  # 2.92 * 12
    assert s.total_paid > s.total_interest + s.total_principal
    assert s.balloon_balance == Decimal("0.00")


def test_summary_repr_no_balloon():
    """Repr omits balloon for fully amortizing loans."""
    s = loan_summary(us_30_year_fixed("100000", "5"))
    r = repr(s)
    assert "balloon" not in r
    assert "payment=" in r
    assert "total_interest=" in r


def test_summary_repr_with_balloon():
    """Repr includes balloon for balloon loans."""
    loan = LoanParams(
        principal=Decimal("1000000"),
        annual_rate=Decimal("5"),
        term_months=60,
        amortization_period_months=360,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
    )
    s = loan_summary(loan)
    r = repr(s)
    assert "balloon=" in r
