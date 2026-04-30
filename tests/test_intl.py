"""Tests for v0.3.0 international fixed-rate features.

Covers:
- Compounding enum (MONTHLY, SEMI_ANNUAL, ANNUAL)
- PaymentFrequency enum and payments_per_year mapping
- monthly_payment ↔ periodic_payment equivalence (alias)
- LoanParams construction validation for non-monthly cadence
- Backward compat: default-construction preserves v0.2.x behavior
"""

from decimal import Decimal

import pytest

from mortgagemath import (
    Compounding,
    DayCount,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
    amortization_schedule,
    monthly_payment,
    periodic_payment,
)


class TestPaymentFrequency:
    @pytest.mark.parametrize(
        "freq, expected_ppy",
        [
            (PaymentFrequency.MONTHLY, 12),
            (PaymentFrequency.SEMI_MONTHLY, 24),
            (PaymentFrequency.BIWEEKLY, 26),
            (PaymentFrequency.WEEKLY, 52),
            (PaymentFrequency.QUARTERLY, 4),
            (PaymentFrequency.ANNUAL, 1),
        ],
    )
    def test_payments_per_year(self, freq, expected_ppy):
        assert freq.payments_per_year == expected_ppy


class TestAlias:
    def test_monthly_payment_is_periodic_payment(self):
        """``monthly_payment`` is a permanent alias for ``periodic_payment``."""
        assert monthly_payment is periodic_payment

    def test_alias_returns_same_value(self):
        loan = LoanParams(
            principal=Decimal("131250"),
            annual_rate=Decimal("4.25"),
            term_months=360,
        )
        assert monthly_payment(loan) == periodic_payment(loan)


class TestBackwardCompat:
    def test_default_construction_unchanged(self):
        """Existing v0.2.x-style construction yields identical numbers."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=360,
        )
        # Defaults: monthly compounding, monthly payments. Periodic rate
        # collapses to annual_rate / 1200, matching v0.2.x exactly.
        assert loan.compounding == Compounding.MONTHLY
        assert loan.payment_frequency == PaymentFrequency.MONTHLY
        assert periodic_payment(loan) == Decimal("1199.11")  # established v0.2.x value

    def test_30_360_default_schedule_unchanged(self):
        """First three rows of a $200k / 6% / 30yr default schedule."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=360,
        )
        sched = amortization_schedule(loan)
        # Spot-check: first month interest, principal, balance.
        assert sched[1].interest == Decimal("1000.00")
        assert sched[1].principal == Decimal("199.11")
        assert sched[1].balance == Decimal("199800.89")


class TestSemiAnnualCompounding:
    def test_canadian_5pct_25yr_monthly(self):
        """Per Canadian Interest Act §6, j_2=5% / 25yr / monthly → $581.60.

        Sanity check that the FCAC default example (which we don't ship
        as a fixture due to total-interest representation) computes the
        right monthly payment.
        """
        loan = LoanParams(
            principal=Decimal("100000"),
            annual_rate=Decimal("5"),
            term_months=300,
            compounding=Compounding.SEMI_ANNUAL,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        assert periodic_payment(loan) == Decimal("581.60")

    def test_quarterly_under_semi_annual_compounding(self):
        """Quarterly cadence under j_2 quoting (eCampus 4.4.1 first term)."""
        loan = LoanParams(
            principal=Decimal("297500"),
            annual_rate=Decimal("3.8"),
            term_months=36,
            amortization_period_months=240,
            compounding=Compounding.SEMI_ANNUAL,
            payment_frequency=PaymentFrequency.QUARTERLY,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        assert periodic_payment(loan) == Decimal("5317.62")

    def test_quarterly_schedule_has_correct_payment_count(self):
        """Quarterly cadence on a 36-month term yields 12 payments."""
        loan = LoanParams(
            principal=Decimal("297500"),
            annual_rate=Decimal("3.8"),
            term_months=36,
            amortization_period_months=240,
            compounding=Compounding.SEMI_ANNUAL,
            payment_frequency=PaymentFrequency.QUARTERLY,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        sched = amortization_schedule(loan)
        assert len(sched) == 13  # opening row + 12 payments


class TestAnnualCompounding:
    def test_annual_compounding_with_annual_payments(self):
        """Effective annual rate 5% on $1000 over 1 year → $1050.00."""
        loan = LoanParams(
            principal=Decimal("1000"),
            annual_rate=Decimal("5"),
            term_months=12,
            compounding=Compounding.ANNUAL,
            payment_frequency=PaymentFrequency.ANNUAL,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        assert periodic_payment(loan) == Decimal("1050.00")


class TestValidation:
    def test_indivisible_term_rejected(self):
        """A 1-month term with biweekly cadence cannot be a whole number of payments."""
        with pytest.raises(ValueError, match="not divisible by 12"):
            LoanParams(
                principal=Decimal("10000"),
                annual_rate=Decimal("5"),
                term_months=1,
                payment_frequency=PaymentFrequency.BIWEEKLY,
            )

    def test_actual_360_rejects_non_monthly_cadence(self):
        """Day-counted accrual is undefined for non-monthly cadence."""
        with pytest.raises(ValueError, match=r"ACTUAL_360 requires PaymentFrequency\.MONTHLY"):
            LoanParams(
                principal=Decimal("10000"),
                annual_rate=Decimal("5"),
                term_months=12,
                day_count=DayCount.ACTUAL_360,
                payment_frequency=PaymentFrequency.QUARTERLY,
            )

    def test_actual_360_rejects_non_monthly_compounding(self):
        with pytest.raises(ValueError, match=r"ACTUAL_360 requires Compounding\.MONTHLY"):
            LoanParams(
                principal=Decimal("10000"),
                annual_rate=Decimal("5"),
                term_months=12,
                day_count=DayCount.ACTUAL_360,
                compounding=Compounding.SEMI_ANNUAL,
            )

    def test_indivisible_amort_period_rejected(self):
        with pytest.raises(ValueError, match="amortization_period_months"):
            LoanParams(
                principal=Decimal("10000"),
                annual_rate=Decimal("5"),
                term_months=12,
                amortization_period_months=1,
                payment_frequency=PaymentFrequency.QUARTERLY,
            )
