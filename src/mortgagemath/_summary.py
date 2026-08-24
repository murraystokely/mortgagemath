"""Loan summary convenience function."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mortgagemath._payment import periodic_payment
from mortgagemath._schedule import amortization_schedule
from mortgagemath._types import AmortizationMethod, LoanParams


@dataclass(frozen=True, slots=True)
class LoanSummary:
    """High-level summary of a loan's cost and structure.

    Returned by :func:`loan_summary`. All monetary values are
    ``Decimal`` at the loan's currency-unit precision.
    """

    periodic_payment: Decimal | None
    """Level payment per period (excludes fee_per_period).

    ``None`` for :attr:`AmortizationMethod.ITALIAN` loans, whose
    installment decreases every period; read ``first_payment`` or the
    schedule itself instead."""

    first_payment: Decimal
    """Amount of the first scheduled installment (excludes
    fee_per_period). Equal to ``periodic_payment`` for level-payment
    (French) loans; the largest installment for ITALIAN loans."""

    total_paid: Decimal
    """Sum of all scheduled payments over the life of the loan
    (includes fees). For balloon loans this does NOT include the
    balloon balance — see ``total_cost``."""

    total_interest: Decimal
    """Cumulative interest paid over the life of the loan."""

    total_fees: Decimal
    """Cumulative fees paid over the life of the loan."""

    total_principal: Decimal
    """Principal repaid through scheduled payments. For fully
    amortizing loans this equals the original principal. For balloon
    loans this is less than the original principal by the balloon
    amount."""

    balloon_balance: Decimal
    """Remaining balance at the end of the term. Zero for fully
    amortizing loans; the balloon amount for balloon loans."""

    total_cost: Decimal
    """Total cash required to extinguish the debt at term:
    ``total_paid + balloon_balance``. For fully amortizing loans
    this equals ``total_paid``."""

    num_payments: int
    """Number of payments in the schedule (excludes the initial
    balance row)."""

    def __repr__(self) -> str:
        """Compact repr showing payment, total interest, and total paid."""
        if self.periodic_payment is None:
            lead = f"LoanSummary(first_payment={self.first_payment:,}, "
        else:
            lead = f"LoanSummary(payment={self.periodic_payment:,}, "
        parts = f"{lead}total_interest={self.total_interest:,}, total_paid={self.total_paid:,}"
        if self.balloon_balance:
            parts += f", balloon={self.balloon_balance:,}"
        parts += f", n={self.num_payments})"
        return parts


def loan_summary(loan: LoanParams) -> LoanSummary:
    """Compute a high-level summary of a loan's cost and structure.

    This is a convenience wrapper that calls :func:`periodic_payment`
    and :func:`amortization_schedule` internally and extracts the
    values most users need first.

    Args:
        loan: Loan parameters.

    Returns:
        A :class:`LoanSummary` with the periodic payment, total
        interest, total paid, total fees, balloon balance, total
        cost, and number of payments.

    Example::

        >>> from mortgagemath import us_30_year_fixed, loan_summary
        >>> s = loan_summary(us_30_year_fixed("300000", "6.5"))
        >>> s.periodic_payment
        Decimal('1896.21')
        >>> s.total_interest
        Decimal('382628.90')
        >>> s.total_cost
        Decimal('682628.90')
    """
    is_italian = loan.amortization_method == AmortizationMethod.ITALIAN
    pmt = None if is_italian else periodic_payment(loan)
    sched = amortization_schedule(loan)
    # Exclude row 0 (initial balance, no payment).
    payment_rows = sched[1:]
    n = len(payment_rows)
    _ZERO = Decimal("0")
    total_paid = sum((row.payment for row in payment_rows), _ZERO)
    total_interest = payment_rows[-1].total_interest if payment_rows else _ZERO
    total_fees = sum((row.fee for row in payment_rows), _ZERO)
    total_principal = sum((row.principal for row in payment_rows), _ZERO)
    balloon_balance = payment_rows[-1].balance if payment_rows else loan.principal
    total_cost = total_paid + balloon_balance
    return LoanSummary(
        periodic_payment=pmt,
        first_payment=payment_rows[0].payment if payment_rows else _ZERO,
        total_paid=total_paid,
        total_interest=total_interest,
        total_fees=total_fees,
        total_principal=total_principal,
        balloon_balance=balloon_balance,
        total_cost=total_cost,
        num_payments=n,
    )
