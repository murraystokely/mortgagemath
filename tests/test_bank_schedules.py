"""Validate computed schedules against real bank statement data.

Test fixtures are auto-discovered from tests/schedules/*.toml + *.csv
pairs. See tests/schedules/README.md for the fixture format.
"""

from datetime import date
from decimal import Decimal

from mortgagemath import (
    DayCount,
    LoanParams,
    PaymentRounding,
    amortization_schedule,
    monthly_payment,
)


def _loan_from_toml(toml_data: dict) -> LoanParams:
    """Build a LoanParams from a TOML fixture's [loan] section."""
    loan = toml_data["loan"]
    start_date = loan.get("start_date")
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    return LoanParams(
        principal=Decimal(loan["principal"]),
        annual_rate=Decimal(loan["annual_rate"]),
        term_months=loan["term_months"],
        day_count=DayCount(loan["day_count"]),
        payment_rounding=PaymentRounding(loan["payment_rounding"]),
        interest_rounding=PaymentRounding(loan["interest_rounding"]),
        start_date=start_date,
        amortization_period_months=loan.get("amortization_period_months"),
    )


class TestBankSchedules:

    def test_monthly_payment_matches(self, bank_schedule):
        """The computed monthly payment must match the TOML expected value."""
        toml_data, _ = bank_schedule
        loan = _loan_from_toml(toml_data)
        expected = Decimal(toml_data["expected"]["monthly_payment"])
        assert monthly_payment(loan) == expected

    def test_schedule_matches_csv(self, bank_schedule):
        """Every row in the CSV must match the computed schedule."""
        toml_data, csv_rows = bank_schedule
        if not csv_rows:
            return  # header-only CSV; only monthly_payment is validated
        loan = _loan_from_toml(toml_data)
        sched = amortization_schedule(loan)

        for row in csv_rows:
            n = int(row["payment"])
            inst = sched[n]

            expected_payment = Decimal(row["payment_amount"])
            expected_principal = Decimal(row["principal"])
            expected_interest = Decimal(row["interest"])
            expected_balance = Decimal(row["balance"])

            assert inst.payment == expected_payment, (
                f"Payment #{n}: payment {inst.payment} != {expected_payment}"
            )
            assert inst.principal == expected_principal, (
                f"Payment #{n}: principal {inst.principal} != {expected_principal}"
            )
            assert inst.interest == expected_interest, (
                f"Payment #{n}: interest {inst.interest} != {expected_interest}"
            )
            assert inst.balance == expected_balance, (
                f"Payment #{n}: balance {inst.balance} != {expected_balance}"
            )

    def test_balloon_at_term_matches(self, bank_schedule):
        """Validate the published balloon at term, if any.

        For balloon loans (term shorter than amortization period), the
        unpaid principal at the loan's term is the balloon the borrower
        owes alongside the final regular payment. Some sources (e.g.
        Fannie Mae §1103) publish this value; the library exposes it as
        ``schedule[term].balance``.
        """
        toml_data, _ = bank_schedule
        balloon = toml_data.get("expected", {}).get("balloon_at_term")
        if balloon is None:
            return
        loan = _loan_from_toml(toml_data)
        sched = amortization_schedule(loan)
        assert sched[loan.term_months].balance == Decimal(balloon), (
            f"Balloon at term: {sched[loan.term_months].balance} != {balloon}"
        )
