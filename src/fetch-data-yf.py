# This file uses Yahoo Finance Library to fetch data for RELIANCE, TCS, etc...

import yfinance as yf
import pandas as pd
import os

def get_yf_data(symbol, out_dir="data/raw", months=12):
    """Fetch daily EOD data from Yahoo Finance (works for NSE tickers with .NS)"""
    os.makedirs(out_dir, exist_ok=True)
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{months}mo")  # last N months
    if df.empty:
        print(f"⚠️ No data for {symbol}")
        return None

    df.reset_index(inplace=True)
    df.rename(columns={
        "Date": "Date",
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Adj Close": "AdjClose",
        "Volume": "Volume"
    }, inplace=True)

    path = os.path.join(out_dir, f"{symbol}.csv")
    df.to_csv(path, index=False)
    print(f"✅ Saved {symbol}: {len(df)} rows")
    return df

if __name__ == "__main__":
    symbols = ["ICICIBANK.NS", "ITC.NS", "MARUTI.NS","TATASTEEL.NS","LT.NS"]
    for s in symbols:
        get_yf_data(s)
