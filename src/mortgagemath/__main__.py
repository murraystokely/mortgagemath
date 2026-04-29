"""Post-install self-check: ``python -m mortgagemath``.

Computes a small set of well-known reference values against the
installed library and reports pass/fail. Exits 0 if every check
matches the published source exactly, 1 otherwise. Useful for
verifying that a freshly-installed wheel matches the same numbers
the test suite validates — without needing to clone the repo or
install a test runner.
"""

from __future__ import annotations

import sys
from datetime import date
from decimal import Decimal

from mortgagemath import (
    BalanceTracking,
    DayCount,
    LoanParams,
    PaymentRounding,
    __version__,
    amortization_schedule,
    monthly_payment,
)


def _check(name: str, got: object, expected: object) -> bool:
    """Print one pass/fail line. Return True iff got == expected."""
    ok = got == expected
    marker = "OK  " if ok else "FAIL"
    print(f"  [{marker}] {name}: got {got}  expected {expected}")
    return ok


def main() -> int:
    """Run the self-check. Return 0 on success, 1 on any failure."""
    print(f"mortgagemath {__version__} self-check\n")
    failures = 0

    # 1. CFPB H-25(B) sample Closing Disclosure. CFPB rounds HALF_UP
    #    (unrounded value is $761.7840...; the library's ROUND_UP default
    #    would ceiling to $761.79).
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

    # 2. Goldstein "Finite Mathematics and Its Applications", 12 ed., §10.3
    #    Example 1 + Table 1 — full 5-row schedule under carry-precision.
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

    # 3. Fannie Mae Multifamily Guide §1103 — Tier 2 SARM, $25M / 5.5% /
    #    10-year term, 30-year amortization, Actual/360, balloon at term.
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


if __name__ == "__main__":  # pragma: no cover - exercised via subprocess test
    sys.exit(main())
