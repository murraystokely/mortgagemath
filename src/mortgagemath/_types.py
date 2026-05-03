"""Types for mortgage calculations."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum

_PENNY = Decimal("0.01")


class EarlyPayoffWarning(UserWarning):
    """Schedule terminated before ``term_months`` due to rounding overpayment.

    For very small principals, the cent-rounded monthly payment can overpay
    the closed-form value by enough that the schedule fully amortizes before
    the requested term.  When this happens, ``amortization_schedule`` truncates
    the schedule at the actual payoff month (with the final row trued up to
    land balance at exactly zero) and emits this warning.

    Filter via the standard :mod:`warnings` machinery::

        import warnings
        from mortgagemath import EarlyPayoffWarning

        warnings.filterwarnings("ignore", category=EarlyPayoffWarning)
        # or, to promote it to an exception:
        warnings.simplefilter("error", EarlyPayoffWarning)
    """


class DayCount(Enum):
    """Day-count convention for interest calculation.

    US residential mortgages typically use 30/360.
    US commercial loans often use Actual/360.
    """

    THIRTY_360 = "30/360"
    ACTUAL_360 = "actual/360"


class PaymentRounding(Enum):
    """Rounding convention for monetary amounts.

    ROUND_UP (ceiling to nearest cent) is used by most US lenders for the
    monthly payment amount.  ROUND_HALF_UP (standard rounding) is used
    for monthly interest calculations.  ROUND_HALF_EVEN (banker's rounding)
    is included so fixtures from lenders or worked examples that use it
    can be modeled.
    """

    ROUND_UP = "ROUND_UP"
    ROUND_HALF_UP = "ROUND_HALF_UP"
    ROUND_HALF_EVEN = "ROUND_HALF_EVEN"


class Compounding(Enum):
    """How the annual rate compounds to a periodic rate.

    ``MONTHLY`` (the default) is the US residential / commercial
    convention: the periodic rate is ``annual_rate / payments_per_year``
    treated as a simple division. For monthly payments under monthly
    compounding this is exactly the v0.2.x behavior.

    ``SEMI_ANNUAL`` is the Canadian convention (Interest Act §6): the
    quoted rate ``j_2`` is per year compounded semi-annually, and the
    periodic rate per payment is
    ``(1 + j_2 / 200) ** (2 / payments_per_year) - 1``.
    For a 5% Canadian mortgage with monthly payments this is
    ``(1.025) ** (1/6) - 1 ≈ 0.41239...%``, **not** ``5/12``.

    ``ANNUAL`` treats the quoted rate as the effective annual rate;
    the periodic rate is ``(1 + annual / 100) ** (1 / payments_per_year) - 1``.
    Included for completeness.
    """

    MONTHLY = "monthly"
    SEMI_ANNUAL = "semi_annual"
    ANNUAL = "annual"


class PaymentFrequency(Enum):
    """How often payments are made.

    The ``payments_per_year`` mapping is the standard banking convention
    used by the worked-example sources the library validates against
    (e.g. the Canadian Olivier and eCampus Ontario texts use exactly
    52 weekly / 26 biweekly / 24 semi-monthly periods per year).
    """

    MONTHLY = "monthly"
    SEMI_MONTHLY = "semi_monthly"
    BIWEEKLY = "biweekly"
    WEEKLY = "weekly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"

    @property
    def payments_per_year(self) -> int:
        """Number of payments per calendar year."""
        return {
            PaymentFrequency.MONTHLY: 12,
            PaymentFrequency.SEMI_MONTHLY: 24,
            PaymentFrequency.BIWEEKLY: 26,
            PaymentFrequency.WEEKLY: 52,
            PaymentFrequency.QUARTERLY: 4,
            PaymentFrequency.ANNUAL: 1,
        }[self]


class BalanceTracking(Enum):
    """How the running balance is tracked between schedule rows.

    ROUND_EACH (the default) is how most US residential lender statements
    are computed: each month's balance is rounded to cents, and next
    month's interest is computed from that rounded balance.  Validated
    against CFPB sample disclosures and most published bank statements.

    CARRY_PRECISION carries the unrounded balance internally between rows
    and rounds only for display.  This is the Excel-default behavior and
    the convention used by graduate-level CRE finance textbooks (Geltner
    et al., LibreTexts Olivier, eCampus Ontario).  For long-horizon loans
    the two algorithms diverge by single-digit cents at each row, with
    the displayed total interest sometimes drifting by a few dollars
    over a 30-year term.

    The ACTUAL_360 day-count always uses CARRY_PRECISION internally
    regardless of this field, because day-counted interest accrual is
    only meaningful with full balance precision.
    """

    ROUND_EACH = "round_each"
    CARRY_PRECISION = "carry_precision"


@dataclass(frozen=True, slots=True)
class RateChange:
    """A scheduled rate change for an Adjustable-Rate Mortgage (ARM).

    Used in ``LoanParams.rate_schedule`` (a tuple of ``RateChange``).
    Goldstein 12e §10.4 Example 13 5/1 ARM is the canonical fixture:
    ``RateChange(effective_payment_number=61, new_annual_rate=Decimal("7.2"))``
    moves the rate from the initial 5.7% to 7.2% starting at payment 61
    and recasts the level payment over the remaining 300 payments.

    Args:
        effective_payment_number: 1-indexed payment ordinal at which
            the new rate first takes effect.  Interest accrual for that
            payment uses the new rate.  Must be ``>= 2`` (a rate change
            at payment 1 is the same as constructing the loan with that
            initial rate).
        new_annual_rate: The new annual rate in percent (e.g.
            ``Decimal("7.2")``).  Must be positive.
        recast: When True (the default), recompute the level payment
            for the remaining payments using the new periodic rate
            applied to the current balance.  When False, keep the prior
            level payment — the rate change still affects every
            subsequent period's interest accrual, and any residual is
            absorbed by the final-row trueup.
        payment_cap_factor: Optional bound on the recast payment as a
            multiple of the prior period's payment (e.g.
            ``Decimal("1.075")`` for a 7.5% annual cap).  Only meaningful
            when ``recast=True``.  When set, the new payment is
            ``min(closed_form_recast, prior_payment * cap_factor)``.
            If the cap binds and the new periodic interest exceeds the
            capped payment, the unpaid interest is capitalized into
            the balance (negative amortization) — the corresponding
            ``Installment.principal`` will be negative and the balance
            will grow.  Validated against the ProEducate ARM payment-
            cap example ($65,000 / 10% Year 1 → 12% Year 2 / 7.5% cap;
            year-2 P&I $613.20, cumulative neg-am $420.90).
    """

    effective_payment_number: int
    new_annual_rate: Decimal
    recast: bool = True
    payment_cap_factor: Decimal | None = None

    def __post_init__(self) -> None:
        """Validate single-instance invariants."""
        if self.effective_payment_number < 2:
            raise ValueError(
                f"effective_payment_number must be >= 2, got "
                f"{self.effective_payment_number}. A rate change at payment 1 "
                f"is the same as constructing the loan with that initial rate."
            )
        if self.new_annual_rate <= 0:
            raise ValueError(f"new_annual_rate must be positive, got {self.new_annual_rate}")
        if self.payment_cap_factor is not None:
            if self.payment_cap_factor <= 0:
                raise ValueError(
                    f"payment_cap_factor must be positive when set, got {self.payment_cap_factor}"
                )
            if not self.recast:
                raise ValueError(
                    "payment_cap_factor is only meaningful when recast=True; "
                    "with recast=False the prior payment carries through unchanged."
                )


@dataclass(frozen=True, slots=True)
class LoanParams:
    """Parameters defining a fixed-rate mortgage.

    Args:
        principal: Original loan amount (e.g. Decimal("131250.00")).
        annual_rate: Annual interest rate as a percentage
            (e.g. Decimal("4.25") for 4.25%).
        term_months: Loan term in months — the number of payments the
            schedule will produce (e.g. 360 for a 30-year fully
            amortizing residential mortgage; 120 for a 10-year SARM).
        day_count: Day-count convention. Defaults to 30/360.
        payment_rounding: How to round the monthly payment to the nearest
            cent. Defaults to ROUND_UP.
        interest_rounding: How to round each month's interest charge.
            Defaults to ROUND_HALF_UP.
        start_date: Date of the first interest-accrual period (the issue
            date). Required for ACTUAL_360 schedules; ignored for 30/360.
            Period 1 covers the calendar month containing this date and
            the first payment is due on the same day of the next month.
            Per Fannie Mae §1103, an issue date of December 1, 2018
            produces a first payment on January 1, 2019 with period 1
            spanning December 2018 (31 days).
        amortization_period_months: Period over which the closed-form
            payment is computed. ``None`` (the default) means it equals
            ``term_months`` — i.e., the loan amortizes fully over its
            term. Set this larger than ``term_months`` for **balloon
            loans**: the level monthly payment is computed as if the
            loan amortized over ``amortization_period_months``, but the
            schedule terminates after ``term_months`` payments, with the
            unpaid principal at term equal to ``Installment.balance``
            on the final row (this is the borrower's balloon payment).
            Per the Fannie Mae §1103 Tier 2 SARM example, a 10-year
            ($120 months) SARM on a 30-year (360 months) amortization
            basis is expressed as ``term_months=120,
            amortization_period_months=360``; the published balloon at
            term 120 is $20,885,505.83.
        balance_tracking: How the running balance propagates between
            rows. ``ROUND_EACH`` (default) is the round-each-month
            convention used by US residential lenders and validated
            against CFPB sample disclosures. ``CARRY_PRECISION`` is the
            Excel-default convention used by graduate-level CRE finance
            textbooks (Geltner, LibreTexts, eCampus). Ignored for
            ACTUAL_360 day count, which always uses carry-precision.
        compounding: How the annual rate compounds to a periodic rate.
            ``MONTHLY`` (default, US convention) divides the annual rate
            by ``payments_per_year``. ``SEMI_ANNUAL`` is the Canadian
            convention required by *Interest Act* §6. ``ANNUAL`` treats
            the quoted rate as the effective annual rate.
        payment_frequency: How often payments are made.  Defaults to
            ``MONTHLY`` (12/yr).  Other supported cadences are
            ``SEMI_MONTHLY`` (24/yr), ``BIWEEKLY`` (26/yr),
            ``WEEKLY`` (52/yr), ``QUARTERLY`` (4/yr), and ``ANNUAL``
            (1/yr).  ``term_months * payments_per_year`` must be
            divisible by 12.
        payment_override: When set, pin the periodic payment to this
            value (in the loan's currency) instead of deriving it from
            the closed-form annuity formula.  The schedule's final row
            absorbs whatever residual balance remains after
            ``term_months - 1`` full payments — the final payment is
            ``balance_before_final + final_period_interest`` rounded
            once to cents.  This unlocks the historical "given-payment,
            find-term" convention used by the FHLBB *Federal Home Loan
            Bank Review* of March 1935 (Direct-Reduction Plan A:
            $3,000 / 6% / $30 monthly / 138 full payments + 139th of
            $29.27).  Defaults to ``None`` (use the closed-form value).
            Currently incompatible with non-empty ``rate_schedule``.
    """

    principal: Decimal
    annual_rate: Decimal
    term_months: int
    day_count: DayCount = DayCount.THIRTY_360
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_UP
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP
    start_date: date | None = None
    amortization_period_months: int | None = None
    balance_tracking: BalanceTracking = BalanceTracking.ROUND_EACH
    compounding: Compounding = Compounding.MONTHLY
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
    rate_schedule: tuple[RateChange, ...] = ()
    payment_override: Decimal | None = None

    def __post_init__(self) -> None:
        """Validate cross-field invariants."""
        # Day-counted accrual is only well-defined for monthly cadence + monthly
        # compounding. The §1103 §1104 §1106 commercial-loan worked examples
        # we validate against are all monthly + monthly + Actual/360.
        if self.day_count == DayCount.ACTUAL_360:
            if self.payment_frequency != PaymentFrequency.MONTHLY:
                raise ValueError(
                    f"DayCount.ACTUAL_360 requires PaymentFrequency.MONTHLY, "
                    f"got {self.payment_frequency}"
                )
            if self.compounding != Compounding.MONTHLY:
                raise ValueError(
                    f"DayCount.ACTUAL_360 requires Compounding.MONTHLY, got {self.compounding}"
                )

        # Number of payments must be a whole number for the schedule loop.
        ppy = self.payment_frequency.payments_per_year
        if self.term_months <= 0:
            raise ValueError(f"term_months must be positive, got {self.term_months}")
        if (self.term_months * ppy) % 12 != 0:
            raise ValueError(
                f"term_months={self.term_months} * payments_per_year={ppy} "
                f"is not divisible by 12; cannot derive a whole number of "
                f"payments. Adjust term_months so the total is an integer "
                f"number of payments at the chosen frequency."
            )

        # amortization_period_months validation lives here (in v0.7.0,
        # moved from periodic_payment) so payment_override loans —
        # which return the override directly without invoking
        # periodic_payment's guards — get the same checks.
        if self.amortization_period_months is not None:
            if self.amortization_period_months <= 0:
                raise ValueError(
                    f"amortization_period_months must be positive when set, "
                    f"got {self.amortization_period_months}"
                )
            if self.amortization_period_months < self.term_months:
                raise ValueError(
                    f"amortization_period_months ({self.amortization_period_months}) "
                    f"must be >= term_months ({self.term_months}). A shorter "
                    f"amortization basis would over-amortize and drive the "
                    f"balance negative before the term ends."
                )
            if (self.amortization_period_months * ppy) % 12 != 0:
                raise ValueError(
                    f"amortization_period_months={self.amortization_period_months} "
                    f"* payments_per_year={ppy} is not divisible by 12."
                )

        # Rate-schedule validation. v0.4.0 ships Tier 1 ARMs (explicit
        # rate-change list) for THIRTY_360 fully-amortizing loans only;
        # ACTUAL_360 + ARM and balloon + ARM stay deferred to a later
        # release that brings published fixtures motivating them.
        if self.rate_schedule:
            if self.day_count != DayCount.THIRTY_360:
                raise ValueError(
                    "rate_schedule is only supported for DayCount.THIRTY_360 in v0.4.0; "
                    f"got {self.day_count}"
                )
            amort = self.amortization_period_months
            if amort is not None and amort != self.term_months:
                raise ValueError(
                    "rate_schedule with a balloon "
                    "(amortization_period_months != term_months) is not supported in v0.4.0"
                )
            total_payments = (self.term_months * ppy) // 12
            prev = 0
            for rc in self.rate_schedule:
                if rc.effective_payment_number <= prev:
                    raise ValueError(
                        "rate_schedule entries must have strictly increasing "
                        f"effective_payment_number; got {rc.effective_payment_number} "
                        f"after {prev}"
                    )
                if rc.effective_payment_number > total_payments:
                    raise ValueError(
                        f"rate_schedule entry effective_payment_number="
                        f"{rc.effective_payment_number} exceeds total_payments="
                        f"{total_payments}"
                    )
                prev = rc.effective_payment_number

        # payment_override constraints. v0.6.0 supports the override
        # for fully-amortizing fixed-rate loans only; combining it with
        # rate_schedule semantics is deferred until a published source
        # motivates it.
        if self.payment_override is not None:
            if self.payment_override <= 0:
                raise ValueError(
                    f"payment_override must be positive when set, got {self.payment_override}"
                )
            # Reject non-cent overrides: a Decimal("99.999") would let
            # public Installment rows carry sub-cent payment amounts,
            # which violates the cents-precision contract.
            if self.payment_override != self.payment_override.quantize(_PENNY):
                raise ValueError(
                    f"payment_override must be denominated in whole cents "
                    f"(two-decimal Decimal), got {self.payment_override}"
                )
            if self.rate_schedule:
                raise ValueError(
                    "payment_override is currently incompatible with rate_schedule. "
                    "When a published source motivates combining them, the override will "
                    "take precedence and ARM payment caps will be ignored."
                )
            # The override path treats the schedule as a fixed-rate,
            # fully-amortizing loan with the user's chosen payment
            # absorbed by the final-row trueup. Balloon basis (amort
            # period > term) was never tested with the override, and
            # without a published source it's not on the roadmap.
            if (
                self.amortization_period_months is not None
                and self.amortization_period_months != self.term_months
            ):
                raise ValueError(
                    "payment_override is supported for fully-amortizing loans only. "
                    "Set amortization_period_months=None or amortization_period_months "
                    "== term_months when using payment_override."
                )

    @property
    def _total_payments(self) -> int:
        """Total number of payments in the schedule."""
        ppy = self.payment_frequency.payments_per_year
        return (self.term_months * ppy) // 12

    @property
    def _amort_payments(self) -> int:
        """Number of payments used for the closed-form payment formula.

        For balloon loans this is larger than ``_total_payments``.
        """
        if self.amortization_period_months is None:
            return self._total_payments
        ppy = self.payment_frequency.payments_per_year
        return (self.amortization_period_months * ppy) // 12

    # Back-compat: many internals predate the rename and refer to "periods"
    # under monthly+monthly. Keep this property; callers that expect a count
    # of payments still work, since under monthly+monthly the total payment
    # count equals the term in months.
    @property
    def _amort_periods(self) -> int:
        """Periods used for the closed-form payment formula."""
        return self._amort_payments


@dataclass(frozen=True, slots=True)
class Installment:
    """A single payment in an amortization schedule.

    Invariant: ``principal + interest == payment`` for every installment.
    """

    number: int
    payment: Decimal
    interest: Decimal
    principal: Decimal
    total_interest: Decimal
    balance: Decimal
