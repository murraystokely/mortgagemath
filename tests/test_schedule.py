"""Structural invariant tests for amortization_schedule()."""

import warnings
from datetime import date
from decimal import Decimal

import pytest

from mortgagemath import (
    DayCount,
    EarlyPayoffWarning,
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
                f"Payment #{inst.number}: {inst.principal} + {inst.interest} != {inst.payment}"
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
        assert total == principal, f"Total principal {total} != original {principal}"

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
        Decimal("1000000"),
        Decimal("5"),
        120,
        date(2020, 1, 1),
        id="1m_5pct_10yr_actual_360",
    ),
    pytest.param(
        Decimal("500000"),
        Decimal("4.5"),
        60,
        date(2021, 2, 1),
        id="500k_45pct_5yr_feb_start",
    ),
    pytest.param(
        Decimal("250000"),
        Decimal("6"),
        24,
        date(2024, 2, 1),
        id="250k_6pct_2yr_leap_feb_start",
    ),
]


class TestActual360Invariants:
    @pytest.mark.parametrize("principal, rate, term, start", ACTUAL_360_LOANS)
    def test_principal_plus_interest_equals_payment(self, principal, rate, term, start):
        loan = LoanParams(
            principal=principal,
            annual_rate=rate,
            term_months=term,
            day_count=DayCount.ACTUAL_360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            start_date=start,
        )
        for inst in amortization_schedule(loan)[1:]:
            assert inst.principal + inst.interest == inst.payment, (
                f"Payment #{inst.number}: {inst.principal} + {inst.interest} != {inst.payment}"
            )

    @pytest.mark.parametrize("principal, rate, term, start", ACTUAL_360_LOANS)
    def test_final_balance_is_zero(self, principal, rate, term, start):
        """Fully amortizing ACTUAL_360 (term == amortization_period) ends at $0.00,
        with the final payment absorbing whatever residual remains."""
        loan = LoanParams(
            principal=principal,
            annual_rate=rate,
            term_months=term,
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
            principal=principal,
            annual_rate=rate,
            term_months=term,
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
            principal=Decimal("100000"),
            annual_rate=Decimal("5"),
            term_months=360,
            day_count=DayCount.ACTUAL_360,
        )
        with pytest.raises(ValueError, match="ACTUAL_360 schedule requires"):
            amortization_schedule(loan)

    def test_thirty_360_silently_ignores_start_date(self):
        """start_date is irrelevant for 30/360 (every period is 30 days);
        passing one should produce the same schedule as omitting it."""
        common = dict(
            principal=Decimal("100000"),
            annual_rate=Decimal("5"),
            term_months=360,
        )
        a = amortization_schedule(LoanParams(**common))
        b = amortization_schedule(LoanParams(**common, start_date=date(2020, 1, 1)))
        for ia, ib in zip(a, b, strict=True):
            assert ia == ib

    def test_balloon_30_360_schedule(self):
        """Balloon support also works with 30/360 day count: the closed-form
        payment is computed against amortization_period_months, the schedule
        runs term_months rows, and the final row's balance is the balloon."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("6"),
            term_months=60,  # 5-year term
            amortization_period_months=360,  # 30-year amortization basis
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
            principal=Decimal("100000"),
            annual_rate=Decimal("5"),
            term_months=360,
        )
        a = amortization_schedule(LoanParams(**common))
        b = amortization_schedule(LoanParams(**common, amortization_period_months=360))
        for ia, ib in zip(a, b, strict=True):
            assert ia == ib


class TestEarlyPayoffFromRounding:
    """Tiny principals can pay off early because ROUND_UP overpays each month.

    Reference example: $20 / 4.4% / 30yr.

    * Closed-form monthly P&I is $0.100152.
    * ROUND_UP rounds it to $0.11.
    * That extra $0.0098/month accumulates: by month 300 the balance is
      $0.02; the standard $0.11 payment in month 301 would drive the
      balance to -$0.09.
    * With round-each-balance accounting (30/360), nothing in the math
      catches this — without the early-payoff guard the schedule keeps
      generating $0.11 payments against an ever-more-negative balance
      out to month 360.

    The library now detects this, truncates the schedule with the final
    row trued up to land balance at exactly $0.00, and emits an
    :class:`EarlyPayoffWarning`.
    """

    LOAN = LoanParams(
        principal=Decimal("20"),
        annual_rate=Decimal("4.4"),
        term_months=360,
    )

    def test_emits_warning(self):
        with pytest.warns(EarlyPayoffWarning, match="paid off at month"):
            amortization_schedule(self.LOAN)

    def test_schedule_truncates_before_term(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EarlyPayoffWarning)
            sched = amortization_schedule(self.LOAN)
        # term + 1 = 361.  Early payoff produces a strictly shorter schedule.
        assert len(sched) < 361
        # Pinned: at the documented per-month overpayment ($0.0098), the loan
        # amortizes at month 301 — well before the 360-month term.
        assert sched[-1].number == 301

    def test_final_balance_is_exactly_zero(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EarlyPayoffWarning)
            sched = amortization_schedule(self.LOAN)
        assert sched[-1].balance == Decimal("0.00")

    def test_balance_decreases_monotonically(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EarlyPayoffWarning)
            sched = amortization_schedule(self.LOAN)
        # No row may walk past zero — that was the symptom of the bug.
        for i in range(1, len(sched)):
            assert sched[i].balance < sched[i - 1].balance
            assert sched[i].balance >= Decimal("0.00")

    def test_principal_plus_interest_equals_payment(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EarlyPayoffWarning)
            sched = amortization_schedule(self.LOAN)
        for inst in sched[1:]:
            assert inst.principal + inst.interest == inst.payment

    def test_total_principal_equals_original_amount(self):
        """Even truncated, the sum of principal payments equals principal."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EarlyPayoffWarning)
            sched = amortization_schedule(self.LOAN)
        total = sum(inst.principal for inst in sched[1:])
        assert total == self.LOAN.principal

    def test_final_payment_is_partial(self):
        """The truncating row is a partial payment, not the standard $0.11."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", EarlyPayoffWarning)
            sched = amortization_schedule(self.LOAN)
        last = sched[-1]
        assert last.payment < Decimal("0.11")
        assert last.payment > Decimal("0.00")

    def test_round_half_up_avoids_truncation(self):
        """ROUND_HALF_UP doesn't overpay every month, so no early payoff."""
        loan = LoanParams(
            principal=Decimal("20"),
            annual_rate=Decimal("4.4"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
        )
        with warnings.catch_warnings():
            # If a warning leaked we'd want to know — make it an error.
            warnings.simplefilter("error", EarlyPayoffWarning)
            sched = amortization_schedule(loan)
        # ROUND_HALF_UP rounds $0.100152 → $0.10; loan never fully amortizes
        # at that payment, so the final payment trues up at month 360.
        assert len(sched) == 361

    def test_warning_is_filterable(self):
        """Standard warnings filtering should suppress the warning."""
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=EarlyPayoffWarning)
            # No warning should propagate; the schedule still truncates.
            sched = amortization_schedule(self.LOAN)
        assert sched[-1].balance == Decimal("0.00")
