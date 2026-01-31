# from pathlib import Path

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.research.oil_energy_correlation import (
    OilEnergyConfig,
    correlation_report,
    rolling_correlations,
    save_outputs,
    plot_rolling_corr,
    plot_scatter,
)

def main():
    cfg = OilEnergyConfig(start="2015-01-01", rolling_window=60)
    prices, returns, corr = correlation_report(cfg)
    roll = rolling_correlations(returns, cfg.rolling_window)

    out_dir = Path("outputs/oil_energy_corr")
    save_outputs(out_dir, prices, returns, corr, roll)

    # Save charts too
    plot_rolling_corr(roll, cfg.rolling_window, out_dir / "rolling_corr.png")
    if "WTI" in returns.columns and "VDE" in returns.columns:
        plot_scatter(returns, "WTI", "VDE", out_dir / "wti_vs_vde_scatter.png")

    print("\n=== Full-period correlation (daily returns) ===")
    print(corr.round(3))
    print(f"\nSaved outputs to: {out_dir.resolve()}")

if __name__ == "__main__":
    main()