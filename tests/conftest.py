"""Auto-discover paired TOML+CSV test fixtures in tests/schedules/."""

import csv
import tomllib
from pathlib import Path

import pytest

SCHEDULES_DIR = Path(__file__).parent / "schedules"


def _load_fixtures():
    """Yield (toml_data, csv_rows) for each .toml file with a matching .csv."""
    for toml_path in sorted(SCHEDULES_DIR.glob("*.toml")):
        csv_path = toml_path.with_suffix(".csv")
        if not csv_path.exists():
            continue

        with open(toml_path, "rb") as f:
            toml_data = tomllib.load(f)

        csv_rows: list[dict[str, str]] = []
        with open(csv_path, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                csv_rows.append(row)

        yield pytest.param((toml_data, csv_rows), id=toml_path.stem)


@pytest.fixture(params=list(_load_fixtures()))
def bank_schedule(request) -> tuple[dict, list[dict[str, str]]]:
    """A paired TOML metadata + CSV schedule fixture."""
    return request.param
