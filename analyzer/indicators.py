"""Texniki indikatorlar (pandas ilə, xarici TA kitabxanası tələb etmir)."""
from __future__ import annotations

import pandas as pd


def sma(s: pd.Series, n: int) -> pd.Series:
    return s.rolling(n, min_periods=n).mean()


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = gain / loss
    out = 100 - 100 / (1 + rs)
    return out.where(loss != 0, 100.0)


def macd(close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    line = ema(close, fast) - ema(close, slow)
    sig = line.ewm(span=signal, adjust=False).mean()
    return pd.DataFrame({"macd": line, "macd_signal": sig, "macd_hist": line - sig})


def bollinger(close: pd.Series, n: int = 20, k: float = 2.0) -> pd.DataFrame:
    mid = sma(close, n)
    std = close.rolling(n, min_periods=n).std()
    return pd.DataFrame({"bb_mid": mid, "bb_up": mid + k * std, "bb_low": mid - k * std})


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    prev = df["Close"].shift()
    tr = pd.concat(
        [df["High"] - df["Low"], (df["High"] - prev).abs(), (df["Low"] - prev).abs()], axis=1
    ).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def add_all(df: pd.DataFrame) -> pd.DataFrame:
    """OHLCV DataFrame-ə bütün indikatorları əlavə edir."""
    out = df.copy()
    c = out["Close"]
    out["sma50"] = sma(c, 50)
    out["sma200"] = sma(c, 200)
    out["rsi14"] = rsi(c)
    out = out.join(macd(c)).join(bollinger(c))
    out["atr14"] = atr(out)
    out["vol_avg20"] = out["Volume"].rolling(20).mean()
    out["mom_3m"] = c.pct_change(63)
    return out
