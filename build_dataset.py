import argparse
import os
from datetime import date

import pandas as pd

from src.providers_yahoo import YahooProvider
from src.data_loader import add_moving_averages
from src.indicators import add_returns, add_rolling_volatility


def parse_args():
    p = argparse.ArgumentParser(description="Week 3: Build ML dataset from tickers")
    p.add_argument("--tickers", nargs="+", required=True, help="Tickers e.g. AAPL MSFT BHP.AX")
    p.add_argument("--period", default="2y", help="History window: 6mo, 1y, 2y, 5y...")
    p.add_argument("--interval", default="1d", help="Data interval: 1d recommended")
    p.add_argument("--horizon", type=int, default=5, help="Future return horizon in days for label")
    p.add_argument("--min_rows", type=int, default=260, help="Minimum rows required per ticker")
    return p.parse_args()


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates feature columns from price history.
    Assumes df has Close + MA columns + Return + Volatility20.
    """
    out = df.copy()

    # Basic ratios (avoid division by zero)
    if "MA20" in out.columns:
        out["ma20_ratio"] = (out["Close"] / out["MA20"]) - 1.0
    if "MA50" in out.columns:
        out["ma50_ratio"] = (out["Close"] / out["MA50"]) - 1.0

    # Past returns as features
    out["return_1d"] = out["Close"].pct_change(1)
    out["return_5d"] = out["Close"].pct_change(5)

    # Keep volatility feature if present
    if "Volatility20" in out.columns:
        out["vol20"] = out["Volatility20"]

    return out


def add_label(df: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """
    Label = 1 if future return over `horizon` days is positive else 0.
    """
    out = df.copy()
    out["future_return"] = out["Close"].pct_change(horizon).shift(-horizon)
    out["label"] = (out["future_return"] > 0).astype(int)
    return out


def main():
    args = parse_args()
    provider = YahooProvider()

    rows = []

    for ticker in args.tickers:
        df = provider.get_price_data(ticker, period=args.period, interval=args.interval)

        if df is None or df.empty or len(df) < args.min_rows:
            print(f"Skipping {ticker}: not enough data (rows={0 if df is None else len(df)})")
            continue

        # Ensure required columns exist
        if "Close" not in df.columns:
            print(f"Skipping {ticker}: Close column missing")
            continue

        # Add indicators
        df = add_moving_averages(df, windows=(20, 50))
        df = add_returns(df)
        df = add_rolling_volatility(df, window=20)

        # Features + label
        df = build_features(df)
        df = add_label(df, horizon=args.horizon)

        # Select final columns
        final = df[[
            "Close",
            "ma20_ratio",
            "ma50_ratio",
            "return_1d",
            "return_5d",
            "vol20",
            "future_return",
            "label",
        ]].copy()

        # Add identifiers
        final["ticker"] = ticker
        final["date"] = final.index

        # Drop rows with NaNs created by rolling windows / shifts
        final = final.dropna()

        rows.append(final)

    if not rows:
        print("No data produced. (Yahoo blocked? or tickers invalid?)")
        return

    dataset = pd.concat(rows, axis=0, ignore_index=True)

    # Reorder columns
    dataset = dataset[[
        "ticker",
        "date",
        "Close",
        "ma20_ratio",
        "ma50_ratio",
        "return_1d",
        "return_5d",
        "vol20",
        "future_return",
        "label",
    ]]

    # Save date-based output
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    today = date.today().isoformat()
    output_path = os.path.join(output_dir, f"dataset_{today}.csv")

    dataset.to_csv(output_path, index=False)
    print(f"\n✅ Saved dataset to {output_path}")
    print(f"Rows: {len(dataset)}, Tickers: {dataset['ticker'].nunique()}")

    # Show quick sample
    print("\nSample:")
    print(dataset.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
