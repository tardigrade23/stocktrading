"""Sadə long-only backtest: bal >= buy olanda al, <= sell olanda və ya
stop-loss (2×ATR) vurulanda sat. Siqnal günün bağlanışında hesablanır,
əməliyyat növbəti günün açılışında icra olunur (look-ahead bias yoxdur)."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .signals import score_series


@dataclass
class BacktestResult:
    total_return: float
    buy_hold_return: float
    cagr: float
    max_drawdown: float
    sharpe: float
    trades: int
    win_rate: float
    equity: pd.Series


def run(df: pd.DataFrame, buy: int = 40, sell: int = -30,
        fee: float = 0.001, start_cash: float = 10_000.0) -> BacktestResult:
    scores = score_series(df)
    cash, shares, stop, entry = start_cash, 0.0, None, 0.0
    equity, wins, trades = [], 0, 0

    for i in range(len(df) - 1):
        today, nxt = df.iloc[i], df.iloc[i + 1]
        s = scores.iloc[i]
        if shares == 0 and s >= buy:
            price = nxt["Open"] * (1 + fee)
            shares, cash, entry = cash / price, 0.0, price
            stop = today["Close"] - 2 * today["atr14"] if pd.notna(today["atr14"]) else None
        elif shares > 0 and (s <= sell or (stop is not None and today["Close"] < stop)):
            price = nxt["Open"] * (1 - fee)
            cash, trades = shares * price, trades + 1
            wins += price > entry
            shares, stop = 0.0, None
        elif shares > 0 and pd.notna(today["atr14"]):
            # trailing stop: yalnız yuxarı qalxır
            stop = max(stop or 0, today["Close"] - 2 * today["atr14"])
        equity.append(cash + shares * today["Close"])

    equity.append(cash + shares * df.iloc[-1]["Close"])
    eq = pd.Series(equity, index=df.index)
    rets = eq.pct_change().dropna()
    years = max((df.index[-1] - df.index[0]).days / 365.25, 1e-9)
    total = eq.iloc[-1] / start_cash - 1
    return BacktestResult(
        total_return=total,
        buy_hold_return=df["Close"].iloc[-1] / df["Close"].iloc[0] - 1,
        cagr=(1 + total) ** (1 / years) - 1,
        max_drawdown=float((eq / eq.cummax() - 1).min()),
        sharpe=float(rets.mean() / rets.std() * np.sqrt(252)) if rets.std() > 0 else 0.0,
        trades=trades,
        win_rate=wins / trades if trades else 0.0,
        equity=eq,
    )
