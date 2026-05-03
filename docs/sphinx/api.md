# API reference

The explicit listings below cover every public function, dataclass,
enum, and warning. ``conf.py`` enables
``autodoc_default_options = {"members": True}``, so each
``autoclass`` directive auto-includes its members; we omit a
top-level ``automodule`` directive to avoid duplicate index
entries.

## Functions

### Convenience constructors

These helpers choose common, fixture-backed defaults and return
ordinary validated `LoanParams` objects. Use `LoanParams` directly
when you need every parameter explicitly.

```{eval-rst}
.. autofunction:: mortgagemath.fixed_rate_mortgage
.. autofunction:: mortgagemath.us_30_year_fixed
.. autofunction:: mortgagemath.us_15_year_fixed
.. autofunction:: mortgagemath.canada_fixed_j2
.. autofunction:: mortgagemath.us_actual_360_commercial
.. autofunction:: mortgagemath.fixed_payment_mortgage
```

### Calculations

```{eval-rst}
.. autofunction:: mortgagemath.periodic_payment
.. autofunction:: mortgagemath.monthly_payment
.. autofunction:: mortgagemath.amortization_schedule
```

## Dataclasses

```{eval-rst}
.. autoclass:: mortgagemath.LoanParams
   :members:
   :show-inheritance:

.. autoclass:: mortgagemath.RateChange
   :members:
   :show-inheritance:

.. autoclass:: mortgagemath.Installment
   :members:
   :show-inheritance:
```

## Enums

```{eval-rst}
.. autoclass:: mortgagemath.DayCount
   :members:

.. autoclass:: mortgagemath.PaymentRounding
   :members:

.. autoclass:: mortgagemath.BalanceTracking
   :members:

.. autoclass:: mortgagemath.Compounding
   :members:

.. autoclass:: mortgagemath.PaymentFrequency
   :members:
```

## Warnings

```{eval-rst}
.. autoclass:: mortgagemath.EarlyPayoffWarning
   :show-inheritance:
```
