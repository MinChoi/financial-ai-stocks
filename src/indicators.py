import pandas as pd

TRADING_DAYS = 252

def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds daily percent returns.
    """
    df = df.copy()
    df["Return"] = df["Close"].pct_change()
    return df

def add_rolling_volatility(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Adds rolling annualized volatility based on daily returns.
    Volatility20 = std(Return over 20 days) * sqrt(252)
    """
    df = df.copy()
    if "Return" not in df.columns:
        df = add_returns(df)

    df[f"Volatility{window}"] = df["Return"].rolling(window=window).std() * (TRADING_DAYS ** 0.5)
    return df