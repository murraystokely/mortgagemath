"""Structural invariant tests for amortization_schedule()."""

from datetime import date
from decimal import Decimal

import pytest

from mortgagemath import (
    DayCount,
    LoanParams,
    PaymentRounding,
    amortization_schedule,
)


# Test across a range of loan configurations.
LOAN_PARAMS = [
    pytest.param(Decimal("200000"), Decimal("6"), 360, id="200k_6pct_30yr"),
    pytest.param(Decimal("131250"), Decimal("4.25"), 360, id="131k_425pct_30yr"),
    pytest.param(Decimal("106500"), Decimal("3.5"), 180, id="106k_35pct_15yr"),
    pytest.param(Decimal("137500"), Decimal("6.938"), 360, id="137k_6938pct_30yr"),
    pytest.param(Decimal("300000"), Decimal("7"), 360, id="300k_7pct_30yr"),
    pytest.param(Decimal("50000"), Decimal("5"), 120, id="50k_5pct_10yr"),
    pytest.param(Decimal("500000"), Decimal("3"), 180, id="500k_3pct_15yr"),
    pytest.param(Decimal("75000"), Decimal("8.5"), 360, id="75k_85pct_30yr"),
]


class TestScheduleInvariants:

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_principal_plus_interest_equals_payment(self, principal, rate, term):
        """For every installment, principal + interest must equal payment."""
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        for inst in amortization_schedule(loan)[1:]:
            assert inst.principal + inst.interest == inst.payment, (
                f"Payment #{inst.number}: "
                f"{inst.principal} + {inst.interest} != {inst.payment}"
            )

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_final_balance_is_zero(self, principal, rate, term):
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        sched = amortization_schedule(loan)
        assert sched[-1].balance == Decimal("0.00")

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_balance_decreases_monotonically(self, principal, rate, term):
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        sched = amortization_schedule(loan)
        for i in range(1, len(sched)):
            assert sched[i].balance < sched[i - 1].balance, (
                f"Balance did not decrease at payment #{i}"
            )

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_total_principal_equals_original_amount(self, principal, rate, term):
        """Sum of all principal payments must equal the original loan amount."""
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        sched = amortization_schedule(loan)
        total = sum(inst.principal for inst in sched[1:])
        assert total == principal, (
            f"Total principal {total} != original {principal}"
        )

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_schedule_length(self, principal, rate, term):
        """Schedule has term_months + 1 entries (including payment 0)."""
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        sched = amortization_schedule(loan)
        assert len(sched) == term + 1

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_payment_zero_is_initial_state(self, principal, rate, term):
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        sched = amortization_schedule(loan)
        p0 = sched[0]
        assert p0.number == 0
        assert p0.payment == Decimal("0.00")
        assert p0.interest == Decimal("0.00")
        assert p0.principal == Decimal("0.00")
        assert p0.balance == principal

    @pytest.mark.parametrize("principal, rate, term", LOAN_PARAMS)
    def test_total_interest_accumulates(self, principal, rate, term):
        """total_interest field must equal cumulative sum of interest."""
        loan = LoanParams(principal=principal, annual_rate=rate, term_months=term)
        sched = amortization_schedule(loan)
        running = Decimal("0.00")
        for inst in sched[1:]:
            running += inst.interest
            assert inst.total_interest == running, (
                f"Payment #{inst.number}: total_interest {inst.total_interest} "
                f"!= cumulative {running}"
            )


# Same loans run through ACTUAL_360 with a January start_date for parametric
# invariant coverage of the day-counted schedule path.
ACTUAL_360_LOANS = [
    pytest.param(
        Decimal("1000000"), Decimal("5"), 120, date(2020, 1, 1),
        id="1m_5pct_10yr_actual_360",
    ),
    pytest.param(
        Decimal("500000"), Decimal("4.5"), 60, date(2021, 2, 1),
        id="500k_45pct_5yr_feb_start",
    ),
    pytest.param(
        Decimal("250000"), Decimal("6"), 24, date(2024, 2, 1),
        id="250k_6pct_2yr_leap_feb_start",
    ),
]


class TestActual360Invariants:

    @pytest.mark.parametrize("principal, rate, term, start", ACTUAL_360_LOANS)
    def test_principal_plus_interest_equals_payment(self, principal, rate, term, start):
        loan = LoanParams(
            principal=principal, annual_rate=rate, term_months=term,
            day_count=DayCount.ACTUAL_360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            start_date=start,
        )
        for inst in amortization_schedule(loan)[1:]:
            assert inst.principal + inst.interest == inst.payment, (
                f"Payment #{inst.number}: "
                f"{inst.principal} + {inst.interest} != {inst.payment}"
            )

    @pytest.mark.parametrize("principal, rate, term, start", ACTUAL_360_LOANS)
    def test_final_balance_is_zero(self, principal, rate, term, start):
        """Fully amortizing ACTUAL_360 (term == amortization_period) ends at $0.00,
        with the final payment absorbing whatever residual remains."""
        loan = LoanParams(
            principal=principal, annual_rate=rate, term_months=term,
            day_count=DayCount.ACTUAL_360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            start_date=start,
        )
        sched = amortization_schedule(loan)
        assert sched[-1].balance == Decimal("0.00")

    @pytest.mark.parametrize("principal, rate, term, start", ACTUAL_360_LOANS)
    def test_total_interest_accumulates(self, principal, rate, term, start):
        loan = LoanParams(
            principal=principal, annual_rate=rate, term_months=term,
            day_count=DayCount.ACTUAL_360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            start_date=start,
        )
        sched = amortization_schedule(loan)
        running = Decimal("0.00")
        for inst in sched[1:]:
            running += inst.interest
            assert inst.total_interest == running, (
                f"Payment #{inst.number}: total_interest {inst.total_interest} "
                f"!= cumulative {running}"
            )


class TestScheduleEdgeCases:

    def test_actual_360_schedule_requires_start_date(self):
        loan = LoanParams(
            principal=Decimal("100000"), annual_rate=Decimal("5"),
            term_months=360, day_count=DayCount.ACTUAL_360,
        )
        with pytest.raises(ValueError, match="ACTUAL_360 schedule requires"):
            amortization_schedule(loan)

    def test_thirty_360_silently_ignores_start_date(self):
        """start_date is irrelevant for 30/360 (every period is 30 days);
        passing one should produce the same schedule as omitting it."""
        common = dict(
            principal=Decimal("100000"), annual_rate=Decimal("5"),
            term_months=360,
        )
        a = amortization_schedule(LoanParams(**common))
        b = amortization_schedule(LoanParams(**common, start_date=date(2020, 1, 1)))
        for ia, ib in zip(a, b):
            assert ia == ib

    def test_balloon_30_360_schedule(self):
        """Balloon support also works with 30/360 day count: the closed-form
        payment is computed against amortization_period_months, the schedule
        runs term_months rows, and the final row's balance is the balloon."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=60,                       # 5-year term
            amortization_period_months=360,       # 30-year amortization basis
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        sched = amortization_schedule(loan)
        # Schedule has term_months + 1 entries (the +1 is the initial state row).
        assert len(sched) == 61
        # Each row honors the standard invariant.
        for inst in sched[1:]:
            assert inst.principal + inst.interest == inst.payment
        # Final row's balance is non-zero (the balloon).
        assert sched[-1].balance > Decimal("0.00")
        # Balance decreased monotonically (no overshoot).
        for i in range(1, len(sched)):
            assert sched[i].balance < sched[i - 1].balance

    def test_amort_period_equal_to_term_matches_default_schedule(self):
        common = dict(
            principal=Decimal("100000"), annual_rate=Decimal("5"),
            term_months=360,
        )
        a = amortization_schedule(LoanParams(**common))
        b = amortization_schedule(LoanParams(**common, amortization_period_months=360))
        for ia, ib in zip(a, b):
            assert ia == ib
