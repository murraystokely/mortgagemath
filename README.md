<p align="center">
  <img src="https://raw.githubusercontent.com/murraystokely/mortgagemath/main/mortgagemath.svg" alt="mortgagemath logo" width="400">
</p>

# mortgagemath

[![tests](https://github.com/murraystokely/mortgagemath/actions/workflows/tests.yml/badge.svg)](https://github.com/murraystokely/mortgagemath/actions/workflows/tests.yml)
<!-- [![lint](https://github.com/murraystokely/mortgagemath/actions/workflows/lint.yml/badge.svg)](https://github.com/murraystokely/mortgagemath/actions/workflows/lint.yml) -->
[![coverage](https://raw.githubusercontent.com/murraystokely/mortgagemath/main/coverage.svg)](https://raw.githubusercontent.com/murraystokely/mortgagemath/main/coverage.svg)
[![PyPI](https://img.shields.io/pypi/v/mortgagemath.svg)](https://pypi.org/project/mortgagemath/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/mortgagemath?period=total&units=INTERNATIONAL_SYSTEM&left_color=BLACK&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/mortgagemath)
[![Documentation](https://img.shields.io/readthedocs/mortgagemath?label=docs)](https://mortgagemath.readthedocs.io/)

**Cent-accurate mortgage amortization for Python.** Validated
against CFPB regulatory disclosures, Fannie Mae GSE servicing
guides, the Reg Z Sample H-14 ARM, the FHLBB *Federal Home Loan
Bank Review* of March 1935, and 30+ open-licensed textbook
worked examples — every published cell matches to the cent.
Decimal end-to-end; no runtime dependencies beyond the Python
standard library.

## Why mortgagemath?

Most mortgage libraries get the closed-form payment right but
diverge from real lender statements by 1–4 cents per row. The
discrepancy compounds over the schedule, breaks reconciliation
against an actual bank statement, and makes audit work painful.
`mortgagemath` is built around the rounding and accounting
conventions actual lenders use:

- **Decimal arithmetic** end-to-end (no float drift)
- **Configurable rounding** for the periodic payment and per-row
  interest (`ROUND_UP`, `ROUND_HALF_UP`, `ROUND_HALF_EVEN`)
- **Two balance-tracking modes** — `ROUND_EACH` (US lender
  statements) and `CARRY_PRECISION` (Excel / graduate CRE
  textbooks)
- **Both day-count conventions** — 30/360 (residential) and
  Actual/360 (commercial)
- **Non-monthly compounding and cadence** — Canadian *Interest
  Act* §6 (`j_2`), effective-annual, weekly through annual
- **Adjustable-rate mortgages** with rate schedules, optional
  payment caps, and capitalized negative amortization
- **Exact zero ending balance** — the final row trues up so
  the schedule lands at $0.00
- **37 cell-for-cell validated fixtures** auto-discovered by
  `pytest`

## Installation

```sh
pip install mortgagemath
```

Requires Python 3.11+. Zero runtime dependencies.

To verify a fresh install reproduces the same reference values
the test suite validates:

```sh
python -m mortgagemath
```

This recomputes a CFPB sample Closing Disclosure, the Goldstein
§10.3 Example 1 carry-precision schedule, and the Fannie Mae
§1103 Tier 2 SARM monthly payment plus balloon-at-term. Exits 0
if every value matches the published source exactly.

## Quick example

The CFPB's Closing Disclosure Sample H-25(B) — $162,000 at
3.875% for 30 years — from the command line:

```sh
mortgagemath schedule --principal 162000 --rate 3.875 --term-months 360 \
    --payment-rounding ROUND_HALF_UP --interest-rounding ROUND_HALF_UP \
    --format csv
```

The same loan from Python:

```python
from decimal import Decimal
from mortgagemath import (
    LoanParams, PaymentRounding,
    periodic_payment, amortization_schedule,
)

loan = LoanParams(
    principal=Decimal("162000.00"),
    annual_rate=Decimal("3.875"),
    term_months=360,
    payment_rounding=PaymentRounding.ROUND_HALF_UP,
    interest_rounding=PaymentRounding.ROUND_HALF_UP,
)

print(periodic_payment(loan))      # Decimal("761.78")
sched = amortization_schedule(loan)
print(sched[1].interest)            # Decimal("523.13")
print(sched[1].principal)           # Decimal("238.65")
print(sched[-1].balance)            # Decimal("0.00")  exact closure
```

For Canadian *j_2* mortgages, US ARMs (with rate caps and
payment caps), commercial Actual/360 with balloon, and the FHLBB
1935 given-payment convention, see the **[Worked
examples](docs/vignettes/rendered/examples.pdf)** vignette.

## What's validated

37 fully published amortization tables from government regulatory
documents, GSE servicing guides, and academic textbooks, exercised
by a test suite of more than 300 tests that runs on every push and
every release to ensure every cent on every row matches the
published source exactly. The sources span:

- **Regulatory disclosures** — CFPB Sample H-25(B); 12 CFR
  Part 1026 Appendix H Sample H-14 (the 1982–1996 1/1 ARM with
  periodic and lifetime caps, traced through the actual CMT
  history)
- **GSE servicing guides** — Fannie Mae Multifamily §1103 Tier 2
  SARM ($25 M / 5.5% / 10-year term on 30-year amortization,
  Actual/360)
- **Federal authorities** — FHLBB *Federal Home Loan Bank
  Review*, March 1935 — Direct-Reduction Plan A
- **Textbooks** — OpenStax *Contemporary Mathematics*, Geltner
  et al. *CRE Analysis*, Skinner *Mathematical Theory of
  Investment* (1913), Arcones SOA Exam FM Manual, Goldstein
  *Finite Mathematics*, eCampus Ontario *Mathematics of
  Finance*, Olivier *Business Math*, Las Positas *Math for
  Liberal Arts*, Mississippi State Extension Service
- **Synthetic boundary cases** for half-cent rounding modes

See the **[Validation
vignette](docs/vignettes/rendered/validation.pdf)** for the full
37-fixture × 8-parameter matrix and bibliography, generated
directly from the fixture `[source]` blocks.

## Documentation

| Resource | Audience |
|---|---|
| **[Read the Docs](https://mortgagemath.readthedocs.io/)** | Installation, quickstart, full API reference, changelog |
| **[At a glance](docs/vignettes/rendered/at-a-glance.pdf)** | 60-second orientation |
| **[Validation](docs/vignettes/rendered/validation.pdf)** | Audit / risk review — full fixture matrix + bibliography |
| **[Worked examples](docs/vignettes/rendered/examples.pdf)** | Picking the right configuration by country and loan type |
| **[History](docs/vignettes/rendered/history.pdf)** | Academic context — institutional and mathematical history of the level-payment mortgage |
| **[HTML site](https://murraystokely.github.io/mortgagemath/)** | Vignettes with navigation and search |

## Reporting a discrepancy

Found a published example or a real lender statement that
`mortgagemath` doesn't reproduce to the cent? Two paths:

- **Reporters / users** — open an issue using the [Mortgage
  example doesn't match](.github/ISSUE_TEMPLATE/mortgage-example.yml)
  template. Paste the published values; no `pytest` needed.
- **Contributors** — add a paired TOML + CSV fixture under
  `tests/schedules/`. See
  [`tests/schedules/README.md`](tests/schedules/README.md) for
  the schema and contribution workflow.

For unrelated bugs or feature requests, use the [Bug or feature
request](.github/ISSUE_TEMPLATE/bug-or-feature.yml) template.

## License

MIT
