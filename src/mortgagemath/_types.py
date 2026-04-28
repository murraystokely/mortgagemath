"""Types for mortgage calculations."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


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


@dataclass(frozen=True, slots=True)
class LoanParams:
    """Parameters defining a fixed-rate mortgage.

    Args:
        principal: Original loan amount (e.g. Decimal("131250.00")).
        annual_rate: Annual interest rate as a percentage
            (e.g. Decimal("4.25") for 4.25%).
        term_months: Loan term in months (e.g. 360 for 30 years).
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
    """

    principal: Decimal
    annual_rate: Decimal
    term_months: int
    day_count: DayCount = DayCount.THIRTY_360
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_UP
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP
    start_date: date | None = None


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