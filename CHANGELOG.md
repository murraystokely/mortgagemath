# Changelog

All notable changes to `mortgagemath` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.6.0] - 2026-05-02

### Added

- **`LoanParams.payment_override`** — pin the periodic payment to
  a chosen value instead of deriving it from the closed-form
  annuity formula. The schedule's final row absorbs the residual
  balance, with the published payment computed from the
  full-precision `balance + interest` rounded once. Reproduces
  the historical "given-payment, find-term" convention used by
  pre-1968 American building-and-loan associations and the
  earliest U.S. federal direct-reduction schedules.
- **FHLBB *Federal Home Loan Bank Review* (March 1935)
  Direct-Reduction Plan A fixture** — \$3,000 / 6% / 138 monthly
  payments of \$30 + 139th of \$29.27. The earliest U.S.
  federal-authority publication of a worked direct-reduction
  amortization schedule, validated cell-for-cell against the
  source. (Fixture #36.)
- **`mortgagemath schedule --payment-override AMOUNT`** CLI flag
  exposing the new field.

### Changed

- **Vignette set consolidated from six to four.** The three
  single-fixture vignettes (`arm-regz-h14`, `payment-caps-proeducate`,
  `canadian-j2`) are folded into a new comprehensive
  `examples.qmd` organized by country convention then by loan
  type. The four-vignette set is now: *At a glance*,
  *Validation*, *Examples*, *History*. Every example block in
  the new vignette has a uniform structure: scenario,
  `LoanParams(...)` literal, equivalent CLI invocation, live
  Python chunk producing the schedule and published-source
  anchors, citation + fixture filename.

### Documentation

- `docs/v0.6-plan.md` records the design decisions for this
  release, including the deferred `fee_per_period` field whose
  ship trigger is conditional on retrieving one row-level
  Crédit Foncier or modern French source.
- `docs/sphinx/installation.md` self-check sample updated to
  reflect v0.6.0.

## [0.5.2] - 2026-05-02

### Added

- **8 new validated fixtures** drawn from public-domain and
  open-licensed sources, expanding the suite from 27 to 35:
  - **Skinner §42 Example 1** ($1,000 / 6% / 15-year annual payment;
    public-domain 1913) — first annual-cadence fixture sourced from
    a pre-WWI actuarial textbook.
  - **Skinner §42 Example 3 piano** ($500 / 6% effective annual /
    5-year monthly payment) — first fixture isolating
    `Compounding.ANNUAL` on a monthly-cadence loan, validating the
    actuarial convention of treating the quoted rate as effective
    annual and back-deriving the equivalent nominal-monthly rate.
  - **Arcones SOA FM Manual §4.1 Example 4** ($20,000 / 8% / 12-year
    annual schedule) — full 12-row published schedule from an SOA
    Exam FM / CAS Exam 2 study manual; first multi-row
    annual-cadence fixture in the corpus.
  - **Broverman MIC §2.1 Example 2.7(a) and 2.7(b)** ($12,000 at
    12% / 36 months and 15% / 48 months) — closed-form payment
    anchors at two distinct rates from a perennial SOA Exam FM
    reference text.
  - **eCampus Ontario *Mathematics of Finance* §4.3 Example 4.3.1
    (Pearline)** ($10,000 / 10% / 4-year annual full schedule).
  - **eCampus §4.3 Exercise 2 (Erika)** ($32,600 / 4.83% / 9-year
    monthly with year-aggregate anchors).
  - **eCampus §4.3 Exercise 3 (Johnetta)** ($20,200 / 3.53% /
    8-year monthly with mid-schedule probe at payment 60).
- **Self-contained bibliographic schema for fixture TOMLs.** Every
  fixture's ``[source]`` block now carries ``short_label``,
  ``bib_key``, ``bib_title``, and ``citation`` fields with full
  prose citations (authors, title, edition, publisher, year, ISBN,
  URL where available). Fixtures sharing a source share a
  ``bib_key`` and the bibliography emits one entry per key.

### Changed

- **Validation vignette is now data-driven.** The ``validation.qmd``
  bibliography section is generated directly from the fixture
  ``[source]`` blocks; the previously hand-curated ``SOURCE_LABELS``
  dict and prose bibliography are gone. Adding a new fixture
  automatically updates both the validation table and the
  bibliography on next render.
- ``tests/schedules/README.md`` documents the new bibliographic
  fields and lists ``reference_work`` as an additional accepted
  ``kind`` value (used by the Wikipedia fixture).

## [0.5.1] - 2026-04-30

### Added

- **Read the Docs site** at <https://mortgagemath.readthedocs.io/>.
  Small Sphinx project under ``docs/sphinx/`` (Furo theme + MyST
  parser + autodoc) covering installation, quickstart, full
  auto-generated API reference, vignette directory, and changelog.
  Sphinx pulls the version from package metadata, so the site
  always reports the same version as ``pip show`` and the in-Python
  ``__version__``.
- **GitHub Pages site** at <https://murraystokely.github.io/mortgagemath/>
  hosting the rendered Quarto vignettes.  Built and deployed by a
  new ``vignettes.yml`` GitHub Actions workflow that triggers on
  push to ``main`` (when ``docs/vignettes/**`` changes) and on
  ``v*`` tags (which also publish the rendered PDFs as workflow
  artifacts).
- **Pre-rendered PDF vignettes** committed to
  ``docs/vignettes/rendered/`` so anyone browsing the GitHub repo
  can click a PDF and read it without cloning or running Quarto.
- **README "Documentation" section** prominently linking the Read
  the Docs site, the GitHub Pages vignette site, and the five
  individual PDFs.
- **PyPI Project URLs** expanded: ``Documentation`` now points to
  Read the Docs (was the README anchor); new ``Vignettes`` URL
  points to GitHub Pages; new ``Changelog`` URL.

### Changed

- ``pyproject.toml`` gains a ``[project.optional-dependencies] docs``
  group with ``sphinx``, ``furo``, ``myst-parser``, and
  ``sphinx-copybutton``.  Read the Docs uses
  ``pip install .[docs]`` per ``.readthedocs.yaml``.

### Notes

- No library code changes in this release.  Test suite, coverage,
  CLI, and the v0.5.0 ARM payment-cap feature are unchanged.

## [0.5.0] - 2026-04-30

### Added

- **Payment caps with negative amortization** for ARMs.
  ``RateChange`` gains an optional ``payment_cap_factor`` field (e.g.
  ``Decimal("1.075")`` for a 7.5% annual cap).  When set on a
  recasting rate change, the new payment is bounded by
  ``min(closed_form_recast, prior_payment * cap_factor)``.  If the
  cap binds and the per-period interest exceeds the capped payment,
  the unpaid interest is capitalized into the balance — the
  corresponding ``Installment.principal`` is negative and the balance
  grows.  The per-row invariant
  ``principal + interest == payment`` continues to hold.
- **ProEducate ARM payment-cap fixture.**  $65,000 / Year 1 at 10% /
  Year 2 at 12% / 30yr / 7.5% annual payment cap.  Validates 7
  cents-level anchors: year-1 P&I $570.42, balance after pmt 12
  $64,638.72, year-2 capped P&I $613.20, month-13 interest $646.39
  with -$33.19 principal (neg-am), cumulative neg-am $420.90 over
  year 2, balance after pmt 24 $65,059.62, year-2 uncapped recast
  for reference $667.30.  See
  ``tests/schedules/proeducate_arm_pmt_cap_65k_10pct_to_12pct_360mo.{toml,csv}``.
- **CLI cap-suffix syntax.**  ``--rate-change`` accepts
  ``EFFECTIVE_PMT:NEW_RATE:cap=FACTOR``, repeatable suffixes parsed
  in any order alongside the existing ``:no_recast`` flag.
- 6 new structural / invariant tests for cap mechanics in both
  balance-tracking modes (cap binds vs doesn't bind, neg-am
  invariant, regression check that cap=None is byte-identical to
  v0.4 recast).
- **Quarto vignette documentation set** in
  ``docs/vignettes/``.  Five vignettes branded with the MortgageMath
  logo, rendered to both HTML (Quarto's website format) and PDF
  (typst engine, deterministic builds, no LaTeX dependency).
  - *At a glance* — single-page overview with install/use, worked
    example, and the full Required + Optional parameter list.
  - *Validation against published sources* — 27-fixture table with
    the six parameter columns (Day / Bal / Rnd / Cmp / Freq / ARM)
    showing the exact ``LoanParams`` settings required to match
    each source, plus a curated bibliography keyed by source.  The
    table is generated dynamically from
    ``tests/schedules/*.toml`` so it stays current as fixtures are
    added.
  - *Reg Z Sample H-14: an ARM walkthrough* — cap derivation table,
    encoded ``LoanParams``, and live anchor verification of all 11
    published anchors against the regulatory worked example.
  - *Payment caps and negative amortization* — ProEducate worked
    example with a row-by-row trace of the rate-change boundary
    (months 10–25) showing where the cap binds and where the
    schedule enters negative amortization.
  - *Canadian semi-annual mortgages* — *Interest Act* §6 convention
    with worked Olivier (Chans, monthly) and eCampus (§4.4.1,
    quarterly) reproductions.

### Validation

- Validation rejects ``payment_cap_factor <= 0`` and the
  combination ``payment_cap_factor`` + ``recast=False`` (cap is only
  meaningful when recasting).
- Empty ``rate_schedule`` and rate changes without
  ``payment_cap_factor`` are byte-identical to v0.4.0 (regression-
  tested; every existing fixture passes unchanged).

### Notes

- **Goldstein 12e §10.4 Example 14** (the textbook canonical 5/1
  ARM with payment cap and neg-am at year 7) was the algorithmic
  motivator for the API but is **not committed as a fixture**.
  Goldstein computes year-6 balances via the textbook closed-form
  outstanding-balance formula at the rounded year-1 payment, which
  diverges 13–26¢ from the library's row-by-row schedule (same
  algorithmic mismatch documented in v0.4.0 for Goldstein Ex 13).
  The 1¢ propagation breaks the year-7 cap calculation.  ProEducate
  is the cents-level published-source fixture.
- See ``docs/v0.5-plan.md`` for the v0.5 design and a deferred-work
  list (Canadian biweekly fixtures, UK / AU fixtures, Quarto
  vignette docs, Reg Z Appendix J APR validator, GPM).

## [0.4.0] - 2026-04-30

### Added

- **Adjustable-rate mortgages (Tier 1).**  New ``RateChange``
  dataclass and ``LoanParams.rate_schedule`` field
  (``tuple[RateChange, ...]``) allow rate changes at specified payment
  numbers.  Each ``RateChange`` declares an ``effective_payment_number``
  (1-indexed), a ``new_annual_rate``, and an optional ``recast`` flag
  (default True — recompute the level payment over remaining payments
  at the new rate).  Empty ``rate_schedule`` is the v0.3.0 fast path
  with byte-identical output; every existing fixture still passes.
- **Validation.**  ``RateChange.__post_init__`` rejects
  ``effective_payment_number < 2`` and non-positive rates.
  ``LoanParams.__post_init__`` rejects non-strictly-increasing
  schedules, entries past the loan's total payments, ARM + ACTUAL_360
  (day-counted accrual semantics undefined under non-monthly
  cadences), and ARM + balloon (``amortization_period_months !=
  term_months``) — both deferred until a fixture motivates them.
- **First-class CLI.**  Three subcommands: ``mortgagemath selfcheck``
  (the existing post-install validation), ``mortgagemath payment``
  (print the periodic P&I), and ``mortgagemath schedule`` (full
  schedule with ``--format table|csv|json``).  Console-script entry
  point ``mortgagemath = "mortgagemath.__main__:main"`` registered in
  ``pyproject.toml``; ``python -m mortgagemath`` continues to work.
  No-args invocation defaults to selfcheck (preserves v0.2.x
  behavior).  ARMs supported in the CLI via repeatable
  ``--rate-change EFFECTIVE_PMT:NEW_RATE[:no_recast]``.  Stdlib only —
  no new runtime dependencies.
- **24 new structural / invariant tests** for ARMs covering both
  balance-tracking modes, recast and no-recast, multi-rate schedules,
  and the empty-schedule fast path.
- **17 new CLI tests** covering all three subcommands, all three
  output formats, ARMs via flag, the no-args default routing to
  selfcheck, and standard argparse error handling.

### Validated against

- **Reg Z, 12 CFR Part 1026, Appendix H, Sample H-14** —
  $10,000 / 30yr 1/1 ARM at 1-year CMT + 3pp margin, 2pp annual cap,
  5pp symmetric lifetime cap. Initial rate 17.41% (1982 origination).
  The fixture validates 11 schedule rows spanning the regulation's
  full 15-year published trajectory, including the periodic cap
  binding at years 2 and 4 (1983 / 1985), the lifetime cap binding
  from year 5 onward (1986–1996), and the year-15 terminal balance
  $8,700.37.  Every published value reproduces exactly under
  ``BalanceTracking.ROUND_EACH`` + ``ROUND_HALF_UP``.  See
  ``tests/schedules/regz_apph_h14_arm_10k_1741_360mo.{toml,csv}``.

### Notes

- **Cap-application math.**  The Reg Z H-14 fixture encodes
  post-cap rates explicitly in its ``[[loan.rate_schedule]]``
  entries; the cap-derivation table (year-by-year application of
  periodic + lifetime caps to the index + margin) is documented in
  the fixture's TOML ``notes`` field.  A library-side
  ``IndexedRateSchedule`` API that derives post-cap rates from raw
  index history was considered ("Tier 2" in ``docs/v0.4-plan.md``)
  but deferred — only one published source motivates it today,
  falling below the project's complexity-threshold rule.  When a
  second source surfaces, that helper becomes justified.
- **Goldstein §10.4 Example 13 5/1 ARM not committed.**  Goldstein
  publishes balances computed via the textbook closed-form
  outstanding-balance formula
  ``pmt × (1 - (1+r)^-(n-k))/r`` using the rounded payment
  $1,160.80, which differs from the library's row-by-row schedule
  by 13–26¢ at month 60 ($185,405.12 published vs $185,405.25
  carry-precision / $185,405.38 round-each).  This is an algorithmic
  difference, not a library bug — Goldstein computes balances at
  conceptual checkpoints, while the library produces actual
  amortization rows.  Per the no-partial-fixtures rule, the
  Goldstein fixture is not committed.
- ``tests/test_selfcheck.py`` was retired in favor of consolidated
  coverage in the new ``tests/test_cli.py``.

## [0.3.0] - 2026-04-29

### Added

- **Non-monthly compounding.**  New ``Compounding`` enum with
  ``MONTHLY`` (default; unchanged US convention), ``SEMI_ANNUAL`` (the
  Canadian *Interest Act* §6 convention — quoted ``j_2`` rate is per
  year compounded semi-annually), and ``ANNUAL``.  Adds the
  ``compounding`` field to ``LoanParams``.
- **Non-monthly payment cadence.**  New ``PaymentFrequency`` enum
  covering ``MONTHLY``, ``SEMI_MONTHLY``, ``BIWEEKLY``, ``WEEKLY``,
  ``QUARTERLY``, and ``ANNUAL``.  Adds the ``payment_frequency``
  field to ``LoanParams`` and a ``payments_per_year`` property to
  ``PaymentFrequency``.  ``term_months × payments_per_year`` must be
  divisible by 12; validated at construction.
- **``periodic_payment(loan)``** — replaces ``monthly_payment(loan)``
  as the canonical name now that non-monthly cadences are
  supported.  ``monthly_payment`` is preserved as a permanent alias
  (``monthly_payment is periodic_payment`` evaluates True); existing
  imports keep working with no deprecation.
- 4 new test fixtures from Canadian textbook sources, all reproducing
  every published value to the cent under
  ``Compounding.SEMI_ANNUAL``:
    - **Olivier *Business Math* §13.4 — Chans first term**:
      $350,100 / j_2 = 4.9% / 3-yr term, 20-yr amort, monthly →
      $2,281.73 + balloon $316,593.49.
    - **Olivier — Chans renewal**: $316,593.49 / j_2 = 5.85% / 17yr
      → $2,440.73.
    - **eCampus Ontario *Mathematics of Finance* §4.4.1 — first
      term**: $297,500 / j_2 = 3.8% / 3-yr term, 20-yr amort,
      **quarterly** → $5,317.62 + balloon $265,830.61.
    - **eCampus §4.4.1 — renewal**: $265,830.61 / j_2 = 2.5% / 17yr,
      quarterly → $4,807.70.
- Fixture TOML schema additions: ``[loan.compounding]``,
  ``[loan.payment_frequency]``, and ``[expected.periodic_payment]``
  (alias for ``[expected.monthly_payment]``).  All optional and
  backward compatible.
- ``docs/v0.3-design.md`` documents the v0.3 (international fixed-
  rate) and v0.4+ (ARM, Australian, UK reversion) design decisions
  and rejected sources.

### Changed

- Schedule generation generalizes from "monthly rate × term in months"
  to "periodic rate × total payments."  Default-construction (monthly
  + monthly) is still a fast-path with byte-identical numerical output
  to v0.2.x — every existing fixture passes unchanged.

### Notes

- ``DayCount.ACTUAL_360`` requires both ``Compounding.MONTHLY`` and
  ``PaymentFrequency.MONTHLY``; day-counted accrual is not
  well-defined for non-monthly cadences and the §1103 / §1104 / §1106
  worked examples we validate against are all monthly + monthly.
  Validated at ``LoanParams`` construction.
- Sources investigated but **not** committed as fixtures (per the
  no-partial-fixtures rule): FCAC Government of Canada calculator
  (publishes a "total interest" computed as
  ``unrounded_payment × n − P``, not from the schedule); AIB(NI)
  Self-Build representative example (publishes "total payable"
  computed as ``rounded_payment × n + fees``, again not from the
  schedule).  Republic of Ireland and Australian sources also
  investigated; details in ``docs/v0.3-design.md``.

## [0.2.2] - 2026-04-29

### Added

- `python -m mortgagemath` runs a built-in post-install self-check
  that recomputes a small set of well-known reference values (CFPB
  H-25(B), Goldstein §10.3 Example 1 carry-precision schedule, and
  Fannie Mae §1103 monthly P&I + balloon at term) and reports
  pass/fail. Exits 0 on success, 1 on any mismatch — useful for
  verifying that a freshly-installed wheel matches the same numbers
  the test suite validates, without needing to clone the repo.

### Fixed

- `mortgagemath.__version__` is now sourced from
  `importlib.metadata.version("mortgagemath")` instead of a hard-coded
  string. The previous literal had drifted (still reported `"0.1.1"`
  in the 0.2.0 and 0.2.1 wheels even though `pip show` correctly
  reported the published version). The in-Python `__version__` now
  always matches the installed package metadata.

## [0.2.1] - 2026-04-29

### Changed

- PyPI Trove classifier promoted from `Development Status :: 4 - Beta`
  to `Development Status :: 5 - Production/Stable`. The library has
  been validated against every published source it ships fixtures for
  (CFPB H-25(B), Fannie Mae §1103, Geltner CRE textbook, Goldstein
  *Finite Mathematics*, OpenStax, Las Positas, MS State Extension, and
  synthetic boundary cases), exposes a stable public API, and is
  on-channel via PyPI and conda-forge.

## [0.2.0] - 2026-04-29

Add support for Excel-style carry-precision balance tracking and adds
more textbook examples.

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
