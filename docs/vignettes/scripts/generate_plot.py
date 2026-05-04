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

# Filter out the initial period 0 for some plots
df_plot = df[df["number"] > 0]

# Create figure with two subplots side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.suptitle("Amortization Analysis: $300,000 Loan, 6.5% 30-Year Fixed", fontsize=16)

# --- Plot 1: Monthly Principal vs Interest (Stacked) ---
ax1.stackplot(
    df_plot["number"],
    df_plot["principal"].astype(float),
    df_plot["interest"].astype(float),
    labels=["Principal", "Interest"],
    alpha=0.8,
    colors=["#2ca02c", "#1f77b4"],
)
ax1.set_title("Monthly Payment Composition", fontsize=12)
ax1.set_xlabel("Payment Number")
ax1.set_ylabel("Payment Amount ($)")
ax1.set_xlim(1, df_plot["number"].max())
ax1.margins(x=0, y=0)
ax1.legend(loc="upper right")
ax1.grid(True, linestyle="--", alpha=0.6)

# --- Plot 2: Balance vs Cumulative Interest ---
color_bal = "tab:green"
ax2.set_title("Balance and Cumulative Interest", fontsize=12)
ax2.set_xlabel("Payment Number")
ax2.set_ylabel("Principal Balance ($)", color=color_bal)
ax2.plot(df["number"], df["balance"].astype(float), color=color_bal, linewidth=2, label="Balance")
ax2.tick_params(axis="y", labelcolor=color_bal)

# Create a second y-axis for cumulative interest
ax2_twin = ax2.twinx()
color_int = "tab:blue"
ax2_twin.set_ylabel("Cumulative Interest ($)", color=color_int)
ax2_twin.plot(
    df["number"], df["total_interest"].astype(float), color=color_int, linewidth=2, label="Interest"
)
ax2_twin.tick_params(axis="y", labelcolor=color_int)

ax2.set_xlim(0, df["number"].max())
ax2.grid(True, linestyle="--", alpha=0.6)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig("pandas_plot.png", dpi=150)
print("Saved pandas_plot.png")
