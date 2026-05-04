"""Generate a sample amortization plot for the README using pandas and matplotlib."""

from dataclasses import asdict

import matplotlib.pyplot as plt
import pandas as pd

from mortgagemath import amortization_schedule, us_30_year_fixed

# 1. Create a schedule
loan = us_30_year_fixed("300000", "6.5")
schedule = amortization_schedule(loan)

# 2. Convert to DataFrame
df = pd.DataFrame([asdict(row) for row in schedule])

# Filter out the initial period 0
df_plot = df[df["number"] > 0]

fig, ax = plt.subplots(figsize=(8, 5))

# Plot principal and interest stacked
ax.stackplot(
    df_plot["number"],
    df_plot["principal"].astype(float),
    df_plot["interest"].astype(float),
    labels=["Principal", "Interest"],
    alpha=0.8,
    colors=["#2ca02c", "#1f77b4"],
)

ax.set_title("Amortization Schedule: Principal vs Interest Over Time", fontsize=14)
ax.set_xlabel("Payment Number")
ax.set_ylabel("Monthly Payment Amount ($)")
ax.set_xlim(1, df_plot["number"].max())
ax.margins(x=0, y=0)
ax.legend(loc="upper right")

plt.tight_layout()
plt.savefig("pandas_plot.png", dpi=150)
print("Saved pandas_plot.png")
