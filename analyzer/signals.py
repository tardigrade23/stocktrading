"""İndikatorlardan bal (score) və AL / SAXLA / SAT siqnalı çıxarır.

Bal -100..+100 aralığındadır. Hər qayda öz səbəbini yazır ki, qərarın
niyə verildiyini görəsən - "qara qutu" yoxdur.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass
class Signal:
    ticker: str
    date: str
    price: float
    score: int
    action: str
    stop_loss: float | None
    reasons: list[str] = field(default_factory=list)


def score_row(row: pd.Series, prev: pd.Series) -> tuple[int, list[str]]:
    score, why = 0, []

    def add(points: int, text: str) -> None:
        nonlocal score
        score += points
        why.append(f"{points:+d}  {text}")

    c = row["Close"]
    # 1) Trend
    if pd.notna(row["sma200"]):
        if c > row["sma200"]:
            add(20, "Qiymət SMA200-dən yuxarıdır (uzunmüddətli yüksəliş trendi)")
        else:
            add(-20, "Qiymət SMA200-dən aşağıdır (uzunmüddətli eniş trendi)")
    if pd.notna(row["sma50"]) and pd.notna(row["sma200"]):
        if row["sma50"] > row["sma200"]:
            add(15, "SMA50 > SMA200 (golden cross rejimi)")
        else:
            add(-15, "SMA50 < SMA200 (death cross rejimi)")

    # 2) MACD
    if pd.notna(row["macd_hist"]) and pd.notna(prev["macd_hist"]):
        if prev["macd_hist"] <= 0 < row["macd_hist"]:
            add(20, "MACD siqnal xəttini yuxarı kəsdi (təzə alış impulsu)")
        elif prev["macd_hist"] >= 0 > row["macd_hist"]:
            add(-20, "MACD siqnal xəttini aşağı kəsdi (təzə satış impulsu)")
        elif row["macd_hist"] > 0:
            add(10, "MACD müsbətdir")
        else:
            add(-10, "MACD mənfidir")

    # 3) RSI
    r = row["rsi14"]
    if pd.notna(r):
        if r < 30:
            add(15, f"RSI={r:.0f} - həddindən artıq satılıb (oversold)")
        elif r > 70:
            add(-15, f"RSI={r:.0f} - həddindən artıq alınıb (overbought)")
        elif 50 <= r <= 70:
            add(5, f"RSI={r:.0f} - sağlam güc zonası")

    # 4) Bollinger
    if pd.notna(row["bb_low"]):
        if c < row["bb_low"]:
            add(10, "Qiymət aşağı Bollinger zolağının altındadır")
        elif c > row["bb_up"]:
            add(-10, "Qiymət yuxarı Bollinger zolağının üstündədir")

    # 5) Momentum (3 ay)
    m = row["mom_3m"]
    if pd.notna(m):
        if m > 0.10:
            add(10, f"3 aylıq momentum güclüdür ({m:+.1%})")
        elif m < -0.10:
            add(-10, f"3 aylıq momentum zəifdir ({m:+.1%})")

    # 6) Həcm təsdiqi
    if pd.notna(row["vol_avg20"]) and row["Volume"] > 1.5 * row["vol_avg20"]:
        direction = 1 if c >= prev["Close"] else -1
        add(5 * direction, "Hərəkət yüksək həcmlə təsdiqlənir")

    return max(-100, min(100, score)), why


def action_for(score: int, buy: int = 40, sell: int = -30) -> str:
    if score >= buy:
        return "AL"
    if score <= sell:
        return "SAT"
    return "SAXLA"


def latest_signal(ticker: str, df: pd.DataFrame) -> Signal:
    row, prev = df.iloc[-1], df.iloc[-2]
    score, why = score_row(row, prev)
    stop = row["Close"] - 2 * row["atr14"] if pd.notna(row["atr14"]) else None
    return Signal(
        ticker=ticker,
        date=str(df.index[-1].date()),
        price=float(row["Close"]),
        score=score,
        action=action_for(score),
        stop_loss=float(stop) if stop is not None else None,
        reasons=why,
    )


def score_series(df: pd.DataFrame) -> pd.Series:
    """Backtest üçün hər gün üzrə bal."""
    vals = [0] + [score_row(df.iloc[i], df.iloc[i - 1])[0] for i in range(1, len(df))]
    return pd.Series(vals, index=df.index)
