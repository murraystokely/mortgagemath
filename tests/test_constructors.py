"""Tests for public convenience constructors."""

from datetime import date
from decimal import Decimal

import pytest

from mortgagemath import (
    BalanceTracking,
    Compounding,
    DayCount,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
    amortization_schedule,
    canada_fixed_j2,
    fixed_payment_mortgage,
    fixed_rate_mortgage,
    periodic_payment,
    us_15_year_fixed,
    us_30_year_fixed,
    us_actual_360_commercial,
)


def test_fixed_rate_mortgage_matches_manual_params():
    loan = fixed_rate_mortgage("300000", "6.5", 30)

    assert loan == LoanParams(
        principal=Decimal("300000"),
        annual_rate=Decimal("6.5"),
        term_months=360,
    )
    assert periodic_payment(loan) == Decimal("1896.21")


def test_us_30_year_fixed_accepts_decimal_inputs_and_overrides_rounding():
    loan = us_30_year_fixed(
        Decimal("162000.00"),
        Decimal("3.875"),
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
    )

    assert loan.term_months == 360
    assert loan.payment_rounding == PaymentRounding.ROUND_HALF_UP
    assert periodic_payment(loan) == Decimal("761.78")


def test_us_15_year_fixed_matches_manual_params():
    loan = us_15_year_fixed("106500", "3.5")

    assert loan == LoanParams(
        principal=Decimal("106500"),
        annual_rate=Decimal("3.5"),
        term_months=180,
    )
    assert periodic_payment(loan) == Decimal("761.35")


def test_canada_fixed_j2_full_amortization_defaults_to_monthly():
    loan = canada_fixed_j2("300000", "5", amortization_years=25)

    assert loan == LoanParams(
        principal=Decimal("300000"),
        annual_rate=Decimal("5"),
        term_months=300,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
        compounding=Compounding.SEMI_ANNUAL,
        payment_frequency=PaymentFrequency.MONTHLY,
    )
    assert periodic_payment(loan) == Decimal("1744.81")


def test_canada_fixed_j2_term_on_longer_amortization_matches_chans_fixture():
    loan = canada_fixed_j2("350100.00", "4.9", amortization_years=20, term_years=3)

    assert loan.term_months == 36
    assert loan.amortization_period_months == 240
    assert periodic_payment(loan) == Decimal("2281.73")
    assert amortization_schedule(loan)[36].balance == Decimal("316593.49")


def test_canada_fixed_j2_supports_quarterly_payment_frequency():
    loan = canada_fixed_j2(
        "297500.00",
        "3.8",
        amortization_years=20,
        term_years=3,
        payment_frequency=PaymentFrequency.QUARTERLY,
    )

    assert periodic_payment(loan) == Decimal("5317.62")
    assert amortization_schedule(loan)[12].balance == Decimal("265830.61")


def test_us_actual_360_commercial_matches_fannie_mae_fixture():
    loan = us_actual_360_commercial(
        "25000000",
        "5.5",
        term_years=10,
        amortization_years=30,
        start_date=date(2018, 12, 1),
    )

    assert loan.day_count == DayCount.ACTUAL_360
    assert loan.term_months == 120
    assert loan.amortization_period_months == 360
    assert periodic_payment(loan) == Decimal("141947.25")
    assert amortization_schedule(loan)[120].balance == Decimal("20885505.83")


def test_fixed_payment_mortgage_matches_fhlbb_fixture():
    loan = fixed_payment_mortgage(
        "3000.00",
        "6",
        "30.00",
        term_months=139,
    )

    sched = amortization_schedule(loan)
    assert loan.payment_override == Decimal("30.00")
    assert sched[138].payment == Decimal("30.00")
    assert sched[139].payment == Decimal("29.27")
    assert sched[139].balance == Decimal("0.00")


def test_constructors_preserve_optional_balance_tracking():
    loan = us_30_year_fixed(
        "100000",
        "6",
        balance_tracking=BalanceTracking.CARRY_PRECISION,
    )

    assert loan.balance_tracking == BalanceTracking.CARRY_PRECISION


def test_constructor_rejects_invalid_decimal_input():
    with pytest.raises(ValueError, match="principal must be a Decimal"):
        us_30_year_fixed("not-a-number", "6")


def test_constructor_rejects_nonpositive_years():
    with pytest.raises(ValueError, match="term_years must be positive"):
        fixed_rate_mortgage("100000", "6", 0)
