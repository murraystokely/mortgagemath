# mortgagemath vignettes

Four vignettes covering the library at-a-glance, the full validated-
fixture table, country-organized worked examples (US fixed / ARMs /
commercial / synthetic, Canadian *j_2*, …), and an academic history
of the level-payment mortgage.

## Sources

- `index.qmd` — landing page (HTML only)
- `at-a-glance.qmd` — 1-page overview
- `validation.qmd` — 36-fixture parameter matrix + bibliography
- `examples.qmd` — country-organized worked examples (US, Canada,
  France, UK, Australia)
- `history.qmd` — institutional and mathematical history with
  academic bibliography

## Build

Each vignette renders to both HTML (Quarto's website format) and PDF
(typst engine, deterministic, no LaTeX dependency).

Requirements:

- [Quarto](https://quarto.org/) 1.5+
- Python 3.11+ with `mortgagemath` available (`pip install -e ../..`)
- `jupyter` (for executing the embedded Python cells)

```sh
cd docs/vignettes/
quarto render
```

Output lands in `_site/` (HTML site + side-by-side `*.pdf` files).
Both `_site/` and `_freeze/` (Quarto's execution cache) are gitignored.

## Logo

`mortgagemath.svg` is a working copy of the project logo at the repo
root.  It's included here so Quarto can find it at render time
without needing relative paths (`fig-align="center" width="35%"` in
each vignette's frontmatter).
