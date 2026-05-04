"""Convenience constructors for common mortgage configurations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from mortgagemath._types import (
    BalanceTracking,
    Compounding,
    DayCount,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
)


def _decimal(value: Decimal | int | str, field_name: str) -> Decimal:
    """Normalize public constructor inputs to Decimal."""
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a Decimal, int, or decimal string") from exc


def _years_to_months(years: int, field_name: str) -> int:
    """Convert a positive whole-year term to months."""
    if years <= 0:
        raise ValueError(f"{field_name} must be positive, got {years}")
    return years * 12


def fixed_rate_mortgage(
    principal: Decimal | int | str,
    annual_rate: Decimal | int | str,
    term_years: int,
    *,
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_UP,
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    balance_tracking: BalanceTracking = BalanceTracking.ROUND_EACH,
) -> LoanParams:
    """Return ``LoanParams`` for a fully amortizing fixed-rate mortgage.

    This is the generic easy-mode constructor for the common 30/360,
    monthly-payment case. Use ``LoanParams`` directly when you need
    non-monthly payments, ARMs, Actual/360, balloon terms, or other
    less common conventions.
    """
    return LoanParams(
        principal=_decimal(principal, "principal"),
        annual_rate=_decimal(annual_rate, "annual_rate"),
        term_months=_years_to_months(term_years, "term_years"),
        payment_rounding=payment_rounding,
        interest_rounding=interest_rounding,
        balance_tracking=balance_tracking,
    )


def us_30_year_fixed(
    principal: Decimal | int | str,
    annual_rate: Decimal | int | str,
    *,
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_UP,
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    balance_tracking: BalanceTracking = BalanceTracking.ROUND_EACH,
) -> LoanParams:
    """Return ``LoanParams`` for a standard US 30-year fixed-rate mortgage."""
    return fixed_rate_mortgage(
        principal,
        annual_rate,
        30,
        payment_rounding=payment_rounding,
        interest_rounding=interest_rounding,
        balance_tracking=balance_tracking,
    )


def us_15_year_fixed(
    principal: Decimal | int | str,
    annual_rate: Decimal | int | str,
    *,
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_UP,
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    balance_tracking: BalanceTracking = BalanceTracking.ROUND_EACH,
) -> LoanParams:
    """Return ``LoanParams`` for a standard US 15-year fixed-rate mortgage."""
    return fixed_rate_mortgage(
        principal,
        annual_rate,
        15,
        payment_rounding=payment_rounding,
        interest_rounding=interest_rounding,
        balance_tracking=balance_tracking,
    )


def canada_fixed_j2(
    principal: Decimal | int | str,
    annual_rate: Decimal | int | str,
    *,
    amortization_years: int = 25,
    term_years: int | None = None,
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY,
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    balance_tracking: BalanceTracking = BalanceTracking.ROUND_EACH,
) -> LoanParams:
    """Return ``LoanParams`` for a Canadian fixed-rate ``j_2`` mortgage.

    Canadian residential rates are commonly quoted as ``j_2``:
    nominal annual rates compounded semi-annually under Interest Act
    convention. If ``term_years`` is provided and is shorter than the
    amortization, the returned loan models the fixed term as a balloon
    period on the longer amortization basis.
    """
    amortization_months = _years_to_months(amortization_years, "amortization_years")
    term_months = (
        amortization_months if term_years is None else _years_to_months(term_years, "term_years")
    )
    amortization_period_months = None if term_years is None else amortization_months
    return LoanParams(
        principal=_decimal(principal, "principal"),
        annual_rate=_decimal(annual_rate, "annual_rate"),
        term_months=term_months,
        amortization_period_months=amortization_period_months,
        payment_rounding=payment_rounding,
        interest_rounding=interest_rounding,
        balance_tracking=balance_tracking,
        compounding=Compounding.SEMI_ANNUAL,
        payment_frequency=payment_frequency,
    )


def us_actual_360_commercial(
    principal: Decimal | int | str,
    annual_rate: Decimal | int | str,
    *,
    term_years: int,
    amortization_years: int,
    start_date: date,
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
) -> LoanParams:
    """Return ``LoanParams`` for a US Actual/360 commercial mortgage.

    This preset matches the Fannie Mae Multifamily style: monthly
    payments, monthly compounding, Actual/360 interest accrual, and a
    possible balloon when ``term_years`` is shorter than
    ``amortization_years``.
    """
    term_months = _years_to_months(term_years, "term_years")
    amortization_months = _years_to_months(amortization_years, "amortization_years")
    return LoanParams(
        principal=_decimal(principal, "principal"),
        annual_rate=_decimal(annual_rate, "annual_rate"),
        term_months=term_months,
        amortization_period_months=amortization_months,
        day_count=DayCount.ACTUAL_360,
        payment_rounding=payment_rounding,
        interest_rounding=interest_rounding,
        start_date=start_date,
    )


def fixed_payment_mortgage(
    principal: Decimal | int | str,
    annual_rate: Decimal | int | str,
    payment: Decimal | int | str,
    *,
    term_months: int,
    payment_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    interest_rounding: PaymentRounding = PaymentRounding.ROUND_HALF_UP,
    balance_tracking: BalanceTracking = BalanceTracking.CARRY_PRECISION,
) -> LoanParams:
    """Return ``LoanParams`` for a fixed-rate loan with a chosen payment.

    The returned loan uses ``payment_override``: the schedule applies
    the chosen periodic payment until the final row trues up the
    remaining balance. The default carry-precision balance tracking is
    the historical given-payment convention validated against the
    FHLBB 1935 Direct-Reduction Plan A fixture.
    """
    return LoanParams(
        principal=_decimal(principal, "principal"),
        annual_rate=_decimal(annual_rate, "annual_rate"),
        term_months=term_months,
        payment_rounding=payment_rounding,
        interest_rounding=interest_rounding,
        balance_tracking=balance_tracking,
        payment_override=_decimal(payment, "payment"),
    )
