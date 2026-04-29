# Changelog

All notable changes to `mortgagemath` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-04-26

### Added

- `BalanceTracking` enum and `LoanParams.balance_tracking` field, with
  values `ROUND_EACH` (the default — US residential lender convention,
  unchanged from prior releases) and `CARRY_PRECISION` (Excel-default
  carry-precision: full-precision balance carried internally between
  rows, per-row figures rounded to cents only for display). Affects
  30/360 schedules; Actual/360 schedules already used carry-precision
  unconditionally.
- Test fixture for the [Geltner et al. *Commercial Real Estate
  Analysis*](https://s3-eu-west-1.amazonaws.com/s3-euw1-ap-pe-ws4-cws-documents.ri-prod/9781041076391/online-chapters/9781041081197_Online_content.pdf)
  Chapter 20 Exhibit 20-6 CPM example ($1M / 12% / 30yr → monthly P&I
  $10,286.13). The library reproduces 7 of the 9 published rows
  exactly under `BalanceTracking.CARRY_PRECISION`; the two remaining
  rows contain editorial arithmetic typos in the textbook itself
  (verified: `principal + interest != payment` in the published
  values). See `docs/accuracy.md` and
  `tests/test_schedule.py::TestGeltnerCPM`.

## [0.1.1] - 2026-04-29

### Fixed

- `amortization_schedule()` no longer walks the balance past zero for
  very small principals.  When 30/360 round-each-balance accounting
  amortizes a loan before `term_months` due to monthly payment
  rounding overpayment, the schedule is now truncated at the actual
  payoff month with the final row trued up to land balance at exactly
  `$0.00`.  Reference example: `$20 / 4.4% / 30yr` previously produced
  360 rows with the balance walking from `$0.02` (month 300) through
  `−$7.18` (month 359) before a `−$7.21` "payment" trued it up; it now
  produces 302 rows ending cleanly at month 301.

### Added

- `EarlyPayoffWarning` (a `UserWarning` subclass) is emitted when the
  schedule truncates due to rounding overpayment.  Filterable via the
  standard `warnings` module.  Exported from the top-level package.

## [0.1.0] - 2026-04-28

First public release.

### Added

- `monthly_payment(LoanParams)` — closed-form annuity payment, Decimal
  end-to-end, configurable rounding mode.
- `amortization_schedule(LoanParams)` — full month-by-month schedule
  guaranteeing `principal + interest == payment` per row and final
  balance of exactly `Decimal("0.00")` for fully amortizing loans.
- `LoanParams` dataclass with `principal`, `annual_rate`, `term_months`,
  plus optional `day_count`, `payment_rounding`, `interest_rounding`,
  `start_date`, and `amortization_period_months`.
- `DayCount` enum: `THIRTY_360` (default — US residential round-each-
  balance accounting) and `ACTUAL_360` (commercial day-counted accrual
  with full-precision internal balance).
- `PaymentRounding` enum: `ROUND_UP` (ceiling — most US residential
  lenders), `ROUND_HALF_UP`, and `ROUND_HALF_EVEN` (banker's rounding).
- Native balloon-loan support: when `amortization_period_months >
  term_months`, the closed-form payment uses the longer basis, the
  schedule produces `term_months` rows, and the final row's `balance`
  is the balloon owed at term.
- `Installment` dataclass exposing `number`, `payment`, `interest`,
  `principal`, `total_interest`, `balance`.
- Test fixtures validated against the [CFPB H-25(B) sample Closing
  Disclosure](https://files.consumerfinance.gov/f/201403_cfpb_closing-disclosure_cover-H25B.pdf),
  the [Fannie Mae Multifamily Selling and Servicing Guide
  §1103](https://mfguide.fanniemae.com/node/5286) Tier 2 SARM example
  (monthly P&I + $20,885,505.83 balloon at term 120, both exact),
  OpenStax *Contemporary Mathematics* worked examples, Las Positas
  *Math for Liberal Arts* examples, the Mississippi State Extension
  P3920 publication, and synthetic half-cent boundary cases. See
  [`docs/accuracy.md`](docs/accuracy.md) for the full source table.
- 100% test coverage on `src/mortgagemath/`. 144 tests, including
  parametric structural invariants and per-fixture validation.
- CI workflows: tests on Python 3.11/3.12/3.13/3.14 (Ubuntu),
  ruff lint + format check, mypy `--strict`, dynamic coverage badge.
- GitHub issue templates for cent-mismatch submissions and general
  bug/feature reports.
- `py.typed` marker for downstream type-checkers.

### Documentation

- `README.md` with installation, quick start, rounding/day-count
  conventions, accuracy summary, and PyPI badges.
- `docs/accuracy.md` listing every source the library reproduces
  exactly.
- `docs/future-work.md` listing investigated sources that did not
  match exactly (and why).
- `tests/schedules/README.md` documenting the fixture schema.
- `CONTRIBUTING.md` pointing reporters at the issue templates and
  contributors at the fixture submission flow.
