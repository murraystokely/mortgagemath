"""Command-line interface for ``mortgagemath``.

Three subcommands:

* ``mortgagemath selfcheck`` — post-install reference checks.  The
  default when no subcommand is given (preserves the v0.2.x
  ``python -m mortgagemath`` behavior).  Recomputes a small set of
  well-known published values (CFPB H-25(B), Goldstein §10.3 Ex 1,
  Fannie Mae §1103) and reports pass/fail.  Exits 0 on every match,
  1 otherwise.

* ``mortgagemath payment`` — print the periodic P&I for a loan.

* ``mortgagemath schedule`` — print the full amortization schedule
  in ``--format table`` (default), ``csv``, or ``json``.

Both ``payment`` and ``schedule`` accept the full ``LoanParams``
surface as flags whose names mirror the field names
(``--principal``, ``--rate``, ``--term-months``, etc.).  ARMs are
supported via repeatable ``--rate-change EFFECTIVE_PMT:NEW_RATE``
flags (append ``:no_recast`` to disable the level-payment
recomputation).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from decimal import Decimal
from typing import IO

from mortgagemath import (
    BalanceTracking,
    Compounding,
    DayCount,
    LoanParams,
    PaymentFrequency,
    PaymentRounding,
    RateChange,
    __version__,
    amortization_schedule,
    monthly_payment,
    periodic_payment,
)

# ---------------------------------------------------------------------------
# selfcheck (default subcommand)
# ---------------------------------------------------------------------------


def _check(name: str, got: object, expected: object) -> bool:
    """Print one pass/fail line. Return True iff got == expected."""
    ok = got == expected
    marker = "OK  " if ok else "FAIL"
    print(f"  [{marker}] {name}: got {got}  expected {expected}")
    return ok


def _run_selfcheck() -> int:
    """Run the post-install self-check. Return 0 on success, 1 on any failure."""
    print(f"mortgagemath {__version__} self-check\n")
    failures = 0

    cfpb = LoanParams(
        principal=Decimal("162000"),
        annual_rate=Decimal("3.875"),
        term_months=360,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
    )
    if not _check(
        "CFPB H-25(B) $162,000 / 3.875% / 30yr monthly P&I",
        monthly_payment(cfpb),
        Decimal("761.78"),
    ):
        failures += 1

    goldstein = LoanParams(
        principal=Decimal("563"),
        annual_rate=Decimal("12"),
        term_months=5,
        balance_tracking=BalanceTracking.CARRY_PRECISION,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
    )
    if not _check(
        "Goldstein §10.3 Ex 1 $563 / 12% / 5mo monthly P&I",
        monthly_payment(goldstein),
        Decimal("116.00"),
    ):
        failures += 1

    sched = amortization_schedule(goldstein)
    rows = [
        (1, "5.63", "110.37", "452.63"),
        (2, "4.53", "111.47", "341.16"),
        (3, "3.41", "112.59", "228.57"),
        (4, "2.29", "113.71", "114.85"),
        (5, "1.15", "114.85", "0.00"),
    ]
    for n, ei, ep, eb in rows:
        inst = sched[n]
        if not _check(
            f"  Goldstein row {n} (interest, principal, balance)",
            (inst.interest, inst.principal, inst.balance),
            (Decimal(ei), Decimal(ep), Decimal(eb)),
        ):
            failures += 1

    fanniemae = LoanParams(
        principal=Decimal("25000000"),
        annual_rate=Decimal("5.5"),
        term_months=120,
        amortization_period_months=360,
        day_count=DayCount.ACTUAL_360,
        payment_rounding=PaymentRounding.ROUND_HALF_UP,
        interest_rounding=PaymentRounding.ROUND_HALF_UP,
        start_date=date(2018, 12, 1),
    )
    if not _check(
        "Fannie Mae §1103 Tier 2 SARM monthly P&I",
        monthly_payment(fanniemae),
        Decimal("141947.25"),
    ):
        failures += 1
    fm_sched = amortization_schedule(fanniemae)
    if not _check(
        "Fannie Mae §1103 balloon at term-120",
        fm_sched[120].balance,
        Decimal("20885505.83"),
    ):
        failures += 1

    print()
    if failures:
        print(f"{failures} check(s) failed.")
        return 1
    print("All checks passed.")
    return 0


# ---------------------------------------------------------------------------
# Argument parsing helpers (shared by `payment` and `schedule`)
# ---------------------------------------------------------------------------


def _parse_rate_change(s: str) -> RateChange:
    """Parse a ``--rate-change`` value.

    Syntax: ``EFFECTIVE_PMT:NEW_RATE[:SUFFIX]*`` where each ``SUFFIX``
    is one of ``recast``, ``no_recast``, or ``cap=FACTOR``.  Defaults
    are ``recast`` and no cap.
    """
    parts = s.split(":")
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            f"--rate-change expects EFFECTIVE_PMT:NEW_RATE[:no_recast][:cap=FACTOR], got {s!r}"
        )
    try:
        effective = int(parts[0])
        rate = Decimal(parts[1])
    except (ValueError, ArithmeticError) as exc:
        raise argparse.ArgumentTypeError(f"--rate-change parse error in {s!r}: {exc}") from exc

    recast = True
    cap_factor: Decimal | None = None
    for suffix in parts[2:]:
        if suffix.lower() == "no_recast":
            recast = False
        elif suffix.lower() == "recast":
            recast = True
        elif suffix.lower().startswith("cap="):
            try:
                cap_factor = Decimal(suffix[len("cap=") :])
            except ArithmeticError as exc:
                raise argparse.ArgumentTypeError(
                    f"--rate-change cap= parse error in {suffix!r}: {exc}"
                ) from exc
        else:
            raise argparse.ArgumentTypeError(
                f"--rate-change suffix must be 'recast', 'no_recast', or 'cap=FACTOR'; "
                f"got {suffix!r}"
            )
    return RateChange(
        effective_payment_number=effective,
        new_annual_rate=rate,
        recast=recast,
        payment_cap_factor=cap_factor,
    )


def _parse_date(s: str) -> date:
    return date.fromisoformat(s)


def _add_loan_args(parser: argparse.ArgumentParser) -> None:
    """Attach LoanParams flags to ``parser``."""
    parser.add_argument("--principal", "-p", type=Decimal, required=True)
    parser.add_argument("--rate", "-r", type=Decimal, required=True, dest="annual_rate")
    parser.add_argument("--term-months", "-t", type=int, required=True)
    parser.add_argument(
        "--day-count",
        choices=[e.value for e in DayCount],
        default=DayCount.THIRTY_360.value,
    )
    parser.add_argument(
        "--payment-rounding",
        choices=[e.value for e in PaymentRounding],
        default=PaymentRounding.ROUND_UP.value,
    )
    parser.add_argument(
        "--interest-rounding",
        choices=[e.value for e in PaymentRounding],
        default=PaymentRounding.ROUND_HALF_UP.value,
    )
    parser.add_argument("--start-date", type=_parse_date, default=None)
    parser.add_argument("--amortization-period-months", type=int, default=None)
    parser.add_argument(
        "--balance-tracking",
        choices=[e.value for e in BalanceTracking],
        default=BalanceTracking.ROUND_EACH.value,
    )
    parser.add_argument(
        "--compounding",
        choices=[e.value for e in Compounding],
        default=Compounding.MONTHLY.value,
    )
    parser.add_argument(
        "--payment-frequency",
        choices=[e.value for e in PaymentFrequency],
        default=PaymentFrequency.MONTHLY.value,
    )
    parser.add_argument(
        "--rate-change",
        action="append",
        default=[],
        type=_parse_rate_change,
        metavar="EFFECTIVE_PMT:NEW_RATE[:no_recast][:cap=FACTOR]",
        help="Rate change for ARM (repeatable). Examples: --rate-change 61:7.2, "
        "--rate-change 13:12:cap=1.075 (7.5%% payment cap)",
    )
    parser.add_argument(
        "--payment-override",
        type=Decimal,
        default=None,
        metavar="AMOUNT",
        help="Pin the periodic payment to AMOUNT instead of deriving it from "
        "the closed-form annuity formula. The schedule's final row absorbs "
        "the residual. Reproduces the FHLBB 1935 'given-payment, find-term' "
        "convention. Currently incompatible with --rate-change.",
    )
    parser.add_argument(
        "--fee-per-period",
        type=Decimal,
        default=Decimal("0"),
        metavar="AMOUNT",
        help="Flat amount added to each Installment.payment on top of the "
        "closed-form interest+principal value. Models the modern French "
        "*assurance emprunteur* loading and the 1852 Credit Foncier "
        "*annuité* shape. Default 0 (no loading).",
    )


def _params_from_args(args: argparse.Namespace) -> LoanParams:
    return LoanParams(
        principal=args.principal,
        annual_rate=args.annual_rate,
        term_months=args.term_months,
        day_count=DayCount(args.day_count),
        payment_rounding=PaymentRounding(args.payment_rounding),
        interest_rounding=PaymentRounding(args.interest_rounding),
        start_date=args.start_date,
        amortization_period_months=args.amortization_period_months,
        balance_tracking=BalanceTracking(args.balance_tracking),
        compounding=Compounding(args.compounding),
        payment_frequency=PaymentFrequency(args.payment_frequency),
        rate_schedule=tuple(args.rate_change),
        payment_override=args.payment_override,
        fee_per_period=args.fee_per_period,
    )


# ---------------------------------------------------------------------------
# Schedule output formatters
# ---------------------------------------------------------------------------


_SCHEDULE_COLUMNS = ("number", "payment", "interest", "principal", "total_interest", "balance")


def _emit_schedule_table(loan: LoanParams, out: IO[str]) -> None:
    sched = amortization_schedule(loan)
    headers = ("#", "Payment", "Interest", "Principal", "Total Int", "Balance")
    widths = (5, 14, 14, 14, 16, 16)
    out.write("  ".join(h.rjust(w) for h, w in zip(headers, widths, strict=True)) + "\n")
    for inst in sched:
        # Data column widths match the header widths above so right-edges align.
        out.write(
            f"  {inst.number:>3d}  "
            f"{inst.payment:>14,.2f}  "
            f"{inst.interest:>14,.2f}  "
            f"{inst.principal:>14,.2f}  "
            f"{inst.total_interest:>16,.2f}  "
            f"{inst.balance:>16,.2f}\n"
        )


def _emit_schedule_csv(loan: LoanParams, out: IO[str]) -> None:
    sched = amortization_schedule(loan)
    writer = csv.writer(out)
    writer.writerow(_SCHEDULE_COLUMNS)
    for inst in sched:
        writer.writerow(
            [
                inst.number,
                str(inst.payment),
                str(inst.interest),
                str(inst.principal),
                str(inst.total_interest),
                str(inst.balance),
            ]
        )


def _emit_schedule_json(loan: LoanParams, out: IO[str]) -> None:
    sched = amortization_schedule(loan)
    payload = [
        {
            "number": inst.number,
            "payment": str(inst.payment),
            "interest": str(inst.interest),
            "principal": str(inst.principal),
            "total_interest": str(inst.total_interest),
            "balance": str(inst.balance),
        }
        for inst in sched
    ]
    json.dump(payload, out, indent=2)
    out.write("\n")


_FORMATTERS = {
    "table": _emit_schedule_table,
    "csv": _emit_schedule_csv,
    "json": _emit_schedule_json,
}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mortgagemath",
        description="Cent-accurate mortgage amortization. "
        "Run with no arguments to perform the post-install self-check.",
    )
    parser.add_argument("--version", action="version", version=f"mortgagemath {__version__}")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("selfcheck", help="Run post-install reference checks")

    p_payment = sub.add_parser("payment", help="Print the periodic P&I for a loan")
    _add_loan_args(p_payment)

    p_schedule = sub.add_parser("schedule", help="Print the full amortization schedule")
    _add_loan_args(p_schedule)
    p_schedule.add_argument("--format", choices=tuple(_FORMATTERS), default="table")

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Return shell exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd in (None, "selfcheck"):
        return _run_selfcheck()

    params = _params_from_args(args)

    if args.cmd == "payment":
        print(periodic_payment(params))
        return 0

    if args.cmd == "schedule":
        _FORMATTERS[args.format](params, sys.stdout)
        return 0

    parser.error(f"unknown command: {args.cmd}")  # pragma: no cover
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess test
    sys.exit(main())
