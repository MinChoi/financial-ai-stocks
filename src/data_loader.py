import yfinance as yf
import pandas as pd

def get_price_data1(ticker: str, period: str = "1y", interval: str = "1d", auto_adjust: bool=True) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=auto_adjust)
    return df





## i found issue with yahoo provider, and discussed better way to build a system
## so for now, make it work with yahoo with provider (abstract files) and will update later
## and for now, I haven't finished getting only price options instead of ticker






def get_price_data(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    try:
        df = yf.download(
            tickers=ticker,
            period=period,
            interval=interval,
            group_by="column",   # 👈 IMPORTANT
            auto_adjust=False,
            progress=False
        )

        # If columns are multi-index, flatten them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)

        return df
    except Exception:
        return pd.DataFrame

def get_price_data3(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    t = yf.Ticker(ticker)
    df = t.history(period=period, interval=interval, auto_adjust=False)

    # Normalize column names (sometimes lowercase)
    if df is None or df.empty:
        return pd.DataFrame()

    # Make sure we have a Close column
    if "Close" not in df.columns and "close" in df.columns:
        df.rename(columns={c: c.title() for c in df.columns}, inplace=True)

    return df

def add_moving_averages(df: pd.DataFrame, windows=(20, 50, 200)) -> pd.DataFrame:

    # print('DF:')
    # print(df)
    #
    # print('')
    # print('')
    # print('')
    #
    # print('pd:')
    # print(pd)
    #
    # print('')
    # print('')
    # print('')

    for w in windows:
        df[f"MA{w}"] = df["Close"].rolling(window=w).mean()
    return df