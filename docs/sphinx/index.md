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
textbook worked examples. `mortgagemath` reproduces every published
value to the cent for every loan in its 27-fixture validation suite —
including:

- The **CFPB H-25(B)** sample Closing Disclosure
- **Fannie Mae §1103** Tier 2 SARM (Actual/360 with balloon)
- **Reg Z Sample H-14** 1/1 ARM with periodic and lifetime caps
- **ProEducate ARM Payment Caps** with negative amortization
- **Geltner et al.** *Commercial Real Estate Analysis* CPM
- **Goldstein** *Finite Mathematics* §10.3
- Canadian *Interest Act* §6 (`j_2`) mortgages from **Olivier** and
  **eCampus Ontario**

Every fixture reproduces every published value the source attests to;
fixtures with even a single 1-cent discrepancy are excluded.  See the
[Validation vignette](vignettes.md) for the full list.

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
