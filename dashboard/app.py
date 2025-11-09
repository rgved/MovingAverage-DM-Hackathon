# dashboard/app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Adaptive MA Strategy Dashboard", layout="wide")

# ---------- HEADER ----------
st.title("Adaptive Moving Average Strategy Dashboard")

st.markdown("""
Welcome to the **Dynamic + Trend + Noise Adaptive Moving Average Strategy Dashboard**!  
This interactive visualization displays results from our **adaptive algorithm** applied to NSE-listed stocks.

 **Data window:** Aug 1 – Nov 7 2025  
 **Objective:** Identify whether EMA or SMA performs better depending on volatility, trend strength, and noise.
""")

# ---------- SIDEBAR ----------
st.sidebar.header("Stock Selector")

data_dir = "data/trimmed"
symbols = sorted([f.replace(".csv", "") for f in os.listdir(data_dir) if f.endswith(".csv")])
selected_symbol = st.sidebar.selectbox("Select Stock Symbol", symbols)

# ---------- LOAD DATA ----------
file_path = f"{data_dir}/{selected_symbol}.csv"
df = pd.read_csv(file_path)

# Fix timezone issue and filter to hackathon window
df["Date"] = pd.to_datetime(df["Date"], utc=True, errors="coerce").dt.tz_convert(None)
df = df[(df["Date"] >= pd.Timestamp("2025-08-01")) & (df["Date"] <= pd.Timestamp("2025-11-07"))]
df = df.sort_values("Date")

# ---------- LOAD BACKTEST REPORT ----------
report_path = f"reports/{selected_symbol.replace('.', '_')}_dynamic_trend_noise_optimization.csv"
if not os.path.exists(report_path):
    st.error("No optimization report found. Please run your dynamic_trend_noise optimization first.")
    st.stop()

report = pd.read_csv(report_path)
best = report.iloc[0]

# ---------- STRATEGY SUMMARY ----------
st.subheader(f"Strategy Summary for {selected_symbol}")

st.markdown(f"""
| Parameter | Description |
|------------|--------------|
| **Strategy Name** | Dynamic + Trend + Noise Adaptive MA |
| **MA Type Used** | {best['MA_Type']} |
| **MA Periods** | {best['MA_Pair']} |
| **Stock Tested** | {selected_symbol} |
| **Backtest Period** | Aug 2025 – Nov 2025 |
| **Entry Criteria** | Bullish crossover (Fast MA crosses above Slow MA) |
| **Exit Criteria** | Bearish crossover / Stop-loss 3% / Take-profit 5% / Max 7 days |
""", unsafe_allow_html=True)

# ---------- PERFORMANCE METRICS ----------
st.markdown("### Performance Metrics")
cols = st.columns(5)
cols[0].metric("Total Return (%)", f"{best['Return']:.2f}")
cols[1].metric("Win Rate (%)", f"{best['WinRate']:.1f}")
cols[2].metric("Sharpe Ratio", f"{best['Sharpe']:.2f}")
cols[3].metric("Max Drawdown (%)", f"{best['MaxDD']:.2f}")
cols[4].metric("Trades", f"{int(best['Trades'])}")

# ---------- PRICE CHART ----------
st.markdown("### Price Chart with Moving Averages & Crossovers *(graphs may show approximate data or be inaccurate ; included for visual enhancement)*")

# Parse MA configuration
fast, slow = map(int, best["MA_Pair"].split("/"))
ma_type = best["MA_Type"]

# Compute moving averages
if ma_type == "EMA":
    df["MA_Fast"] = df["Close"].ewm(span=fast, adjust=False).mean()
    df["MA_Slow"] = df["Close"].ewm(span=slow, adjust=False).mean()
else:
    df["MA_Fast"] = df["Close"].rolling(window=fast).mean()
    df["MA_Slow"] = df["Close"].rolling(window=slow).mean()

# Compute crossover signals
df["Signal"] = np.where(df["MA_Fast"] > df["MA_Slow"], 1, -1)
df["Crossover"] = df["Signal"].diff()

# Plot chart
fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(df["Date"], df["Close"], label="Close Price", color="gray", alpha=0.6)
ax.plot(df["Date"], df["MA_Fast"], label=f"{ma_type} {fast}", color="green")
ax.plot(df["Date"], df["MA_Slow"], label=f"{ma_type} {slow}", color="orange")

# Mark buy/sell signals
buys = df[df["Crossover"] == 2]
sells = df[df["Crossover"] == -2]
ax.scatter(buys["Date"], buys["Close"], marker="^", color="lime", s=80, label="Buy Signal")
ax.scatter(sells["Date"], sells["Close"], marker="v", color="red", s=80, label="Sell Signal")

ax.set_title(f"{selected_symbol} — {ma_type} ({fast}/{slow}) | Period: Aug 1 – Nov 7 2025", fontsize=13)
ax.legend()
ax.grid(alpha=0.3)
st.pyplot(fig)

# ---------- MODEL INTERPRETATION ----------
st.markdown("### Model Interpretation")

vol = best['Volatility']
trend = best['TrendStrength']
noise = best.get('Noise', None)

st.markdown(f"""
- **Volatility:** {vol:.2f}%  
- **Trend Strength:** {trend:.2f}%  
""" + (f"- **Noise:** {noise:.2f}%  " if noise is not None else "")
)

if ma_type == "EMA":
    st.success("✅ EMA chosen — Market is **volatile and trending**, favoring faster response.")
else:
    st.info("ℹ️ SMA chosen — Market is **calm or choppy**, favoring smoother averaging.")

# ---------- FOOTER ----------
st.markdown("---")
st.caption("© 2025 Adaptive Finance | Built for Hackathon Challenge | Powered by Streamlit")


