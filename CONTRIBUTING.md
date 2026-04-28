# Contributing

Thanks for your interest in `mortgagemath`. The project's distinguishing
goal is **cent-accurate validation against published authoritative
sources**, so contributions that strengthen the validation suite are
especially welcome.

## Reporting issues

- **Lender / textbook / regulator example doesn't reproduce to the
  cent**: please use the
  [Mortgage example doesn't match](.github/ISSUE_TEMPLATE/mortgage-example.yml)
  issue template. It walks through the loan parameters and any per-row
  data the source publishes.
- **Bugs, feature requests, documentation, anything else**: use the
  [Bug or feature request](.github/ISSUE_TEMPLATE/bug-or-feature.yml)
  template.
- **Open-ended questions** belong in
  [Discussions](https://github.com/murraystokely/mortgagemath/discussions).

## Submitting a test fixture as a PR

If you can run `pytest` locally, the fastest path is a direct PR
adding a paired `.toml` + `.csv` fixture in `tests/schedules/`. See
[`tests/schedules/README.md`](tests/schedules/README.md) for the schema
and required `[source]` provenance fields.

The standing rule: a fixture must reproduce **every** value the source
attests to (monthly payment, every published row, every cumulative
total, balloon at term). Partial matches go in
[`docs/future-work.md`](docs/future-work.md), not in the suite.

## Local development

```
git clone https://github.com/murraystokely/mortgagemath.git
cd mortgagemath
uv run --with pytest --with-editable . pytest
```

Before opening a PR, run the same checks CI runs:

```
uv run --with 'ruff>=0.6' --with-editable . ruff check src/ tests/
uv run --with 'ruff>=0.6' --with-editable . ruff format --check src/ tests/
uv run --with 'mypy>=1.10' --with-editable . mypy
uv run --with pytest --with pytest-cov --with-editable . pytest --cov=src/mortgagemath
```

Optional: set up [pre-commit](https://pre-commit.com/) to run these on
every commit:

```
pip install pre-commit
pre-commit install
```

## Privacy

Fixture submissions must not contain personally identifying information
— no addresses, lender names, account numbers, or borrower names. Loan
parameters alone (principal, rate, term, schedule rows) are fine.
