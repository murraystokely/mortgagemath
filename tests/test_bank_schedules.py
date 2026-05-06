"""Validate computed schedules against real bank statement data.

Test fixtures are auto-discovered from tests/schedules/*.toml + *.csv
pairs. See tests/schedules/README.md for the fixture format.
"""

from datetime import date
from decimal import Decimal

from mortgagemath import (
    BalanceTracking,
    Compounding,
    DayCount,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
    RateChange,
    amortization_schedule,
    periodic_payment,
)


def _loan_from_toml(toml_data: dict) -> LoanParams:
    """Build a LoanParams from a TOML fixture's [loan] section."""
    loan = toml_data["loan"]
    start_date = loan.get("start_date")
    if isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)
    balance_tracking_str = loan.get("balance_tracking", "round_each")
    compounding_str = loan.get("compounding", "monthly")
    payment_frequency_str = loan.get("payment_frequency", "monthly")
    rate_schedule = tuple(
        RateChange(
            effective_payment_number=int(rc["effective_payment_number"]),
            new_annual_rate=Decimal(rc["new_annual_rate"]),
            recast=rc.get("recast", True),
            payment_cap_factor=(
                Decimal(rc["payment_cap_factor"]) if "payment_cap_factor" in rc else None
            ),
        )
        for rc in loan.get("rate_schedule", ())
    )
    payment_override = loan.get("payment_override")
    currency_unit_str = loan.get("currency_unit")
    fee_per_period = loan.get("fee_per_period")
    return LoanParams(
        principal=Decimal(loan["principal"]),
        annual_rate=Decimal(loan["annual_rate"]),
        term_months=loan["term_months"],
        day_count=DayCount(loan.get("day_count", "30/360")),
        payment_rounding=PaymentRounding(loan["payment_rounding"]),
        interest_rounding=PaymentRounding(loan["interest_rounding"]),
        start_date=start_date,
        amortization_period_months=loan.get("amortization_period_months"),
        balance_tracking=BalanceTracking(balance_tracking_str),
        compounding=Compounding(compounding_str),
        payment_frequency=PaymentFrequency(payment_frequency_str),
        rate_schedule=rate_schedule,
        payment_override=Decimal(payment_override) if payment_override is not None else None,
        currency_unit=Decimal(currency_unit_str)
        if currency_unit_str is not None
        else Decimal("0.01"),
        interest_only_months=loan.get("interest_only_months", 0),
        fee_per_period=(Decimal(fee_per_period) if fee_per_period is not None else Decimal("0")),
    )


class TestBankSchedules:
    def test_periodic_payment_matches(self, bank_schedule):
        """The computed periodic payment must match the TOML expected value.

        Accepts either ``monthly_payment`` (legacy key, used by all
        v0.2.x fixtures) or ``periodic_payment`` (new in v0.3.0,
        preferred for non-monthly cadences).
        """
        toml_data, _ = bank_schedule
        loan = _loan_from_toml(toml_data)
        expected_str = toml_data["expected"].get("periodic_payment") or toml_data["expected"].get(
            "monthly_payment"
        )
        if expected_str is None:
            raise AssertionError(
                "Fixture must declare expected.periodic_payment or expected.monthly_payment"
            )
        expected = Decimal(expected_str)
        assert periodic_payment(loan) == expected

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

            # Optional fee column for fee-loaded fixtures.  Older CSVs
            # without a `fee` column trivially accept the default
            # Decimal("0.00").
            if "fee" in row:
                expected_fee = Decimal(row["fee"])
                assert inst.fee == expected_fee, f"Payment #{n}: fee {inst.fee} != {expected_fee}"

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
        # The balloon is the unpaid balance after the final scheduled
        # payment of the loan's *term*. For monthly cadence this is row
        # ``term_months``; for non-monthly cadence the schedule has
        # ``term_months * payments_per_year / 12`` rows after the
        # opening row.
        ppy = loan.payment_frequency.payments_per_year
        final_index = loan.term_months * ppy // 12
        assert sched[final_index].balance == Decimal(balloon), (
            f"Balloon at term: {sched[final_index].balance} != {balloon}"
        )

    def test_amortization_ranges_match(self, bank_schedule):
        """Validate published amortization worksheet ranges, if any.

        Some sources publish calculator-style ranges rather than individual
        rows: a beginning payment number, ending payment number, ending
        balance, cumulative principal, and cumulative interest. These ranges
        are source-backed aggregate anchors and are stricter than validating
        the payment alone.
        """
        toml_data, _ = bank_schedule
        ranges = toml_data.get("expected", {}).get("amortization_ranges", ())
        if not ranges:
            return
        loan = _loan_from_toml(toml_data)
        sched = amortization_schedule(loan)

        for range_data in ranges:
            start = int(range_data["start_payment"])
            end = int(range_data["end_payment"])
            rows = sched[start : end + 1]

            expected_balance = Decimal(range_data["balance"])
            expected_principal = Decimal(range_data["principal"])
            expected_interest = Decimal(range_data["interest"])

            assert sched[end].balance == expected_balance, (
                f"Payments {start}-{end}: balance {sched[end].balance} != "
                f"{expected_balance}"
            )
            principal = sum(inst.principal for inst in rows)
            assert principal == expected_principal, (
                f"Payments {start}-{end}: principal {principal} != "
                f"{expected_principal}"
            )
            interest = sum(inst.interest for inst in rows)
            assert interest == expected_interest, (
                f"Payments {start}-{end}: interest {interest} != {expected_interest}"
            )
