import pandas as pd
import matplotlib.pyplot as plt

def plot_price_with_mas(df: pd.DataFrame, ticker: str, ma_windows=(20, 50)):
    df = df.copy()

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["Close"], label="Close")

    for w in ma_windows:
        col = f"MA{w}"
        if col in df.columns:
            plt.plot(df.index, df[col], label=col)

    plt.title(f"{ticker} - Price & Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_volume(df: pd.DataFrame, ticker: str):
    if "Volume" not in df.columns:
        print("No Volume column available.")
        return

    plt.figure(figsize=(12, 3))
    plt.plot(df.index, df["Volume"], label="Volume")
    plt.title(f"{ticker} - Volume")
    plt.xlabel("Date")
    plt.ylabel("Volume")
    plt.legend()
    plt.tight_layout()
    plt.show()