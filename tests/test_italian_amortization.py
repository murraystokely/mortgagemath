"""Structural tests for AmortizationMethod.ITALIAN (ammortamento italiano).

Fixture-level validation against the published Università di Cagliari,
telemutuo.it and Andrea il Matematico schedules lives in
``test_bank_schedules.py``.  These tests cover the invariants and the
error paths that no fixture exercises.
"""

import re
from decimal import Decimal
from itertools import pairwise

import pytest

from mortgagemath import (
    AmortizationMethod,
    BalanceTracking,
    Compounding,
    DayCount,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
    RateChange,
    amortization_schedule,
    loan_summary,
    periodic_payment,
    principal_quota,
)


def italian_loan(**overrides) -> LoanParams:
    """A 50k / 10% / 4 annual-payment constant-principal loan."""
    params = {
        "principal": Decimal("50000"),
        "annual_rate": Decimal("10"),
        "term_months": 48,
        "payment_rounding": PaymentRounding.ROUND_HALF_UP,
        "interest_rounding": PaymentRounding.ROUND_HALF_UP,
        "payment_frequency": PaymentFrequency.ANNUAL,
        "amortization_method": AmortizationMethod.ITALIAN,
    }
    params.update(overrides)
    return LoanParams(**params)


class TestPrincipalQuota:
    def test_quota_is_principal_over_payments(self):
        assert principal_quota(italian_loan()) == Decimal("12500.00")

    def test_quota_rejects_french_loans(self):
        loan = italian_loan(amortization_method=AmortizationMethod.FRENCH)
        with pytest.raises(ValueError, match=re.escape("applies only to")):
            principal_quota(loan)

    def test_quota_honors_currency_unit(self):
        loan = italian_loan(currency_unit=Decimal("1"))
        assert principal_quota(loan) == Decimal("12500")

    def test_quota_rejects_non_positive_principal(self):
        # LoanParams permits it; the guard lives at call time, matching
        # periodic_payment()'s behavior for FRENCH loans.
        loan = italian_loan(principal=Decimal("0"))
        with pytest.raises(ValueError, match=re.escape("principal must be positive")):
            principal_quota(loan)

    def test_quota_rounds_with_payment_rounding(self):
        # 10000 / 3 = 3333.33... — ROUND_UP must give 3333.34.
        loan = italian_loan(
            principal=Decimal("10000"),
            term_months=36,
            payment_rounding=PaymentRounding.ROUND_UP,
        )
        assert principal_quota(loan) == Decimal("3333.34")


class TestItalianSchedule:
    def test_principal_is_constant_except_final_row(self):
        loan = italian_loan()
        sched = amortization_schedule(loan)
        quota = principal_quota(loan)
        non_final = [row.principal for row in sched[1:-1]]
        assert non_final == [quota] * len(non_final)
        assert len(non_final) == 3

    def test_payment_strictly_decreases(self):
        payments = [row.payment for row in amortization_schedule(italian_loan())[1:]]
        assert all(a > b for a, b in pairwise(payments))

    def test_balance_lands_exactly_at_zero(self):
        assert amortization_schedule(italian_loan())[-1].balance == Decimal("0.00")

    def test_principal_plus_interest_equals_payment(self):
        for row in amortization_schedule(italian_loan())[1:]:
            assert row.principal + row.interest == row.payment

    def test_principal_repaid_sums_to_original(self):
        sched = amortization_schedule(italian_loan())
        assert sum(row.principal for row in sched[1:]) == Decimal("50000")

    def test_final_row_absorbs_rounding_residual(self):
        # 10000 over 3 annual payments with ROUND_UP leaves a residual
        # the final row must absorb: 3 x 3333.34 = 10000.02 > principal.
        loan = italian_loan(
            principal=Decimal("10000"),
            term_months=36,
            payment_rounding=PaymentRounding.ROUND_UP,
        )
        sched = amortization_schedule(loan)
        assert sched[-1].balance == Decimal("0.00")
        assert sched[-1].principal == Decimal("3333.32")
        assert sum(row.principal for row in sched[1:]) == Decimal("10000")

    def test_zero_interest_loan(self):
        loan = italian_loan(annual_rate=Decimal("0"))
        sched = amortization_schedule(loan)
        assert all(row.interest == Decimal("0.00") for row in sched[1:])
        assert sched[-1].balance == Decimal("0.00")


class TestItalianSummary:
    def test_summary_reports_no_level_payment(self):
        s = loan_summary(italian_loan())
        assert s.periodic_payment is None
        assert s.first_payment == Decimal("17500.00")
        assert s.num_payments == 4

    def test_summary_repr_shows_first_payment(self):
        assert "first_payment=17,500.00" in repr(loan_summary(italian_loan()))

    def test_total_interest_matches_schedule(self):
        s = loan_summary(italian_loan())
        assert s.total_interest == Decimal("12500.00")
        assert s.total_paid == Decimal("62500.00")


class TestItalianRejectedCombinations:
    def test_periodic_payment_raises(self):
        with pytest.raises(ValueError, match=re.escape("no single periodic payment")):
            periodic_payment(italian_loan())

    def test_actual_360_rejected(self):
        # Monthly cadence so the ACTUAL_360 frequency guard passes and
        # the ITALIAN-specific day-count guard is what fires.
        with pytest.raises(ValueError, match=re.escape("requires DayCount.THIRTY_360")):
            italian_loan(
                day_count=DayCount.ACTUAL_360,
                payment_frequency=PaymentFrequency.MONTHLY,
            )

    def test_carry_precision_rejected(self):
        with pytest.raises(ValueError, match=re.escape("requires BalanceTracking.ROUND_EACH")):
            italian_loan(balance_tracking=BalanceTracking.CARRY_PRECISION)

    def test_rate_schedule_rejected(self):
        with pytest.raises(ValueError, match=re.escape("rate_schedule is not supported")):
            italian_loan(
                rate_schedule=(
                    RateChange(effective_payment_number=2, new_annual_rate=Decimal("11")),
                )
            )

    def test_payment_override_rejected(self):
        with pytest.raises(ValueError, match=re.escape("payment_override is incompatible")):
            italian_loan(payment_override=Decimal("1000"))

    def test_interest_only_rejected(self):
        with pytest.raises(ValueError, match=re.escape("interest_only_months is not supported")):
            italian_loan(interest_only_months=12)

    def test_fee_per_period_rejected(self):
        with pytest.raises(ValueError, match=re.escape("fee_per_period is not supported")):
            italian_loan(fee_per_period=Decimal("25"))

    def test_balloon_rejected(self):
        with pytest.raises(ValueError, match="balloon"):
            italian_loan(term_months=48, amortization_period_months=60)


class TestSemiAnnualFrequency:
    def test_payments_per_year(self):
        assert PaymentFrequency.SEMI_ANNUAL.payments_per_year == 2

    def test_nominal_period_rate_is_annual_over_two(self):
        # telemutuo.it states the convention explicitly: 6% annual -> 3%
        # per semester under the default (nominal) compounding.
        loan = italian_loan(
            principal=Decimal("50000"),
            annual_rate=Decimal("6"),
            term_months=60,
            payment_frequency=PaymentFrequency.SEMI_ANNUAL,
        )
        assert amortization_schedule(loan)[1].interest == Decimal("1500.00")

    def test_effective_annual_compounding_uses_equivalent_rate(self):
        # Cagliari: (1.07)^(1/2) - 1 = 0.034408..., so the first
        # interest charge on 600,000 is 20,645 and not 21,000.
        loan = italian_loan(
            principal=Decimal("600000"),
            annual_rate=Decimal("7"),
            term_months=48,
            compounding=Compounding.ANNUAL,
            payment_frequency=PaymentFrequency.SEMI_ANNUAL,
            currency_unit=Decimal("1"),
        )
        assert amortization_schedule(loan)[1].interest == Decimal("20645")

    def test_semi_annual_works_for_french_loans_too(self):
        loan = LoanParams(
            principal=Decimal("100000"),
            annual_rate=Decimal("6"),
            term_months=60,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            payment_frequency=PaymentFrequency.SEMI_ANNUAL,
        )
        sched = amortization_schedule(loan)
        assert len(sched) == 11  # row 0 + 10 semi-annual payments
        assert sched[-1].balance == Decimal("0.00")

    def test_term_must_divide_into_whole_semi_annual_payments(self):
        with pytest.raises(ValueError, match=re.escape("not divisible by 12")):
            LoanParams(
                principal=Decimal("100000"),
                annual_rate=Decimal("6"),
                term_months=7,
                payment_rounding=PaymentRounding.ROUND_HALF_UP,
                interest_rounding=PaymentRounding.ROUND_HALF_UP,
                payment_frequency=PaymentFrequency.SEMI_ANNUAL,
            )
