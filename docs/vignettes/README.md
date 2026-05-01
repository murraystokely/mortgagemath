# mortgagemath vignettes

Five vignettes covering the library at-a-glance, the full validated-
fixture table, ARM mechanics (Reg Z H-14), payment caps with negative
amortization (ProEducate), and Canadian semi-annual mortgages.

## Sources

- `index.qmd` — landing page (HTML only)
- `at-a-glance.qmd` — 1-page overview
- `validation.qmd` — 27-fixture parameter matrix + bibliography
- `arm-regz-h14.qmd` — Reg Z Sample H-14 ARM walkthrough
- `payment-caps-proeducate.qmd` — payment cap + negative amortization
- `canadian-j2.qmd` — Canadian semi-annual (`j_2`) convention

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
