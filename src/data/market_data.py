from __future__ import annotations

import pandas as pd
import yfinance as yf


def download_prices(symbols: list[str], start: str = "2015-01-01") -> pd.DataFrame:
    """
    Download auto-adjusted close prices for given symbols via yfinance.
    Returns a DataFrame indexed by Date with columns=symbols.
    """
    raw = yf.download(symbols, start=start, auto_adjust=True, progress=False)

    if isinstance(raw.columns, pd.MultiIndex):
        close = raw["Close"]
    else:
        # Rare edge case; keep consistent
        close = raw

    close = close.sort_index().ffill()
    # Ensure columns order
    close = close.loc[:, [c for c in symbols if c in close.columns]]
    return close