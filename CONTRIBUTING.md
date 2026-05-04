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

### Prerequisites

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management. Install it first if you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup

```bash
git clone https://github.com/murraystokely/mortgagemath.git
cd mortgagemath
uv sync --extra dev
```

This creates a virtual environment and installs the package in editable
mode along with all dev tools (ruff, mypy, pytest, pytest-cov).

### Running checks

```bash
uv run ruff format --check src/ tests/   # formatting
uv run ruff check src/ tests/            # linting
uv run mypy                              # type checking
uv run pytest                            # tests
uv run pytest --cov=src/mortgagemath     # tests + coverage
```

Before opening a PR, run at least the four checks above — they match
what CI runs.

### Pre-commit hooks (optional)

To run these checks automatically on every commit:

```bash
uv run pre-commit install
```

Then `pre-commit run --all-files` catches formatting, whitespace,
YAML/TOML, large-file, ruff, and mypy issues in one command.

## Privacy

Fixture submissions must not contain personally identifying information
— no addresses, lender names, account numbers, or borrower names. Loan
parameters alone (principal, rate, term, schedule rows) are fine.
