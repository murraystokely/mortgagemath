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

Every fixture must declare where its numbers came from. The schema is rich
enough that the validation vignette's bibliography is generated entirely
from these blocks — no hand-curated list anywhere. Required fields:

| Field | Notes |
|-------|-------|
| `kind` | One of the values in the table below |
| `short_label` | Compact label used in the validation table (e.g. `"CFPB H-25(B)"`, `"OpenStax §6.8 car"`) |
| `bib_key` | Bibliography group key — fixtures sharing a source share a `bib_key`, and the bibliography emits one entry per key |
| `bib_title` | Bold lead-in for the bibliography entry (e.g. `"CFPB H-25(B)"`, `"Geltner Ch 20"`) |
| `citation` | Full prose citation, formatted as a single line of Markdown (authors, title, edition, publisher, year, ISBN, plus a trailing `<url>` if available). Identical across fixtures sharing a `bib_key`. |

The legacy `label` field is accepted as an alias for `short_label` during
the v0.5.x transition.

`kind` values:

| `kind` | Meaning |
|--------|---------|
| `statement` | Pulled from an actual bank/servicer statement for a real loan |
| `regulatory_example` | Worked example published by a US regulator (CFPB, Federal Reserve, VA, HUD) |
| `gse_guide` | Worked example from a GSE seller/servicer guide (Fannie Mae, Freddie Mac) |
| `textbook` | Worked example from an open-licensed or public-domain textbook |
| `calculator` | Output of a publicly available lender or third-party calculator |
| `reference_work` | Encyclopedia / reference (e.g. Wikipedia worked example) |
| `synthetic` | Constructed to exercise a specific rounding boundary; values cross-verified |

Optional structured fields (used when present, but not required — the
`citation` string is the canonical bibliographic record):

| Field | Notes |
|-------|-------|
| `country` | ISO-style country code (`"US"`, `"CA"`, etc.) |
| `license` | Free-text license summary (`"public domain"`, `"CC-BY-4.0"`, `"CC-BY-NC-SA-4.0"`) |
| `url` | Direct link to the source document |
| `notes` | Per-fixture commentary (rounding choices, divergences explained, boundary condition for `synthetic`) |

For `statement` sources include `verified_by` and `verified_date`
instead of `url`. For `synthetic`, the `notes` field is required and
must explain the boundary condition and how the expected values were
independently verified.

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
| `rate_schedule` | array of tables (optional) | ARM rate-change schedule; see below. |

#### `[[loan.rate_schedule]]` (ARMs)

Optional array-of-tables for adjustable-rate mortgages.  Each entry
declares one rate change:

```toml
[[loan.rate_schedule]]
effective_payment_number = 61   # 1-indexed; new rate applies starting at this payment
new_annual_rate = "7.2"         # Decimal string — quote like `annual_rate`
recast = true                   # optional, default true; false keeps prior level payment
payment_cap_factor = "1.075"    # optional Decimal string; bounds the recast at
                                # min(uncapped, prior_pmt × factor). Only meaningful
                                # when recast=true. When the cap binds and interest
                                # exceeds the capped payment, the unpaid interest is
                                # capitalized into the balance (negative amortization);
                                # the corresponding Installment.principal is negative.
```

Constraints (validated by ``LoanParams.__post_init__``): entries must
have ``effective_payment_number >= 2``, strictly increasing, and
``<= total_payments``.  ARM is currently restricted to
``day_count = "30/360"`` and to fully-amortizing loans
(``amortization_period_months`` either omitted or equal to
``term_months``).

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
