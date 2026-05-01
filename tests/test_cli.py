"""Tests for the v0.4.0 command-line interface.

The CLI is implemented in ``mortgagemath.__main__`` and registered as
the ``mortgagemath`` console script in ``pyproject.toml``.  These
tests exercise both the in-process ``main()`` entry point and (for one
case) the ``python -m mortgagemath`` subprocess form, to confirm both
invocations work and that the no-args default still routes to
``selfcheck`` (preserving the v0.2.x contract).
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys

import pytest

from mortgagemath import __main__ as cli


def test_no_args_runs_selfcheck(capsys):
    """Calling ``main()`` with no args defaults to selfcheck (preserves
    v0.2.x ``python -m mortgagemath`` behavior)."""
    rc = cli.main([])
    out = capsys.readouterr().out
    assert rc == 0
    assert "self-check" in out
    assert "All checks passed." in out


def test_selfcheck_subcommand(capsys):
    rc = cli.main(["selfcheck"])
    assert rc == 0
    assert "All checks passed." in capsys.readouterr().out


def test_subprocess_no_args_matches_selfcheck():
    """``python -m mortgagemath`` with no args still exits 0 and runs
    selfcheck (subprocess form, the FreeBSD-validation use case)."""
    result = subprocess.run(
        [sys.executable, "-m", "mortgagemath"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "All checks passed." in result.stdout


# ---------------------------------------------------------------------------
# `payment` subcommand
# ---------------------------------------------------------------------------


def test_payment_basic(capsys):
    rc = cli.main(
        [
            "payment",
            "--principal",
            "131250",
            "--rate",
            "4.25",
            "--term-months",
            "360",
        ]
    )
    assert rc == 0
    assert capsys.readouterr().out.strip() == "645.68"


def test_payment_with_rounding_flag(capsys):
    """CFPB-style HALF_UP payment ($761.78) vs ROUND_UP default ($761.79)."""
    rc = cli.main(
        [
            "payment",
            "--principal",
            "162000",
            "--rate",
            "3.875",
            "--term-months",
            "360",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
        ]
    )
    assert rc == 0
    assert capsys.readouterr().out.strip() == "761.78"


def test_payment_canadian_semi_annual(capsys):
    """Canadian j_2=4.9% mortgage Olivier §13.4 Chans first term."""
    rc = cli.main(
        [
            "payment",
            "--principal",
            "350100",
            "--rate",
            "4.9",
            "--term-months",
            "36",
            "--amortization-period-months",
            "240",
            "--compounding",
            "semi_annual",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
        ]
    )
    assert rc == 0
    assert capsys.readouterr().out.strip() == "2281.73"


def test_payment_with_arm_rate_change(capsys):
    """ARM via --rate-change. The reported `payment` is the *initial*
    period's level payment; the schedule is what changes after the rate
    change."""
    rc = cli.main(
        [
            "payment",
            "--principal",
            "200000",
            "--rate",
            "5.7",
            "--term-months",
            "360",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
            "--rate-change",
            "61:7.2",
        ]
    )
    assert rc == 0
    assert capsys.readouterr().out.strip() == "1160.80"


# ---------------------------------------------------------------------------
# `schedule` subcommand — output formats
# ---------------------------------------------------------------------------


_LOAN_FLAGS = [
    "--principal",
    "131250",
    "--rate",
    "4.25",
    "--term-months",
    "360",
]


def test_schedule_csv_format(capsys):
    rc = cli.main(["schedule", *_LOAN_FLAGS, "--format", "csv"])
    assert rc == 0
    out = capsys.readouterr().out
    reader = csv.reader(io.StringIO(out))
    rows = list(reader)
    assert rows[0] == [
        "number",
        "payment",
        "interest",
        "principal",
        "total_interest",
        "balance",
    ]
    # 360 payment rows + 1 header + 1 opening row = 362 lines.
    assert len(rows) == 362
    # Spot-check first payment.
    assert rows[2][1] == "645.68"


def test_schedule_json_format(capsys):
    rc = cli.main(["schedule", *_LOAN_FLAGS, "--format", "json"])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert isinstance(payload, list)
    assert len(payload) == 361  # opening row + 360 payments
    # Decimal values are serialized as strings to preserve cents.
    first_payment = payload[1]
    assert first_payment["payment"] == "645.68"
    assert isinstance(first_payment["interest"], str)


def test_schedule_table_format_default(capsys):
    rc = cli.main(["schedule", *_LOAN_FLAGS])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Payment" in out
    assert "Balance" in out
    # Table has 1 header + 361 schedule rows.
    assert out.count("\n") == 362


def test_schedule_with_arm(capsys):
    """Schedule honors --rate-change and recasts at the boundary."""
    rc = cli.main(
        [
            "schedule",
            "--principal",
            "200000",
            "--rate",
            "5.7",
            "--term-months",
            "360",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
            "--rate-change",
            "61:7.2",
            "--format",
            "json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload[60]["payment"] == "1160.80"  # last row at initial rate
    # Row 61 is the first row after the rate change; payment recasts.
    assert payload[61]["payment"] != "1160.80"


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


def test_bad_rate_change_format_exits_two():
    """argparse type errors exit with status 2 (standard convention)."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["payment", "-p", "1000", "-r", "5", "-t", "12", "--rate-change", "bad"])
    assert exc.value.code == 2


def test_rate_change_no_recast_suffix(capsys):
    """The ``:no_recast`` suffix produces a RateChange with recast=False."""
    rc = cli.main(
        [
            "schedule",
            "--principal",
            "100000",
            "--rate",
            "5",
            "--term-months",
            "360",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
            "--rate-change",
            "61:6:no_recast",
            "--format",
            "json",
        ]
    )
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    # Without recast, level payment stays equal to the initial value
    # for non-final rows.
    initial = payload[1]["payment"]
    assert payload[100]["payment"] == initial


def test_rate_change_invalid_suffix():
    with pytest.raises(SystemExit) as exc:
        cli.main(["payment", "-p", "100000", "-r", "5", "-t", "360", "--rate-change", "61:6:bogus"])
    assert exc.value.code == 2


def test_rate_change_non_numeric_value_exits_two():
    """Bad numeric inside a well-formed colon split (line 161-162 path)."""
    with pytest.raises(SystemExit) as exc:
        cli.main(["payment", "-p", "100000", "-r", "5", "-t", "360", "--rate-change", "abc:5"])
    assert exc.value.code == 2


def test_rate_change_cap_factor_via_cli(capsys):
    """ProEducate via CLI: --rate-change 13:12:cap=1.075 — year 2 P&I $613.20."""
    import json as _json

    rc = cli.main(
        [
            "schedule",
            "--principal",
            "65000",
            "--rate",
            "10",
            "--term-months",
            "360",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
            "--rate-change",
            "13:12:cap=1.075",
            "--format",
            "json",
        ]
    )
    assert rc == 0
    payload = _json.loads(capsys.readouterr().out)
    assert payload[13]["payment"] == "613.20"


def test_rate_change_cap_with_no_recast_rejected():
    """``cap=`` and ``no_recast`` together are rejected by the RateChange dataclass."""
    with pytest.raises(SystemExit) as exc:
        cli.main(
            [
                "payment",
                "-p",
                "100000",
                "-r",
                "5",
                "-t",
                "360",
                "--rate-change",
                "13:6:no_recast:cap=1.05",
            ]
        )
    assert exc.value.code == 2


def test_rate_change_cap_unparseable_factor():
    with pytest.raises(SystemExit) as exc:
        cli.main(
            ["payment", "-p", "100000", "-r", "5", "-t", "360", "--rate-change", "13:6:cap=zzz"]
        )
    assert exc.value.code == 2


def test_rate_change_explicit_recast_suffix(capsys):
    """Explicit ``:recast`` suffix is the same as omitting it."""
    rc = cli.main(
        [
            "payment",
            "--principal",
            "100000",
            "--rate",
            "5",
            "--term-months",
            "360",
            "--rate-change",
            "61:6:recast",
        ]
    )
    assert rc == 0


def test_actual_360_with_start_date(capsys):
    """Fannie Mae §1103 SARM via the CLI, using --start-date."""
    rc = cli.main(
        [
            "payment",
            "--principal",
            "25000000",
            "--rate",
            "5.5",
            "--term-months",
            "120",
            "--amortization-period-months",
            "360",
            "--day-count",
            "actual/360",
            "--payment-rounding",
            "ROUND_HALF_UP",
            "--interest-rounding",
            "ROUND_HALF_UP",
            "--start-date",
            "2018-12-01",
        ]
    )
    assert rc == 0
    assert capsys.readouterr().out.strip() == "141947.25"


# ---------------------------------------------------------------------------
# selfcheck failure path (monkeypatched broken helpers)
# ---------------------------------------------------------------------------


def test_selfcheck_returns_one_on_failure(monkeypatch, capsys):
    """If reference helpers return broken values, every per-check
    failure must increment the counter and ``selfcheck`` must exit 1
    with a FAIL summary."""
    from decimal import Decimal

    def _broken_payment(_loan):
        return Decimal("0.00")

    class _BrokenInstallment:
        interest = principal = balance = Decimal("0.00")

    def _broken_schedule(_loan):
        return [_BrokenInstallment() for _ in range(400)]

    monkeypatch.setattr(cli, "monthly_payment", _broken_payment)
    monkeypatch.setattr(cli, "amortization_schedule", _broken_schedule)
    rc = cli.main([])
    out = capsys.readouterr().out
    assert rc == 1
    assert "check(s) failed" in out
    assert "FAIL" in out
