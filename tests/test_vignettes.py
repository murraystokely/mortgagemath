"""Smoke tests for executable vignette code."""

import contextlib
import io
from pathlib import Path


def _python_chunks(qmd_path: Path) -> list[str]:
    """Extract executable Python chunks from a Quarto Markdown file."""
    chunks: list[str] = []
    current: list[str] = []
    in_python_chunk = False

    for line in qmd_path.read_text().splitlines():
        if line.startswith("```{python}"):
            in_python_chunk = True
            current = []
            continue
        if in_python_chunk and line.startswith("```"):
            chunks.append("\n".join(current))
            in_python_chunk = False
            continue
        if in_python_chunk:
            current.append(line)

    return chunks


def test_validation_vignette_python_chunks_execute(monkeypatch):
    """The validation matrix must handle every fixture enum value.

    This catches missing display-map entries such as a new
    ``PaymentRounding`` value before Quarto render time.
    """
    repo_root = Path(__file__).resolve().parents[1]
    vignette_dir = repo_root / "docs" / "vignettes"
    qmd_path = vignette_dir / "validation.qmd"
    namespace: dict[str, object] = {}

    monkeypatch.chdir(vignette_dir)
    with contextlib.redirect_stdout(io.StringIO()):
        for chunk in _python_chunks(qmd_path):
            exec(compile(chunk, str(qmd_path), "exec"), namespace)

    assert namespace["fixtures"]
