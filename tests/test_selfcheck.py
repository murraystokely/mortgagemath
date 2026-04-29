"""Tests for the `python -m mortgagemath` self-check entry point."""

import subprocess
import sys
from decimal import Decimal

from mortgagemath import __main__ as selfcheck


def test_selfcheck_main_returns_zero():
    """`main()` must return 0 when every reference value matches."""
    assert selfcheck.main() == 0


def test_selfcheck_module_runs_clean():
    """Invoking the module via `python -m mortgagemath` must exit 0
    and print 'All checks passed.'"""
    result = subprocess.run(
        [sys.executable, "-m", "mortgagemath"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, (
        f"non-zero exit ({result.returncode}); stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    assert "All checks passed." in result.stdout
    assert "FAIL" not in result.stdout


def test_selfcheck_main_returns_one_on_failure(monkeypatch, capsys):
    """If both helpers return broken values, every per-check failure must
    increment the counter, and main() must return 1 with a FAIL summary."""

    def _broken_payment(_loan):
        return Decimal("0.00")

    class _BrokenInstallment:
        interest = principal = balance = Decimal("0.00")

    def _broken_schedule(_loan):
        return [_BrokenInstallment() for _ in range(400)]

    monkeypatch.setattr(selfcheck, "monthly_payment", _broken_payment)
    monkeypatch.setattr(selfcheck, "amortization_schedule", _broken_schedule)
    rc = selfcheck.main()
    out = capsys.readouterr().out
    assert rc == 1
    assert "check(s) failed" in out
    assert "FAIL" in out
