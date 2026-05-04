# CLAUDE.md — project rules and active context

This file documents project-specific rules and active work-in-progress
that I (any future Claude session) need to know before changing the
library or shipping a release.

## Hard rules

### 1. Strict complexity-threshold

**Do not add a new library mode, option, parameter, enum value, or
configuration knob unless it unlocks matching a specific, verifiable,
public-domain or open-licensed published example cell-for-cell.**

This rule is non-negotiable. It is the reason this library has a
defensible 36-fixture test suite that audits cleanly against external
sources, rather than a sprawling option matrix that produces internally
consistent but arbitrary outputs.

What counts as a verifiable published example:

- A published source (regulator, GSE, textbook, ACTEX manual, OER,
  bank disclosure) showing principal, rate, term, and either a
  periodic payment value (single-anchor) or a row-by-row schedule
  (full match). Cents precision, not mill / three-decimal-cents.
- Either public-domain (pre-1929 in the U.S., government documents)
  or open-licensed (CC-BY, CC-BY-NC-SA, CC-BY-SA). Closed-copyright
  textbooks are acceptable for the *numerical values themselves*
  (those are uncopyrightable facts) provided we cite the source URL
  and don't transcribe prose.
- The library's existing or proposed parameter combination produces
  every published value to the cent. Single-anchor fixtures
  (only the periodic payment is published) trivially match the row
  test; full-schedule fixtures must match every printed cell.

What does NOT count:

- Marketing webpages publishing only year-level aggregates without
  documented rounding conventions.
- Sources that publish to mill precision (Hart 1924, Hardy 1909) —
  the library is cents-only.
- Sources that produce internally inconsistent column totals (some
  pre-1929 actuarial textbooks; bank pages where 12 × rounded
  payment ≠ published year total).
- Synthetic constructions designed to motivate a feature.

### 2. No synthetic-fixture-only features

**A new library mode/option must NOT be justified by a synthetic
fixture alone.** Synthetic fixtures (the
``synthetic_halfcent_*`` series) are legitimate when they validate a
specific edge case in the library's *existing* arithmetic — for
example, the half-cent interest boundary that distinguishes
``ROUND_HALF_UP`` from ``ROUND_HALF_EVEN``. They are not legitimate
as the sole justification for a new feature.

If we cannot find a real published example that the proposed feature
would unlock, we do not ship the feature. We keep it on an
unversioned WIP branch (see §"Branch naming" below) and resume when
a real source surfaces.

This rule was learned the hard way during the v0.6.1 cycle: the
``LoanParams.fee_per_period`` feature was implemented and committed
to a ``v0.6.1-fee-per-period`` branch, but no row-level Crédit
Foncier or modern French *offre de prêt* could be retrieved from
public-domain or open-licensed sources, so the feature was anchored
to a synthetic fixture only. PR #25 was closed without merging; the
branch was renamed ``fee-per-period-wip``.

### 3. No-partial-fixtures

A fixture must reproduce **every** published numerical value from
its source, or be removed entirely. If a published schedule shows 5
rows and the library matches 4 of 5, the fixture does not ship.
Single-anchor fixtures (only the periodic payment is published) are
fine; partial-schedule fixtures are not.

## Branch naming

- ``vX.Y.Z-<feature-name>``: branches that have cleared the
  complexity-threshold rule and are intended to become the named
  release. Open a PR; merge to ``main``; tag ``vX.Y.Z`` to trigger
  the auto-release workflow.
- ``<feature-name>-wip``: unversioned WIP branches for work that has
  *not yet* cleared the rule. Push to remote so the work isn't lost,
  but do not open a PR for merge until a verifiable trigger source
  surfaces. List active WIP branches in the section below.

## Active WIP branches

### `fee-per-period-wip`

A complete implementation of ``LoanParams.fee_per_period`` and
``Installment.fee`` that adds a flat per-period loading on top of
the closed-form interest+principal payment. Models the modern French
*assurance emprunteur* convention and the 1852 Crédit Foncier
*annuité* loading shape.

**Status:** unversioned WIP. Implementation is complete and the unit
tests pass; documentation is updated end-to-end. The blocker is the
absence of a row-level published source that would let us validate
the feature against a real fee-loaded schedule cell-for-cell.

**To resume:** check out ``fee-per-period-wip``, rebase on ``main``,
delete the synthetic fixture
(``tests/schedules/synthetic_fee_loaded_240k_400_60mo_assur80.{toml,csv}``),
add a real fixture against whichever of the trigger sources below
becomes accessible, and rename the branch to ``v0.6.1-fee-per-period``
(or whatever the next version is) before opening a PR.

**Trigger sources to watch for:**

1. **Bellet, *Le guide de l'emprunteur* (1854).** Gallica:
   <https://gallica.bnf.fr/ark:/12148/bpt6k65540535>. JS-walled to
   automated fetchers; needs manual retrieval through a real browser.
   Possibly contains row-level CF schedules.
2. **Josseau, *Traité du crédit foncier* (1872), Vol. II.** Gallica:
   <https://gallica.bnf.fr/ark:/12148/bpt6k63655159>. Same JS wall.
3. **Pinschof, "The Credit Foncier System," *The Argus* (Melbourne),
   18 November 1892.** Trove:
   <https://trove.nla.gov.au/newspaper/article/8482789>. Anubis
   proof-of-work wall blocks automated fetchers.
4. **A French *offre de prêt* PDF** (the borrower-facing
   amortization-table document banks are statutorily required to
   provide). Any reproducible public example would unlock the
   feature; banks don't post these on educational webpages.
5. **U.S. Senate Document 261 (1914)** or the Metcalf/Black
   Washington-state report on European rural credits. Possibly
   reproduce CF row-level data.

## Open research priorities

The clear next step for this library is **finding more real worked
amortization examples**, not adding more library features.

The current 36-fixture suite has strong U.S. coverage (CFPB regs,
GSE servicing guides, Reg Z H-14 ARM, ProEducate payment caps,
FHLBB 1935 given-payment, Geltner CRE, multiple OpenStax problems,
Skinner 1913 piano), strong Canadian coverage (Olivier, eCampus
quarterly + monthly), and one SOA actuarial fixture (Arcones).
The clear gaps are:

- **France:** zero fixtures. Needed: a row-level published table.
  Trigger sources listed under ``fee-per-period-wip`` above.
- **United Kingdom:** zero fixtures. UK building-society
  direct-reduction loans converge with the U.S. convention from the
  1990s onward, so a U.K. fixture would mostly be mechanically a
  duplicate of an existing U.S. example. Low priority unless a
  pre-convergence pre-1990s building-society schedule surfaces.
- **Australia:** zero fixtures. Victoria's 1896 Credit Foncier Act
  established a state mortgage bank; a state-bank schedule from the
  1900s-1950s would land here, contingent on the
  ``fee_per_period`` work shipping.
- **Germany / *Pfandbrief* tradition:** zero fixtures. Conceptually
  important (the *Hypothekenbanken* model influenced both the CF
  *obligations foncières* and U.S. mortgage-backed securities), but
  no specific public worked example identified yet.
- **Pre-1968 American sources beyond FHLBB 1935.** Bodfish 1931
  *History of Building and Loan in the United States* is on
  HathiTrust but most volumes are JS-walled. A digitized B&L annual
  report from the 1880s-1920s with a worked share-accumulation OR
  direct-reduction schedule would be a major find.

Searches to repeat periodically:

- HathiTrust full-text for B&L association annual reports
- Internet Archive for actuarial textbooks not yet examined
- French academic repositories (HAL, Persée) for cited CF tables
- Trove (Australian) and Papers Past (NZ) for colonial-era schedules

## Project conventions

- Test fixtures live under ``tests/schedules/<name>.{toml,csv}``;
  ``tests/schedules/README.md`` documents the schema.
- Validation vignette is data-driven from the fixture ``[source]``
  blocks; bibliography auto-generates from per-fixture ``citation``
  fields.
- Every branch that changes public API, behavior, tests, packaging,
  documentation, workflows, fixtures, or agent guidance must update
  ``CHANGELOG.md`` in the same branch. Put unreleased work under
  ``## [Unreleased]`` using the existing Keep a Changelog headings;
  only move entries into a versioned section during release prep.
- Before opening or updating a PR, run the same local gates that
  pre-commit/CI expect for the files you touched. At minimum, run
  ``ruff format --check`` (or ``ruff format`` before committing),
  ``ruff check``, ``mypy``, and the relevant ``pytest`` target. If
  ``pre-commit`` is installed, prefer ``pre-commit run --all-files``
  because it catches formatting, whitespace, YAML/TOML, large-file,
  ruff, and mypy hooks in one command.
- CHANGELOG dates use the user's local timezone (typically
  US/Pacific). Don't anchor to nearby entries; read today's date
  from the system reminder.
- Auto-release on tag push: ``release.yml`` builds, publishes to
  PyPI, and creates the GitHub Release with notes extracted from
  ``CHANGELOG.md`` plus computed SHA-256 hashes. From v0.6.0 onward
  the only manual release step is ``git tag -a vX.Y.Z -m "..." &&
  git push origin vX.Y.Z``.
- Vignettes auto-render PDFs back to the PR branch via
  ``vignettes.yml``. Reviewers can view PDFs inline in the PR's
  Files Changed tab.
