# Test Schedules

This directory contains verified mortgage amortization data used to validate
the `mortgagemath` library against real bank statements.

## File Format

Each loan has two files with matching names:

- **`<name>.toml`** — loan parameters and metadata (principal, rate, term,
  rounding conventions, provenance)
- **`<name>.csv`** — full or partial amortization schedule with columns:
  `payment,payment_amount,principal,interest,balance`

## Contributing

To add a new verified loan:

1. Create a `.toml` file with the loan parameters. See existing files for
   the format. **Do not include property addresses, lender names, or other
   PII.** Use opaque labels.
2. Create a matching `.csv` file with at least the payments you have verified
   against bank statements. Partial schedules are fine — only include rows
   you can confirm.
3. Include the `[source]` section with your name, date, and country/state.
4. Run `pytest` to verify the schedule matches the library's computation.
