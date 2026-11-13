"""Bazar məlumatı mənbələri.

- yfinance: pulsuz, açar tələb etmir, gündəlik data üçün kifayətdir (default).
- Alpaca Market Data: ALPACA_API_KEY / ALPACA_SECRET_KEY təyin olunubsa istifadə olunur.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import pandas as pd

COLS = ["Open", "High", "Low", "Close", "Volume"]


def from_yfinance(ticker: str, years: int = 3) -> pd.DataFrame:
    import yfinance as yf

    df = yf.download(ticker, period=f"{years}y", interval="1d",
                     auto_adjust=True, progress=False)
    if df.empty:
        raise RuntimeError(f"{ticker}: Yahoo Finance-dən data gəlmədi")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df[COLS].dropna()


def from_alpaca(ticker: str, years: int = 3) -> pd.DataFrame:
    import requests

    headers = {
        "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY"],
        "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"],
    }
    start = (datetime.now(timezone.utc) - timedelta(days=365 * years)).strftime("%Y-%m-%d")
    url = f"https://data.alpaca.markets/v2/stocks/{ticker}/bars"
    params = {"timeframe": "1Day", "start": start, "limit": 10000,
              "adjustment": "all", "feed": "iex"}
    bars, token = [], None
    while True:
        if token:
            params["page_token"] = token
        r = requests.get(url, headers=headers, params=params, timeout=30)
        r.raise_for_status()
        j = r.json()
        bars += j.get("bars") or []
        token = j.get("next_page_token")
        if not token:
            break
    if not bars:
        raise RuntimeError(f"{ticker}: Alpaca-dan data gəlmədi")
    df = pd.DataFrame(bars).rename(columns={"o": "Open", "h": "High", "l": "Low",
                                            "c": "Close", "v": "Volume"})
    df.index = pd.to_datetime(df["t"]).dt.tz_localize(None)
    return df[COLS]


def load(ticker: str, years: int = 3, source: str = "auto") -> pd.DataFrame:
    if source == "alpaca" or (source == "auto" and os.getenv("ALPACA_API_KEY")):
        return from_alpaca(ticker, years)
    return from_yfinance(ticker, years)
