"""Alpaca Trading API ilə əmr göndərmək (default: PAPER - virtual pul).

Real pula keçmək üçün ALPACA_LIVE=1 təyin etmək LAZIMDIR və hər əmr
əlavə olaraq təsdiq istəyir. Bu bilərəkdəndir.
"""
from __future__ import annotations

import os

import requests

PAPER = "https://paper-api.alpaca.markets"
LIVE = "https://api.alpaca.markets"


class Alpaca:
    def __init__(self) -> None:
        self.live = os.getenv("ALPACA_LIVE") == "1"
        self.base = LIVE if self.live else PAPER
        self.h = {
            "APCA-API-KEY-ID": os.environ["ALPACA_API_KEY"],
            "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"],
        }

    def _get(self, path: str):
        r = requests.get(self.base + path, headers=self.h, timeout=30)
        r.raise_for_status()
        return r.json()

    def account(self) -> dict:
        return self._get("/v2/account")

    def positions(self) -> list[dict]:
        return self._get("/v2/positions")

    def order(self, symbol: str, qty: float, side: str,
              stop_loss: float | None = None) -> dict:
        if self.live:
            ans = input(f"REAL PUL: {side.upper()} {qty} {symbol}. Təsdiq üçün 'beli' yaz: ")
            if ans.strip().lower() != "beli":
                raise SystemExit("Ləğv edildi.")
        body = {"symbol": symbol, "qty": str(qty), "side": side,
                "type": "market", "time_in_force": "day"}
        if stop_loss and side == "buy":
            body.update(order_class="oto", stop_loss={"stop_price": f"{stop_loss:.2f}"})
        r = requests.post(self.base + "/v2/orders", headers=self.h, json=body, timeout=30)
        r.raise_for_status()
        return r.json()
