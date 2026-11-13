# Azərbaycandan səhm ticarəti üçün API-lər — araşdırma (noyabr 2026)

> Ölkə siyahıları dəyişir. Hesab açmazdan əvvəl brokerin rəsmi səhifəsində
> və ya dəstək xidmətində Azərbaycanın dəstəkləndiyini mütləq yoxla.

## 1. Əmr göndərmək üçün (broker API-ləri)

| Broker | Azərbaycan rezidenti | API | Uyğunluq |
|---|---|---|---|
| **Interactive Brokers (IBKR)** | Bəli (üçüncü tərəf siyahılarında var; ~217 ölkə) | TWS API (Python `ib_async`), Client Portal Web API (REST) | ⭐ Real ticarət üçün əsas seçim. ABŞ, Avropa, Asiya birjaları, aşağı komissiya. Hesab açmaq: pasport + ünvan sənədi, 1–3 gün. |
| **Alpaca** | Fərdi hesab üçün rəsmi siyahı yoxdur — `support@alpaca.markets`-dən soruşmaq lazımdır | REST + WebSocket, çox sadə | ⭐ **Paper trading (virtual pul) hamıya açıqdır** — sistemi test etmək üçün ideal. |
| **Birbank Invest** (Kapital Bank + PASHA Capital) | Bəli, yerli | İctimai API yoxdur (yalnız mobil tətbiq) | Arxa planda Alpaca Broker API işləyir; 12 000+ ABŞ səhmi/ETF, real sahiblik (CFD deyil). Avtomatlaşdırma mümkün deyil, amma əl ilə alış üçün ən rahat yerli yol. |
| **Tradier** | 75 ölkə üçün onlayn qeydiyyat, Azərbaycan təsdiqlənməyib | REST | Yoxlamaq lazımdır. |
| **Exness və s. CFD brokerləri** | Offşor qurumlar vasitəsilə | MT4/MT5 | ❌ Tövsiyə olunmur: CFD-dir (səhmə sahib olmursan), Mərkəzi Bank lisenziyası yoxdur. |

### Tövsiyə olunan yol
1. **İndi:** Alpaca paper hesabı aç (pulsuz, yalnız e-poçt) → bu analizatoru
   1–3 ay virtual pulla işlət.
2. **Nəticələr qənaətbəxşdirsə:** IBKR-də real hesab aç (və ya Alpaca live,
   əgər Azərbaycanı təsdiqləyərlərsə). Kod IBKR-ə uyğunlaşdırıla bilər.
3. Əl ilə alıb-satmaq istəsən — Birbank Invest + bu analizatorun siqnalları.

## 2. Bazar məlumatı (data) API-ləri

| Mənbə | Qiymət | Qeyd |
|---|---|---|
| **yfinance** (Yahoo) | Pulsuz, açarsız | Gündəlik data üçün kifayətdir; rəsmi deyil, bəzən limitə düşür. Analizatorda default. |
| **Alpaca Market Data** | Pulsuz (IEX feed) | Paper hesabın açarları ilə işləyir. |
| **Finnhub** | Pulsuz plan var | Xəbərlər, fundamental göstəricilər, real-time quote. |
| **Alpha Vantage** | Pulsuz (gündə ~25 sorğu) | Fundamental + texniki. |
| **Twelve Data / Polygon** | Pulsuz plan məhdud, ödənişli | Intraday / real-time üçün. |
| **IBKR market data** | Aylıq abunə (~$1–10) | IBKR hesabın olanda ən etibarlısı. |

## 3. Vergi və hüquqi qeydlər
- ABŞ səhmlərində dividendlərdən W-8BEN forması ilə ABŞ-da tutulan vergi
  (Azərbaycan–ABŞ arasında ikiqat vergi müqaviləsi olub-olmamasını yoxla).
- Xaricdəki gəlirin Azərbaycanda bəyan edilməsi ilə bağlı vergi məsləhətçisi ilə
  danış.

## Mənbələr
- https://brokerchooser.com/best-brokers/best-international-online-brokers-for-citizens-in-azerbaijan
- https://brokerchooser.com/best-brokers/best-stock-brokers-in-azerbaijan
- https://thebanks.eu/brokers/interactive-brokers
- https://tradersunion.com/brokers/forex/view/interactive_brokers/available-countries/
- https://alpaca.markets/learn/live-trading-account-non-us
- https://alpaca.markets/support
- https://alpaca.markets/blog/how-pasha-capital-and-birbank-invest-are-expanding-global-market-access-in-azerbaijan/
- https://www.crowdfundinsider.com/2026/04/272870-pasha-capital-and-birbank-invest-aim-to-expand-us-equities-access-in-azerbaijan/
- https://tradier.com/company/press/tradier-brokerage-announces-a-new-digital-onboarding-process-for-customers-of-75-countries-to-enhance-the-experience-for-the-global-active-trading-community-and-its-marketplace-of-platforms
