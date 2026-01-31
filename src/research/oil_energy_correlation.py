from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

from src.data.market_data import download_prices


@dataclass
class OilEnergyConfig:
    start: str = "2015-01-01"
    rolling_window: int = 60
    tickers: dict[str, str] = None  # friendly -> symbol

    def __post_init__(self):
        if self.tickers is None:
            self.tickers = {
                "WTI": "CL=F",
                "Brent": "BZ=F",
                "VDE": "VDE",
                "XLE": "XLE",
                # Optional market control (for later extension):
                "SPY": "SPY",
            }


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    return prices.pct_change().dropna()


def correlation_report(
    cfg: OilEnergyConfig,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Returns:
      prices (friendly columns),
      returns,
      full-period correlation matrix (returns.corr()).
    """
    symbols = list(cfg.tickers.values())
    prices = download_prices(symbols, start=cfg.start)

    # Rename symbols -> friendly names
    inv = {v: k for k, v in cfg.tickers.items()}
    prices = prices.rename(columns=inv)

    returns = compute_returns(prices)
    corr = returns.corr()
    return prices, returns, corr


def rolling_correlations(returns: pd.DataFrame, window: int) -> pd.DataFrame:
    pairs = [
        ("WTI", "VDE"),
        ("WTI", "XLE"),
        ("Brent", "VDE"),
        ("Brent", "XLE"),
    ]
    out = pd.DataFrame(index=returns.index)
    for a, b in pairs:
        if a in returns.columns and b in returns.columns:
            out[f"{a} vs {b}"] = returns[a].rolling(window).corr(returns[b])
    return out


def save_outputs(
    out_dir: str | Path,
    prices: pd.DataFrame,
    returns: pd.DataFrame,
    corr: pd.DataFrame,
    roll: pd.DataFrame,
) -> None:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    prices.to_csv(out_dir / "prices.csv")
    returns.to_csv(out_dir / "returns.csv")
    corr.to_csv(out_dir / "correlation_matrix.csv")
    roll.to_csv(out_dir / "rolling_correlation.csv")


def plot_rolling_corr(roll: pd.DataFrame, window: int, out_path: str | Path | None = None) -> None:
    plt.figure()
    roll.plot()
    plt.title(f"Rolling Correlation ({window}d) — Oil vs Energy ETFs (Daily Returns)")
    plt.xlabel("Date")
    plt.ylabel("Correlation")
    plt.axhline(0, linewidth=1)
    plt.tight_layout()

    if out_path:
        plt.savefig(out_path, dpi=160)
    else:
        plt.show()


def plot_scatter(returns: pd.DataFrame, x: str, y: str, out_path: str | Path | None = None) -> None:
    plt.figure()
    plt.scatter(returns[x], returns[y], alpha=0.3)
    plt.title(f"{x} vs {y} — Daily Returns Scatter")
    plt.xlabel(f"{x} daily return")
    plt.ylabel(f"{y} daily return")
    plt.axhline(0, linewidth=1)
    plt.axvline(0, linewidth=1)
    plt.tight_layout()

    if out_path:
        plt.savefig(out_path, dpi=160)
    else:
        plt.show()