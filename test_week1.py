from src.data_loader import get_price_data, add_moving_averages

def main():
    ticker = "AAPL"   # try "BHP.AX" later
    print(f"Downloading data for {ticker}...")

    df = get_price_data(ticker)

    if df.empty:
        print("❌ No data returned")
        return

    df = add_moving_averages(df)

    print("✅ Data loaded successfully")
    print(df.tail())  # show last 5 rows

    # Simple checks
    print("\nLatest values:")
    print("Close:", df["Close"].iloc[-1])
    print("MA20 :", df["MA20"].iloc[-1])
    print("MA50 :", df["MA50"].iloc[-1])

if __name__ == "__main__":
    main()