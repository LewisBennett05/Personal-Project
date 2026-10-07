# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

btc = yf.download("BTC-USD", start="2015-01-01", end="2026-09-20")
sp500 = yf.download("^GSPC", start="2015-01-01", end="2026-09-20")
gold = yf.download("GC=F", start="2015-01-01", end="2026-09-20")

print(btc.shape, sp500.shape, gold.shape)
print(btc.head())

print("BTC date range:", btc.index.min(), "to", btc.index.max())
print("S&P500 date range:", sp500.index.min(), "to", sp500.index.max())
print("Gold date range:", gold.index.min(), "to", gold.index.max())

btc_close = btc['Close'].squeeze()
sp500_close = sp500['Close'].squeeze()
gold_close = gold['Close'].squeeze()

combined = pd.DataFrame({
    'BTC': btc_close,
    'SP500': sp500_close,
    'Gold': gold_close
}).dropna()

print(combined.shape)
print(combined.head())

returns = combined.pct_change().dropna()
print(returns.head())
print(returns.describe())

fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

axes[0].plot(combined.index, combined['BTC'], color='orange')
axes[0].set_title('Bitcoin Price (USD)')

axes[1].plot(combined.index, combined['SP500'], color='blue')
axes[1].set_title('S&P 500')

axes[2].plot(combined.index, combined['Gold'], color='goldenrod')
axes[2].set_title('Gold Price (USD)')

plt.tight_layout()
plt.show()


fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)

axes[0].plot(returns.index, returns['BTC'], color='orange', linewidth=0.5)
axes[0].set_title('Bitcoin Daily Returns')

axes[1].plot(returns.index, returns['SP500'], color='blue', linewidth=0.5)
axes[1].set_title('S&P 500 Daily Returns')

axes[2].plot(returns.index, returns['Gold'], color='goldenrod', linewidth=0.5)
axes[2].set_title('Gold Daily Returns')

plt.tight_layout()
plt.show()

correlation_matrix = returns.corr()
print(correlation_matrix)

unemployment = pd.read_csv("UNRATE.csv")
print(unemployment.head())
print(unemployment.columns)

unemployment['observation_date'] = pd.to_datetime(unemployment['observation_date'])
unemployment = unemployment.set_index('observation_date')

unemployment_daily = unemployment['UNRATE'].reindex(returns.index, method='ffill')

gpr = pd.read_excel("data_gpr_export.xls")
print(gpr.head())
print(gpr.columns)

gpr['month'] = pd.to_datetime(gpr['month'])
gpr = gpr.set_index('month')

gpr_daily = gpr['GPR'].reindex(returns.index, method='ffill')

print(unemployment_daily.head())
print(unemployment_daily.isna().sum())
print(gpr_daily.head())
print(gpr_daily.isna().sum())


master = returns.copy()
master['Unemployment'] = unemployment_daily
master['GPR'] = gpr_daily
master = master.dropna()

print(master.shape)
print(master.head())

median_unemployment = master['Unemployment'].median()
print("Median unemployment:", median_unemployment)

high_unemployment = master[master['Unemployment'] > median_unemployment]
low_unemployment = master[master['Unemployment'] <= median_unemployment]

print("\nCorrelation matrix - HIGH unemployment periods:")
print(high_unemployment[['BTC', 'SP500', 'Gold']].corr())

print("\nCorrelation matrix - LOW unemployment periods:")
print(low_unemployment[['BTC', 'SP500', 'Gold']].corr())

median_gpr = master['GPR'].median()
print("Median GPR:", median_gpr)

high_gpr = master[master['GPR'] > median_gpr]
low_gpr = master[master['GPR'] <= median_gpr]

print("\nCorrelation matrix - HIGH geopolitical risk periods:")
print(high_gpr[['BTC', 'SP500', 'Gold']].corr())

print("\nCorrelation matrix - LOW geopolitical risk periods:")
print(low_gpr[['BTC', 'SP500', 'Gold']].corr())


X = master[['SP500', 'Gold', 'Unemployment', 'GPR']]
X = sm.add_constant(X)
y = master['BTC']

model = sm.OLS(y, X).fit()
print(model.summary())

print(master[['SP500', 'Gold', 'Unemployment', 'GPR']].corr())
from statsmodels.stats.outliers_influence import variance_inflation_factor

X_vif = master[['SP500', 'Gold', 'Unemployment', 'GPR']]
vif_data = pd.DataFrame()
vif_data['Variable'] = X_vif.columns
vif_data['VIF'] = [variance_inflation_factor(X_vif.values, i) for i in range(X_vif.shape[1])]
print(vif_data)

plt.figure(figsize=(8, 6))
sns.heatmap(returns.corr(), annot=True, cmap='coolwarm', center=0, fmt='.3f')
plt.title('Correlation Matrix: BTC, S&P 500, Gold (Daily Returns)')
plt.tight_layout()
plt.show()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

sns.heatmap(high_gpr[['BTC', 'SP500', 'Gold']].corr(), annot=True, cmap='coolwarm', center=0, fmt='.3f', ax=axes[0])
axes[0].set_title('High Geopolitical Risk Periods')

sns.heatmap(low_gpr[['BTC', 'SP500', 'Gold']].corr(), annot=True, cmap='coolwarm', center=0, fmt='.3f', ax=axes[1])
axes[1].set_title('Low Geopolitical Risk Periods')

plt.tight_layout()
plt.show()