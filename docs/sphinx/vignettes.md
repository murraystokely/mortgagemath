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

## The five vignettes

### At a glance

A 1-page overview: install + use, a worked 30-year fixed-rate
example, and the full Required + Optional `LoanParams` parameter
list.

- HTML: <https://murraystokely.github.io/mortgagemath/at-a-glance.html>
- PDF: [`at-a-glance.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/at-a-glance.pdf)

### Validation against published sources

The full **27-fixture × 6-parameter table** showing the exact
`LoanParams` settings required to match each published source, plus
a curated bibliography keyed by source.  Generated dynamically from
the test fixture TOML files so it stays current as fixtures land.

- HTML: <https://murraystokely.github.io/mortgagemath/validation.html>
- PDF: [`validation.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/validation.pdf)

### Reg Z Sample H-14: an ARM walkthrough

The regulatory worked example for a 1/1 Adjustable-Rate Mortgage
with periodic and lifetime caps.  Cap derivation table, encoded
`LoanParams`, and live anchor verification of all 11 published
checkpoints.

- HTML: <https://murraystokely.github.io/mortgagemath/arm-regz-h14.html>
- PDF: [`arm-regz-h14.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/arm-regz-h14.pdf)

### Payment caps and negative amortization

The ProEducate worked example with a row-by-row trace of the
rate-change boundary (months 10–25) showing where the cap binds and
the schedule enters negative amortization.

- HTML: <https://murraystokely.github.io/mortgagemath/payment-caps-proeducate.html>
- PDF: [`payment-caps-proeducate.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/payment-caps-proeducate.pdf)

### Canadian semi-annual mortgages

The *Interest Act* §6 convention with worked Olivier (Chans) and
eCampus Ontario (§4.4.1) reproductions; math display of the j_2 →
periodic-rate derivation.

- HTML: <https://murraystokely.github.io/mortgagemath/canadian-j2.html>
- PDF: [`canadian-j2.pdf`](https://github.com/murraystokely/mortgagemath/blob/main/docs/vignettes/rendered/canadian-j2.pdf)
