# Stock Analyzer

Texniki analizlə ABŞ səhmləri üçün **AL / SAXLA / SAT** siqnalları, backtest
və Alpaca vasitəsilə (default: virtual pul) əmr göndərmə.

> ⚠️ Bu maliyyə məsləhəti deyil. Siqnallar keçmiş qiymətlərə əsaslanır və
> gələcəyi zəmanət etmir. Əvvəl **paper trading** ilə yoxla, itirə biləcəyindən
> artıq pul qoyma.

API araşdırması: [docs/API_ARASDIRMASI.md](docs/API_ARASDIRMASI.md)

## Quraşdırma
```bash
pip install -r requirements.txt
```

## İstifadə
```bash
# Siqnallar (izahları ilə)
python -m analyzer analyze AAPL MSFT NVDA SPY

# Strategiyanı son 5 ilin datası üzərində yoxla
python -m analyzer backtest AAPL MSFT --years 5
```

### Alpaca (paper trading)
1. https://alpaca.markets saytında qeydiyyatdan keç → Paper Trading → API Keys.
2. Açarları mühit dəyişəni kimi təyin et (kodda saxlama!):
```bash
export ALPACA_API_KEY=...
export ALPACA_SECRET_KEY=...
python -m analyzer account
python -m analyzer order AAPL 1 buy     # avtomatik 2×ATR stop-loss ilə
```
Real pul yalnız `ALPACA_LIVE=1` olduqda və hər əmr əl ilə təsdiqləndikdə istifadə olunur.

## Siqnal necə hesablanır
| Faktor | Bal |
|---|---|
| Qiymət SMA200-dən yuxarı/aşağı | ±20 |
| SMA50 vs SMA200 | ±15 |
| MACD kəsişməsi / istiqaməti | ±20 / ±10 |
| RSI < 30 / > 70 / 50–70 | +15 / −15 / +5 |
| Bollinger zolağından kənar | ±10 |
| 3 aylıq momentum > ±10% | ±10 |
| Yüksək həcm təsdiqi | ±5 |

Bal ≥ 40 → **AL**, ≤ −30 → **SAT**, arası → **SAXLA**.
Stop-loss = qiymət − 2×ATR(14) (backtestdə trailing).

## Struktur
```
analyzer/
  data.py        # yfinance / Alpaca data
  indicators.py  # SMA, EMA, RSI, MACD, Bollinger, ATR
  signals.py     # bal sistemi və izahlar
  backtest.py    # long-only backtest, komissiya, növbəti gün icrası
  broker.py      # Alpaca paper/live əmrlər
tests/
```
