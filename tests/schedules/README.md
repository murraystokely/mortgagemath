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

## TOML schema

### `[loan]` (required)

| Field | Type | Notes |
|-------|------|-------|
| `principal`, `annual_rate` | string (Decimal) | Always quote — not a float |
| `term_months` | integer | |
| `day_count` | `"30/360"` or `"actual/360"` | |
| `payment_rounding`, `interest_rounding` | `"ROUND_UP"`, `"ROUND_HALF_UP"`, `"ROUND_HALF_EVEN"` | |
| `start_date` | `"YYYY-MM-DD"` | Required for `actual/360` (issue date / first interest-accrual period); ignored otherwise |
| `amortization_period_months` | integer | Optional. Set when `>= term_months` for balloon loans (the amortization basis the closed-form payment uses, with a balloon at term). |
| `balance_tracking` | `"round_each"` (default) or `"carry_precision"` | Round-each-balance is the US-residential-lender convention; carry-precision is Excel-default and used by graduate CRE finance textbooks. Ignored for `actual/360` (always carry-precision). |
| `compounding` | `"monthly"` (default), `"semi_annual"`, or `"annual"` | How the annual rate compounds. `"semi_annual"` is the Canadian *Interest Act* §6 convention — quoted `j_2` is per year compounded semi-annually. |
| `payment_frequency` | `"monthly"` (default), `"semi_monthly"`, `"biweekly"`, `"weekly"`, `"quarterly"`, `"annual"` | Cadence of payments. `term_months * payments_per_year` must be divisible by 12. |

### `[expected]` (required)

```toml
[expected]
periodic_payment = "141947.25"   # required (alias: monthly_payment for v0.2.x fixtures)
balloon_at_term = "20885505.83"  # optional — balance at end of loan's term
```

`periodic_payment` is the closed-form annuity payment value the library
must reproduce per period.  ``monthly_payment`` is accepted as an
alias for backward compatibility with v0.2.x fixtures and is still
preferred for monthly-cadence loans where it reads more clearly.

Optional `balloon_at_term` validates the unpaid principal at the end
of the loan's term — used for sources (e.g. Fannie Mae §1103, Canadian
fixed-term mortgages on longer amortizations) that publish a balloon
or end-of-term balance rather than per-row schedule data.

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
