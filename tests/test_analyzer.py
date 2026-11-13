import numpy as np
import pandas as pd

from analyzer import backtest, indicators, signals


def synthetic(n=600, drift=0.0005, seed=1):
    rng = np.random.default_rng(seed)
    close = 100 * np.exp(np.cumsum(rng.normal(drift, 0.015, n)))
    idx = pd.bdate_range("2022-01-03", periods=n)
    open_ = close * (1 + rng.normal(0, 0.003, n))
    return pd.DataFrame({
        "Open": open_,
        "High": np.maximum(open_, close) * 1.005,
        "Low": np.minimum(open_, close) * 0.995,
        "Close": close,
        "Volume": rng.integers(1_000_000, 3_000_000, n),
    }, index=idx)


def test_rsi_bounds():
    r = indicators.rsi(synthetic()["Close"]).dropna()
    assert ((r >= 0) & (r <= 100)).all()


def test_signal_uptrend_vs_downtrend():
    up = signals.latest_signal("UP", indicators.add_all(synthetic(drift=0.003)))
    down = signals.latest_signal("DN", indicators.add_all(synthetic(drift=-0.003)))
    assert up.score > down.score
    assert up.action in {"AL", "SAXLA"} and down.action in {"SAT", "SAXLA"}


def test_backtest_runs():
    r = backtest.run(indicators.add_all(synthetic()))
    assert len(r.equity) == 600
    assert -1 < r.max_drawdown <= 0
