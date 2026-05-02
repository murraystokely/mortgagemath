# Installation

`mortgagemath` is a pure-Python package distributed on PyPI and
conda-forge.  Requires Python 3.11 or later.  Zero runtime
dependencies — only the standard library (`decimal`, `dataclasses`,
`enum`).

## From PyPI

```sh
pip install mortgagemath
```

## From conda-forge

```sh
conda install -c conda-forge mortgagemath
```

## From source

```sh
git clone https://github.com/murraystokely/mortgagemath
cd mortgagemath
pip install -e .
```

## Verify the install

The package ships with a built-in self-check that recomputes a small
set of well-known reference values and reports pass/fail:

```sh
python -m mortgagemath
```

Sample output:

```
mortgagemath 0.6.0 self-check

  [OK  ] CFPB H-25(B) $162,000 / 3.875% / 30yr monthly P&I: got 761.78  expected 761.78
  [OK  ] Goldstein §10.3 Ex 1 $563 / 12% / 5mo monthly P&I: got 116.00  expected 116.00
  ...
  [OK  ] Fannie Mae §1103 Tier 2 SARM monthly P&I: got 141947.25  expected 141947.25
  [OK  ] Fannie Mae §1103 balloon at term-120: got 20885505.83  expected 20885505.83

All checks passed.
```

This is a real cents-level validation against the published sources
the test suite uses — useful for confirming a fresh install on a new
host matches the upstream reference values.

## Console script

Installing the package also registers a `mortgagemath` console
script.  Both forms work:

```sh
mortgagemath payment --principal 131250 --rate 4.25 --term-months 360
python -m mortgagemath schedule --principal 131250 --rate 4.25 --term-months 360
```

See {doc}`quickstart` for usage examples.
