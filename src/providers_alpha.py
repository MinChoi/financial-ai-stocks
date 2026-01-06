import os
import requests
import pandas as pd
from src.providers import PriceDataProvider

class AlphaVantageProvider(PriceDataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_price_data(self, ticker: str, period="1y", interval="1d") -> pd.DataFrame:
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": ticker,
            "apikey": self.api_key,
            "outputsize": "compact",
        }

        r = requests.get(url, params=params)
        data = r.json()["Time Series (Daily)"]

        df = (
            pd.DataFrame.from_dict(data, orient="index")
            .astype(float)
            .rename(columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "6. volume": "Volume",
            })
        )

        df.index = pd.to_datetime(df.index)
        return df.sort_index()