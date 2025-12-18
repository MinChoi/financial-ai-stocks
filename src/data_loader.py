import yfinance as yf
import pandas as pd

def get_price_data(ticker: str, period: str = "1y", interval: str = "1d", auto_adjust: bool=True) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, auto_adjust=auto_adjust)
    return df

def add_moving_averages(df: pd.DataFrame, windows=(20, 50, 200)) -> pd.DataFrame:
    for w in windows:
        df[f"MA{w}"] = df["Close"].rolling(window=w).mean()
    return df