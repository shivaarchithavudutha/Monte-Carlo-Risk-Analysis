import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

class MonteCarloSimulator:
    def __init__(self, ticker, horizon=252, iterations=10000):
        self.ticker = ticker
        self.horizon = horizon
        self.iterations = iterations
        self.data = self._fetch_data()

    def _fetch_data(self):
        df = yf.download(self.ticker, period="2y", auto_adjust=True, progress=False)
        return np.log(1 + df['Close'].pct_change()).dropna()

    def run_simulation(self):
        mu = self.data.mean().item() 
        var = self.data.var().item()
        sigma = self.data.std().item()

        drift = mu - (0.5 * var)
        daily_returns = np.exp(drift + sigma * np.random.standard_normal((self.horizon, self.iterations)))

        S0 = yf.download(self.ticker, period="1d", auto_adjust=True, progress=False)['Close'].iloc[-1]
        paths = np.zeros_like(daily_returns)
        paths[0] = S0

        for t in range(1, self.horizon):
            paths[t] = paths[t-1] * daily_returns[t]

        return paths

# Execution & Risk Analysis
sim = MonteCarloSimulator('JPM')
results = sim.run_simulation()
final_prices = results[-1]

# Calculation of Metrics
var_95 = np.percentile(final_prices, 5)
cvar_95 = final_prices[final_prices <= var_95].mean()

print(f"Simulation Complete for {sim.ticker}")
print("-" * 30)
print(f"Current Price:           ${results[0][0]:.2f}")
print(f"95% Value at Risk (VaR): ${var_95:.2f}")
print(f"95% Expected Shortfall:  ${cvar_95:.2f}")
print("-" * 30)

# Visualization
plt.figure(figsize=(12, 7))
plt.hist(final_prices, bins=100, color='royalblue', alpha=0.7, label='Price Distribution')
plt.axvline(var_95, color='red', linestyle='--', linewidth=2, label=f'VaR (95%): ${var_95:.2f}')
plt.axvline(cvar_95, color='darkred', linestyle='-', linewidth=2, label=f'CVaR (95%): ${cvar_95:.2f}')

plt.title(f"Monte Carlo Simulation: {sim.ticker} Future Price Distribution", fontsize=14)
plt.xlabel("Price ($)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(axis='y', alpha=0.3)
plt.show()
