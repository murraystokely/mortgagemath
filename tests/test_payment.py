"""Unit tests for monthly_payment()."""

from decimal import Decimal

import pytest

from mortgagemath import DayCount, LoanParams, PaymentRounding, monthly_payment


class TestMonthlyPayment:

    def test_30yr_425(self):
        """$131,250 at 4.25% for 30yr = $645.68."""
        loan = LoanParams(
            principal=Decimal("131250"),
            annual_rate=Decimal("4.25"),
            term_months=360,
        )
        assert monthly_payment(loan) == Decimal("645.68")

    def test_15yr_350(self):
        """$106,500 at 3.5% for 15yr = $761.35."""
        loan = LoanParams(
            principal=Decimal("106500"),
            annual_rate=Decimal("3.5"),
            term_months=180,
        )
        assert monthly_payment(loan) == Decimal("761.35")

    def test_30yr_6938(self):
        """$137,500 at 6.938% for 30yr = $909.08."""
        loan = LoanParams(
            principal=Decimal("137500"),
            annual_rate=Decimal("6.938"),
            term_months=360,
        )
        assert monthly_payment(loan) == Decimal("909.08")

    def test_30yr_6pct_200k(self):
        """$200,000 at 6% for 30yr = $1,199.11 with ROUND_UP."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=360,
        )
        assert monthly_payment(loan) == Decimal("1199.11")

    def test_round_half_up(self):
        """ROUND_HALF_UP should round 645.671... to 645.67, not 645.68."""
        loan = LoanParams(
            principal=Decimal("131250"),
            annual_rate=Decimal("4.25"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        assert monthly_payment(loan) == Decimal("645.67")

    def test_round_half_even_runs(self):
        """ROUND_HALF_EVEN must be a valid payment_rounding choice."""
        loan = LoanParams(
            principal=Decimal("131250"),
            annual_rate=Decimal("4.25"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_EVEN,
        )
        # Unrounded is 645.671...; both HALF_UP and HALF_EVEN round to 645.67.
        assert monthly_payment(loan) == Decimal("645.67")

    def test_result_has_two_decimal_places(self):
        loan = LoanParams(
            principal=Decimal("100000"),
            annual_rate=Decimal("5"),
            term_months=360,
        )
        pmt = monthly_payment(loan)
        assert pmt == pmt.quantize(Decimal("0.01"))

    def test_higher_rate_higher_payment(self):
        base = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("4"),
            term_months=360,
        )
        high = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("8"),
            term_months=360,
        )
        assert monthly_payment(high) > monthly_payment(base)

    def test_shorter_term_higher_payment(self):
        long = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5"),
            term_months=360,
        )
        short = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5"),
            term_months=180,
        )
        assert monthly_payment(short) > monthly_payment(long)

    def test_actual_360_higher_than_30_360(self):
        """Actual/360 effective rate is higher due to 365/360 factor."""
        base = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=360,
            day_count=DayCount.THIRTY_360,
        )
        commercial = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=360,
            day_count=DayCount.ACTUAL_360,
        )
        assert monthly_payment(commercial) > monthly_payment(base)

    def test_zero_principal_raises(self):
        with pytest.raises(ValueError, match="principal must be positive"):
            monthly_payment(LoanParams(
                principal=Decimal("0"),
                annual_rate=Decimal("5"),
                term_months=360,
            ))

    def test_negative_principal_raises(self):
        with pytest.raises(ValueError, match="principal must be positive"):
            monthly_payment(LoanParams(
                principal=Decimal("-100000"),
                annual_rate=Decimal("5"),
                term_months=360,
            ))

    def test_zero_term_raises(self):
        with pytest.raises(ValueError, match="term_months must be positive"):
            monthly_payment(LoanParams(
                principal=Decimal("100000"),
                annual_rate=Decimal("5"),
                term_months=0,
            ))
