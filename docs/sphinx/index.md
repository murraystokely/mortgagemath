# mortgagemath

Cent-accurate mortgage amortization for Python — validated against
CFPB, Fannie Mae, Reg Z, and published textbook examples.

```{toctree}
:maxdepth: 2
:caption: Getting started

installation
quickstart
```

```{toctree}
:maxdepth: 2
:caption: Reference

api
vignettes
changelog
```

## Why mortgagemath

Most Python amortization libraries float-drift by one cent or more
against published lender statements, regulatory disclosures, and
textbook worked examples. `mortgagemath`'s 36-fixture validation
suite ships paired loan-parameter and schedule files for every
loan; every committed fixture cell reproduces its source value to
the cent. Sources include:

- The **CFPB H-25(B)** sample Closing Disclosure
- **Fannie Mae §1103** Tier 2 SARM (Actual/360 with balloon)
- **Reg Z Sample H-14** 1/1 ARM with periodic and lifetime caps
- **ProEducate ARM Payment Caps** with negative amortization
- **FHLBB *Federal Home Loan Bank Review*** (March 1935)
  Direct-Reduction Plan A
- **Geltner et al.** *Commercial Real Estate Analysis* CPM
- **Goldstein** *Finite Mathematics* §10.3
- **Skinner** *Mathematical Theory of Investment* (1913)
- Canadian *Interest Act* §6 (`j_2`) mortgages from **Olivier** and
  **eCampus Ontario**

Where a published source contains an internal arithmetic typo (a
known issue in some 19th-century actuarial tables and in two rows
of the Geltner CRE example), the divergent rows are documented
rather than forced into the fixture corpus. See the
[Validation vignette](vignettes.md) for the full table.

## At a glance

```python
from decimal import Decimal
from mortgagemath import LoanParams, periodic_payment, amortization_schedule

loan = LoanParams(
    principal=Decimal("300000"),
    annual_rate=Decimal("6.5"),
    term_months=360,
)
print(periodic_payment(loan))   # Decimal("1896.21")
sched = amortization_schedule(loan)
print(sched[-1].balance)        # Decimal("0.00") — exact closure
```

A built-in CLI is also registered:

```sh
mortgagemath payment --principal 300000 --rate 6.5 --term-months 360
mortgagemath schedule --principal 300000 --rate 6.5 --term-months 360 --format csv
python -m mortgagemath           # post-install self-check
```

## Indices

- {ref}`genindex`
- {ref}`modindex`
- {ref}`search`
