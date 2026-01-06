import pandas as pd

class PriceDataProvider:
    def get_price_data(
        self,
        ticker: str,
        period: str = "1y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        raise NotImplementedError