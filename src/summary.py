import pandas as pd

def generate_basic_summary(df: pd.DataFrame, ticker: str) -> str:
    """
    Rule-based summary (no LLM). Assumes df has Close, MA20, MA50, and Volatility20 if available.
    """
    df = df.copy()

    # Use the most recent row with Close
    df = df.dropna(subset=["Close"])
    if df.empty:
        return f"Summary for {ticker}: no price data available."

    latest = df.iloc[-1]
    close = float(latest["Close"])

    lines = [f"Summary for {ticker}"]
    lines.append(f"- Latest close: {close:.2f}")

    # Trend vs moving averages
    for w in (20, 50):
        col = f"MA{w}"
        if col in df.columns:
            ma = latest.get(col)
            if pd.notna(ma):
                ma = float(ma)
                if close > ma:
                    lines.append(f"- Price is above {w}-day MA ({ma:.2f}) → uptrend bias.")
                else:
                    lines.append(f"- Price is below {w}-day MA ({ma:.2f}) → downtrend/weak bias.")

    # Simple momentum: MA20 vs MA50
    if "MA20" in df.columns and "MA50" in df.columns:
        ma20 = latest.get("MA20")
        ma50 = latest.get("MA50")
        if pd.notna(ma20) and pd.notna(ma50):
            if float(ma20) > float(ma50):
                lines.append("- MA20 is above MA50 → positive short-term momentum.")
            else:
                lines.append("- MA20 is below MA50 → weaker short-term momentum.")

    # Volatility bucket
    vol_series = df["Volatility20"].dropna() if "Volatility20" in df.columns else pd.Series(dtype=float)
    if not vol_series.empty:
        vol = float(vol_series.iloc[-1]) * 100
        if vol < 20:
            bucket = "low"
        elif vol < 40:
            bucket = "medium"
        else:
            bucket = "high"
        lines.append(f"- 20-day annualized volatility: {vol:.1f}% ({bucket}).")

    return "\n".join(lines)
