# Test Schedules

This directory contains verified amortization fixtures used to validate the
`mortgagemath` library against published, authoritative sources (regulatory
examples, textbook worked examples, and synthetic boundary cases).

## File Format

Each loan has two files with matching names:

- **`<name>.toml`** — loan parameters and metadata (principal, rate, term,
  rounding conventions, provenance)
- **`<name>.csv`** — full or partial amortization schedule with columns:
  `payment,payment_amount,principal,interest,balance`

## `[source]` provenance

Every fixture must declare where its numbers came from. The `kind` field is
required; pick the most specific that applies:

| `kind` | Meaning |
|--------|---------|
| `statement` | Pulled from an actual bank/servicer statement for a real loan |
| `regulatory_example` | Worked example published by a US regulator (CFPB, Federal Reserve, VA, HUD) |
| `gse_guide` | Worked example from a GSE seller/servicer guide (Fannie Mae, Freddie Mac) |
| `textbook` | Worked example from an open-licensed or public-domain textbook |
| `calculator` | Output of a publicly available lender or third-party calculator |
| `synthetic` | Constructed to exercise a specific rounding boundary; values cross-verified |

For non-`statement` kinds, include a `url` field pointing to the source
document. For `synthetic`, include a `notes` field explaining the boundary
condition and how the expected values were independently verified.

## Contributing

To add a new verified loan:

1. Create a `.toml` file with the loan parameters. See existing files for
   the format. **Do not include property addresses, lender names, or other
   PII.** Use opaque labels.
2. Create a matching `.csv` file with at least the payments you have verified
   against the source. Partial schedules are fine — only include rows you can
   confirm.
3. Include the `[source]` section with `kind`, country/state, and (for
   non-statement sources) a `url`. For statement sources include
   `verified_by` and `verified_date`.
4. Run `pytest` to verify the schedule matches the library's computation.
