"""Structural invariant tests for amortization_schedule()."""

from decimal import Decimal

import pytest

from mortgagemath import LoanParams, amortization_schedule


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
