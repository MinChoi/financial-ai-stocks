import pandas as pd
import yfinance as yf
from src.providers import PriceDataProvider

class YahooProvider(PriceDataProvider):
    def get_price_data(self, ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        df = yf.download(
            tickers=ticker,
            period=period,
            interval=interval,
            group_by="column",
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            return pd.DataFrame()

        # ✅ If columns are MultiIndex, flatten them.
        # Typical forms:
        # 1) (PriceField, Ticker) or
        # 2) (Ticker, PriceField)
        if isinstance(df.columns, pd.MultiIndex):
            level0 = set(df.columns.get_level_values(0))
            level1 = set(df.columns.get_level_values(1))

            price_fields = {"Open", "High", "Low", "Close", "Adj Close", "Volume"}

            # If level0 contains price fields, use level0 as final column names
            if level0 & price_fields:
                df.columns = df.columns.get_level_values(0)
            # If level1 contains price fields, use level1 as final column names
            elif level1 & price_fields:
                df.columns = df.columns.get_level_values(1)
            else:
                # Fallback: join both levels
                df.columns = ["_".join(map(str, col)).strip() for col in df.columns.to_list()]

            # Optional: enforce standard column order if present
        preferred = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
        cols = [c for c in preferred if c in df.columns]
        if cols:
            df = df[cols + [c for c in df.columns if c not in cols]]

        return df