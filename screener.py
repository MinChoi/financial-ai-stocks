import argparse
import pandas as pd

from src.providers_yahoo import YahooProvider
from src.data_loader import add_moving_averages
from src.indicators import add_returns, add_rolling_volatility


def parse_args():
    p = argparse.ArgumentParser(description="Week 3: Simple Stock Screener (ASX + US)")
    p.add_argument("--tickers", nargs="+", required=True, help="Tickers e.g. AAPL MSFT BHP.AX CBA.AX")
    p.add_argument("--period", default="6mo", help="Data period: 1mo, 3mo, 6mo, 1y, 2y ...")
    p.add_argument("--interval", default="1d", help="Data interval: 1d, 1h ...")
    p.add_argument("--min_rows", type=int, default=60, help="Minimum rows required to score")
    return p.parse_args()


def score_ticker(df: pd.DataFrame) -> dict:
    """
    Simple rule-based scoring:
    +1 if Close > MA20
    +1 if Close > MA50
    +1 if MA20 > MA50
    -1 if Volatility20 > 0.40 (40%)

    Ticker      Close AboveMA20 AboveMA50 MA20>MA50    Vol20%  Score
BHP.AX  49.419998       Yes       Yes       Yes 26.778051      3
  AAPL 259.480011       Yes        No        No 20.157431      1
  TSLA 430.410004        No        No        No 39.770429      0
CBA.AX 151.479996        No        No        No 20.074730      0
  MSFT 430.290009        No        No        No 42.680212     -1

    // analysing from Chatgpt
    BHP.AX — Score 3 (strongest by your rules)
        AboveMA20: Yes
        AboveMA50: Yes
        MA20 > MA50: Yes
        Vol20% ~ 20% (reasonable)
        ✅ This matches a simple “uptrend + momentum” definition.
    TSLA — Score 1
        Close below MA20 and MA50 (down/weak trend)
        But MA20 > MA50 = Yes (short-term still above mid-term, could be recent drop)
        Volatility is higher (~31%)
        So it’s “mixed”: momentum structure might be positive, but price is currently below key averages.
    AAPL / MSFT / CBA.AX — Score 0
        All are below MA20 and MA50
        MA20 <= MA50
        Vol is not bad, but trend rules are negative → score stays 0

    """
    latest = df.dropna().iloc[-1]

    close = float(latest["Close"])
    ma20 = float(latest["MA20"]) if "MA20" in latest else None
    ma50 = float(latest["MA50"]) if "MA50" in latest else None

    vol20 = None
    if "Volatility20" in df.columns:
        v = df["Volatility20"].dropna()
        if not v.empty:
            vol20 = float(v.iloc[-1])

    score = 0
    above_ma20 = False
    above_ma50 = False
    ma20_gt_ma50 = False

    if ma20 is not None:
        above_ma20 = close > ma20
        score += 1 if above_ma20 else 0

    if ma50 is not None:
        above_ma50 = close > ma50
        score += 1 if above_ma50 else 0

    if ma20 is not None and ma50 is not None:
        ma20_gt_ma50 = ma20 > ma50
        score += 1 if ma20_gt_ma50 else 0

    if vol20 is not None and vol20 > 0.40:
        score -= 1

    return {
        "Close": close,
        "AboveMA20": "Yes" if above_ma20 else "No",
        "AboveMA50": "Yes" if above_ma50 else "No",
        "MA20>MA50": "Yes" if ma20_gt_ma50 else "No",
        "Vol20%": (vol20 * 100) if vol20 is not None else None,
        "Score": score,
    }


def main():
    args = parse_args()
    provider = YahooProvider()

    results = []
    for t in args.tickers:
        try:
            df = provider.get_price_data(t, period=args.period, interval=args.interval)

            if df is None or df.empty or len(df) < args.min_rows:
                results.append({"Ticker": t, "Error": "Not enough data"})
                continue

            df = add_moving_averages(df, windows=(20, 50))
            df = add_returns(df)
            df = add_rolling_volatility(df, window=20)

            row = {"Ticker": t}
            row.update(score_ticker(df))
            results.append(row)

        except Exception as e:
            results.append({"Ticker": t, "Error": str(e)})

    out = pd.DataFrame(results)

    # Sort best first (Score desc), errors at bottom
    if "Score" in out.columns:
        out["Score"] = pd.to_numeric(out["Score"], errors="coerce")
        out = out.sort_values(by=["Score"], ascending=False, na_position="last")

    # Pretty print
    cols = ["Ticker", "Close", "AboveMA20", "AboveMA50", "MA20>MA50", "Vol20%", "Score", "Error"]
    cols = [c for c in cols if c in out.columns]
    print(out[cols].to_string(index=False))


if __name__ == "__main__":
    main()
