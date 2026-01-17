import argparse
import pandas as pd
from src.data_loader import get_price_data, add_moving_averages
from src.indicators import add_returns, add_rolling_volatility
from src.providers_yahoo import YahooProvider
from src.plotter import plot_price_with_mas, plot_volume
# later:
# from src.providers_alpha import AlphaVantageProvider

# examples
# python cli.py TSLA
# python cli.py CTT.AX
# python cli.py CTT.AX --period 1y
# python cli.py CTT.AX --windows 10 20 50 --rows 10


# extras
# Add a --plot option to show chart
# Add support for multiple tickers in one command (python cli.py AAPL MSFT TSLA)
# Save output to CSV (--out data/AAPL.csv)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Financial AI - Stock Downloader + Moving Averages (Week 1 CLI)"
    )
    parser.add_argument(
        "ticker",
        help="Stock ticker (e.g., AAPL, TSLA, BHP.AX, CBA.AX)"
    )
    parser.add_argument(
        "--period",
        default="1y",
        help="Data period (e.g., 6mo, 1y, 2y, 5y). Default: 1y"
    )
    parser.add_argument(
        "--interval",
        default="1d",
        help="Data interval (e.g., 1d, 1h). Default: 1d"
    )
    parser.add_argument(
        "--windows",
        nargs="+",
        type=int,
        default=[20, 50, 200],
        help="Moving average windows. Example: --windows 10 20 50"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=5,
        help="How many rows to print from the end. Default: 5"
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Show charts (Close + moving averages, plus volume)"
    )
    return parser.parse_args()

def main():
    args = parse_args()

    print(f"Downloading {args.ticker} (period={args.period}, interval={args.interval})...")

    provider = YahooProvider()
    # provider = AlphaVantageProvider(api_key=os.getenv("ALPHA_VANTAGE_KEY"))

    df = provider.get_price_data(args.ticker, period=args.period, interval=args.interval)


    # ######
    # print("ticker arg:", args.ticker, type(args.ticker))
    # ######

    if df.empty:
        print("❌ No data returned. Check ticker symbol or network.")
        return

    df = add_moving_averages(df, windows=tuple(args.windows))

    print("✅ Success. Last rows:")
    print(df.tail(args.rows))

    # Show latest values (useful quick check)
    latest = df.dropna().iloc[-1] if not df.dropna().empty else df.iloc[-1]
    close = latest["Close"]
    print("\nLatest summary:")
    # latest_output = format(close, '.2f')
    # latest_output = f"{close:.2f}"
    # print("- Close: ", latest_output)
    print("- Close: ", close)

    for w in args.windows:
        col = f"MA{w}"
        if col in df.columns:
            val = latest.get(col)
            if val is not None:
                print(f"- {col}: {val}")

    df = add_returns(df)
    df = add_rolling_volatility(df, window=20)
    vol_col = "Volatility20"
    latest = df.dropna().iloc[-1] if not df.dropna().empty else df.iloc[-1]
    if vol_col in df.columns:
        # print('___')
        # print(latest.get(vol_col))
        print(f"- {vol_col}: {latest[vol_col] * 100}%")
        # print('___')
        # min) error, how do i fix notna?
        # if pd.notna(latest.get(vol_col)):
        #    print(f"- {vol_col}: {latest[vol_col] * 100:.1f}%")

    if args.plot:
        plot_price_with_mas(df, args.ticker, ma_windows=tuple(args.windows))
        plot_volume(df, args.ticker)

    print('\n')

if __name__ == "__main__":
    main()

