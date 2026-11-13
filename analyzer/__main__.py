"""İstifadə:
    python -m analyzer analyze AAPL MSFT NVDA
    python -m analyzer backtest AAPL --years 5
    python -m analyzer account
    python -m analyzer order AAPL 1 buy
"""
from __future__ import annotations

import argparse

from . import backtest, data, indicators, signals

COLOR = {"AL": "\033[92m", "SAT": "\033[91m", "SAXLA": "\033[93m"}
RESET = "\033[0m"


def cmd_analyze(a) -> None:
    rows = []
    for t in a.tickers:
        try:
            df = indicators.add_all(data.load(t.upper(), a.years, a.source))
        except Exception as e:  # noqa: BLE001
            print(f"{t}: XƏTA - {e}")
            continue
        s = signals.latest_signal(t.upper(), df)
        rows.append(s)
        print(f"\n{COLOR[s.action]}{s.ticker}: {s.action}{RESET}  bal={s.score:+d}  "
              f"qiymət={s.price:.2f}  tarix={s.date}")
        if s.stop_loss:
            print(f"  Təklif olunan stop-loss: {s.stop_loss:.2f} "
                  f"({s.stop_loss / s.price - 1:+.1%})")
        for r in s.reasons:
            print("   ", r)
    if len(rows) > 1:
        print("\nSıralama (ən güclüdən):")
        for s in sorted(rows, key=lambda x: -x.score):
            print(f"  {s.ticker:6} {s.score:+4d}  {s.action}")


def cmd_backtest(a) -> None:
    for t in a.tickers:
        df = indicators.add_all(data.load(t.upper(), a.years, a.source))
        r = backtest.run(df)
        print(f"\n{t.upper()}  ({df.index[0].date()} → {df.index[-1].date()})")
        print(f"  Strategiya gəliri : {r.total_return:+.1%}  (illik {r.cagr:+.1%})")
        print(f"  Buy & Hold        : {r.buy_hold_return:+.1%}")
        print(f"  Max drawdown      : {r.max_drawdown:.1%}")
        print(f"  Sharpe            : {r.sharpe:.2f}")
        print(f"  Əməliyyat sayı    : {r.trades}  (uğurlu {r.win_rate:.0%})")


def cmd_account(a) -> None:
    from .broker import Alpaca
    b = Alpaca()
    acc = b.account()
    print(f"Rejim: {'LIVE' if b.live else 'PAPER'}  Nağd: {acc['cash']}  "
          f"Portfel: {acc['portfolio_value']}")
    for p in b.positions():
        print(f"  {p['symbol']:6} {p['qty']:>8}  P/L {float(p['unrealized_plpc']):+.1%}")


def cmd_order(a) -> None:
    from .broker import Alpaca
    stop = None
    if a.side == "buy":
        df = indicators.add_all(data.load(a.ticker.upper(), 2, a.source))
        stop = signals.latest_signal(a.ticker.upper(), df).stop_loss
    print(Alpaca().order(a.ticker.upper(), a.qty, a.side, stop))


def main() -> None:
    p = argparse.ArgumentParser(prog="analyzer")
    p.add_argument("--source", default="auto", choices=["auto", "yfinance", "alpaca"])
    sub = p.add_subparsers(required=True)

    s = sub.add_parser("analyze", help="Səhmlər üçün AL/SAXLA/SAT siqnalı")
    s.add_argument("tickers", nargs="+")
    s.add_argument("--years", type=int, default=2)
    s.set_defaults(fn=cmd_analyze)

    s = sub.add_parser("backtest", help="Strategiyanı keçmiş data üzərində yoxla")
    s.add_argument("tickers", nargs="+")
    s.add_argument("--years", type=int, default=5)
    s.set_defaults(fn=cmd_backtest)

    s = sub.add_parser("account", help="Alpaca hesab məlumatı")
    s.set_defaults(fn=cmd_account)

    s = sub.add_parser("order", help="Alpaca-ya əmr göndər (default paper)")
    s.add_argument("ticker")
    s.add_argument("qty", type=float)
    s.add_argument("side", choices=["buy", "sell"])
    s.set_defaults(fn=cmd_order)

    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
