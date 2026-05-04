# Vignettes

In addition to this Sphinx reference site, `mortgagemath` ships a set
of **branded vignette PDFs** rendered from Quarto sources under
[`docs/vignettes/`](https://github.com/murraystokely/mortgagemath/tree/main/docs/vignettes).
The vignettes are also available as a hosted HTML site at
[murraystokely.github.io/mortgagemath](https://murraystokely.github.io/mortgagemath/).

Each vignette is reproducible from source: every Python code block is
executed during render, and every published-source value reproduces
to the cent.  Built with [Quarto](https://quarto.org/) and the
[typst](https://typst.app/) PDF engine.

## The four vignettes

### At a glance

A 1-page overview: install + use, a worked 30-year fixed-rate
example, and the full Required + Optional `LoanParams` parameter
list.

- HTML: <https://murraystokely.github.io/mortgagemath/at-a-glance.html>
- PDF: [`at-a-glance.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/at-a-glance.pdf)

### Validation against published sources

The full **40-fixture × 8-parameter table** showing the exact
`LoanParams` settings required to match each published source, plus
a bibliography keyed by source.  Generated dynamically from the test
fixture TOML files so it stays current as fixtures land.

- HTML: <https://murraystokely.github.io/mortgagemath/validation.html>
- PDF: [`validation.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/validation.pdf)

### Worked examples

A country-organized walkthrough of every loan type the library
covers, with a uniform structure per example: scenario, equivalent
`mortgagemath` CLI invocation, ``LoanParams(...)`` Python literal,
live schedule produced by the library, and source citation.
Sections: United States (CFPB H-25(B), OpenStax, Fannie Mae §1103,
Reg Z H-14 ARM, ProEducate payment cap with negative amortization,
CFPB Interest-Only, Geltner CRE, half-cent synthetic boundary, 0%
synthetic boundary, Skinner 1913 effective-annual, Arcones SOA FM
annual, FHLBB 1935 given-payment), Canada (Olivier Chans monthly
*j_2*, eCampus quarterly *j_2*, RBC Accelerated Bi-Weekly), France,
UK, Australia / Nordic (Swedish Serial). First-page table of contents.

- HTML: <https://murraystokely.github.io/mortgagemath/examples.html>
- PDF: [`examples.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/examples.pdf)

### A short history of the level-payment mortgage

Academic-style treatment of the institutional and mathematical
history of the residential mortgage loan, from the medieval
*mortuum vadium* through the New Deal direct-reduction
standardization to ARMs and modern conventions.  Detailed
bibliography of primary and secondary sources (Rose & Snowden NBER
WP 18388, FHLBB *Review* March 1935, Wolowski 1852, Wright 1894,
Skinner 1913, …).

- HTML: <https://murraystokely.github.io/mortgagemath/history.html>
- PDF: [`history.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/history.pdf)
