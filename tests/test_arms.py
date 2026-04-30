"""Tests for v0.4.0 ARM (rate-change schedule) features.

Covers:
- ``RateChange`` per-instance validation.
- ``LoanParams.rate_schedule`` cross-field validation (strictly
  increasing, within bounds, day-count restriction).
- Structural invariants on synthetic ARMs: ``principal + interest ==
  payment`` per row, final balance zero, interest reflects post-recast
  rate, recast=True vs recast=False semantics, multiple consecutive
  rate changes.
- Empty ``rate_schedule`` produces byte-identical output to the same
  loan constructed without the field (the v0.3.0 fast path).

The library reproduces Goldstein 12e §10.4 Example 13 (5/1 ARM)
*conceptually* — the recast formula, rate-change semantics, and
month-61 interest match Goldstein's published values. However,
Goldstein's published "balance after pmt 60" of $185,405.12 is
computed via textbook closed-form PV math (``pmt * (1 -
(1+r)^-(n-k))/r``, using the rounded payment $1,160.80), whereas the
library produces a row-by-row schedule whose balance at month 60
diverges by 13-26 cents from Goldstein's PV value (carry-precision gives
$185,405.25; round-each gives $185,405.38). The library's recast
payment at month 61 ($1,334.16) therefore differs by 1¢ from
Goldstein's $1,334.15 (computed off the PV-derived $185,405.12).
This reflects a fundamental algorithmic difference, not a library
bug; it's documented in ``docs/v0.4-plan.md``. v0.4.0 ships the ARM
API without a published-source row-level fixture.
"""

from decimal import Decimal

import pytest

from mortgagemath import (
    BalanceTracking,
    DayCount,
    LoanParams,
    PaymentRounding,
    RateChange,
    amortization_schedule,
    periodic_payment,
)


class TestRateChangeValidation:
    def test_effective_payment_number_must_be_at_least_two(self):
        with pytest.raises(ValueError, match="effective_payment_number must be >= 2"):
            RateChange(effective_payment_number=1, new_annual_rate=Decimal("5"))

    def test_effective_payment_number_zero_rejected(self):
        with pytest.raises(ValueError, match="effective_payment_number must be >= 2"):
            RateChange(effective_payment_number=0, new_annual_rate=Decimal("5"))

    def test_negative_rate_rejected(self):
        with pytest.raises(ValueError, match="new_annual_rate must be positive"):
            RateChange(effective_payment_number=12, new_annual_rate=Decimal("-1"))

    def test_zero_rate_rejected(self):
        with pytest.raises(ValueError, match="new_annual_rate must be positive"):
            RateChange(effective_payment_number=12, new_annual_rate=Decimal("0"))


class TestLoanParamsRateScheduleValidation:
    def _base(self, **overrides):
        params = dict(
            principal=Decimal("100000"),
            annual_rate=Decimal("5"),
            term_months=360,
        )
        params.update(overrides)
        return params

    def test_non_increasing_rejected(self):
        with pytest.raises(ValueError, match="strictly increasing"):
            LoanParams(
                **self._base(),
                rate_schedule=(
                    RateChange(effective_payment_number=60, new_annual_rate=Decimal("6")),
                    RateChange(effective_payment_number=60, new_annual_rate=Decimal("7")),
                ),
            )

    def test_decreasing_rejected(self):
        with pytest.raises(ValueError, match="strictly increasing"):
            LoanParams(
                **self._base(),
                rate_schedule=(
                    RateChange(effective_payment_number=120, new_annual_rate=Decimal("6")),
                    RateChange(effective_payment_number=60, new_annual_rate=Decimal("7")),
                ),
            )

    def test_past_term_rejected(self):
        with pytest.raises(ValueError, match="exceeds total_payments"):
            LoanParams(
                **self._base(),
                rate_schedule=(
                    RateChange(effective_payment_number=361, new_annual_rate=Decimal("6")),
                ),
            )

    def test_actual_360_with_rate_schedule_rejected(self):
        with pytest.raises(ValueError, match=r"DayCount\.THIRTY_360"):
            LoanParams(
                **self._base(),
                day_count=DayCount.ACTUAL_360,
                payment_rounding=PaymentRounding.ROUND_HALF_UP,
                interest_rounding=PaymentRounding.ROUND_HALF_UP,
                rate_schedule=(
                    RateChange(effective_payment_number=60, new_annual_rate=Decimal("6")),
                ),
            )

    def test_balloon_with_rate_schedule_rejected(self):
        with pytest.raises(ValueError, match="balloon"):
            LoanParams(
                **self._base(term_months=120),
                amortization_period_months=360,
                rate_schedule=(
                    RateChange(effective_payment_number=60, new_annual_rate=Decimal("6")),
                ),
            )

    def test_empty_rate_schedule_is_default(self):
        loan = LoanParams(**self._base())
        assert loan.rate_schedule == ()


# Three loans that exercise each balance-tracking mode and the
# common rate-change cadences.
ARM_PARAMS = [
    pytest.param(
        BalanceTracking.ROUND_EACH,
        (RateChange(effective_payment_number=61, new_annual_rate=Decimal("7"), recast=True),),
        id="round_each_single_recast",
    ),
    pytest.param(
        BalanceTracking.CARRY_PRECISION,
        (RateChange(effective_payment_number=61, new_annual_rate=Decimal("7"), recast=True),),
        id="carry_precision_single_recast",
    ),
    pytest.param(
        BalanceTracking.ROUND_EACH,
        (
            RateChange(effective_payment_number=61, new_annual_rate=Decimal("6"), recast=True),
            RateChange(effective_payment_number=121, new_annual_rate=Decimal("7"), recast=True),
            RateChange(effective_payment_number=181, new_annual_rate=Decimal("8"), recast=True),
        ),
        id="round_each_multi_recast",
    ),
    pytest.param(
        BalanceTracking.CARRY_PRECISION,
        (
            RateChange(effective_payment_number=61, new_annual_rate=Decimal("6"), recast=True),
            RateChange(effective_payment_number=62, new_annual_rate=Decimal("7"), recast=True),
            RateChange(effective_payment_number=63, new_annual_rate=Decimal("8"), recast=True),
        ),
        id="carry_precision_consecutive_recast",
    ),
    pytest.param(
        BalanceTracking.ROUND_EACH,
        (RateChange(effective_payment_number=61, new_annual_rate=Decimal("6"), recast=False),),
        id="round_each_no_recast",
    ),
]


class TestArmStructuralInvariants:
    @pytest.mark.parametrize("balance_tracking, schedule", ARM_PARAMS)
    def test_principal_plus_interest_equals_payment_each_row(self, balance_tracking, schedule):
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.7"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            balance_tracking=balance_tracking,
            rate_schedule=schedule,
        )
        sched = amortization_schedule(loan)
        for inst in sched[1:]:
            assert inst.principal + inst.interest == inst.payment, (
                f"Row #{inst.number}: {inst.principal} + {inst.interest} != {inst.payment}"
            )

    @pytest.mark.parametrize("balance_tracking, schedule", ARM_PARAMS)
    def test_final_balance_is_zero(self, balance_tracking, schedule):
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.7"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            balance_tracking=balance_tracking,
            rate_schedule=schedule,
        )
        sched = amortization_schedule(loan)
        assert sched[-1].balance == Decimal("0.00")


class TestArmRecastSemantics:
    def test_recast_changes_payment_after_rate_change(self):
        """When recast=True, the payment after the rate change differs
        from the initial payment."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.7"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            rate_schedule=(
                RateChange(effective_payment_number=61, new_annual_rate=Decimal("7.2")),
            ),
        )
        sched = amortization_schedule(loan)
        initial_pmt = sched[60].payment
        recast_pmt = sched[61].payment
        assert recast_pmt > initial_pmt

    def test_no_recast_keeps_payment_unchanged(self):
        """When recast=False, the payment field stays equal to the
        initial level payment for every row except possibly the final."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.7"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            rate_schedule=(
                RateChange(
                    effective_payment_number=61, new_annual_rate=Decimal("7.2"), recast=False
                ),
            ),
        )
        sched = amortization_schedule(loan)
        initial_pmt = periodic_payment(loan)
        # All non-final rows should carry the initial level payment.
        for inst in sched[1:-1]:
            assert inst.payment == initial_pmt, (
                f"Row #{inst.number}: payment {inst.payment} != initial {initial_pmt}"
            )

    def test_post_recast_interest_uses_new_rate(self):
        """Interest at row 61 = balance * new_rate, not balance * old_rate."""
        loan = LoanParams(
            principal=Decimal("200000"),
            annual_rate=Decimal("5.7"),
            term_months=360,
            payment_rounding=PaymentRounding.ROUND_HALF_UP,
            interest_rounding=PaymentRounding.ROUND_HALF_UP,
            rate_schedule=(
                RateChange(effective_payment_number=61, new_annual_rate=Decimal("7.2")),
            ),
        )
        sched = amortization_schedule(loan)
        bal_60 = sched[60].balance
        # New rate is 7.2%; periodic = 0.072/12 = 0.006.
        new_periodic = Decimal("7.2") / Decimal("1200")
        expected_int = (bal_60 * new_periodic).quantize(Decimal("0.01"))
        assert sched[61].interest == expected_int


class TestEmptyRateScheduleFastPath:
    def test_empty_rate_schedule_byte_identical_to_no_field(self):
        """Constructing with rate_schedule=() must produce the same
        schedule as constructing without the field (the v0.3.0 fast
        path) — every row, every cell."""
        params_kwargs = dict(
            principal=Decimal("131250"),
            annual_rate=Decimal("4.25"),
            term_months=360,
        )
        loan_default = LoanParams(**params_kwargs)
        loan_empty = LoanParams(**params_kwargs, rate_schedule=())
        sched_default = amortization_schedule(loan_default)
        sched_empty = amortization_schedule(loan_empty)
        assert len(sched_default) == len(sched_empty)
        for a, b in zip(sched_default, sched_empty, strict=True):
            assert a == b
