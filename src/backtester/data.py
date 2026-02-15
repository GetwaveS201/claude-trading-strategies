"""
Data loading and validation
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime


class DataFeed:
    """
    Loads and validates OHLCV data from CSV files

    Supports:
    - One CSV per symbol: data/SPY.csv, data/AAPL.csv
    - Combined CSV with symbol column
    """

    REQUIRED_COLUMNS = ["datetime", "open", "high", "low", "close", "volume"]

    def __init__(self, data_dir: str, symbol: Optional[str] = None):
        """
        Initialize data feed

        Args:
            data_dir: Directory containing CSV files
            symbol: Symbol to load (if None, tries to load from combined file)
        """
        self.data_dir = Path(data_dir)
        self.symbol = symbol
        self.data: Optional[pd.DataFrame] = None

    def load(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Load data from CSV

        Returns:
            DataFrame with columns: datetime, open, high, low, close, volume
        """
        # Try to find the data file
        if self.symbol:
            # Look for symbol-specific file
            csv_path = self.data_dir / f"{self.symbol}.csv"
            if not csv_path.exists():
                # Try with _sample suffix for our test data
                csv_path = self.data_dir / f"{self.symbol}_sample.csv"
            if not csv_path.exists():
                raise FileNotFoundError(f"Data file not found: {csv_path}")

            df = pd.read_csv(csv_path)
        else:
            # Try to load combined file
            combined_files = list(self.data_dir.glob("*.csv"))
            if not combined_files:
                raise FileNotFoundError(f"No CSV files found in {self.data_dir}")

            df = pd.read_csv(combined_files[0])

            # Check if it has symbol column
            if "symbol" in df.columns:
                if self.symbol is None:
                    raise ValueError(
                        "Combined CSV found but no symbol specified. "
                        "Use --symbol to specify which symbol to load."
                    )
                df = df[df["symbol"] == self.symbol].copy()

        # Validate required columns
        missing = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        # Parse datetime
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Sort by datetime
        df = df.sort_values("datetime").reset_index(drop=True)

        # Check for duplicates
        if df["datetime"].duplicated().any():
            raise ValueError("Duplicate datetime entries found in data")

        # Filter by date range
        if start_date:
            start_dt = pd.to_datetime(start_date)
            df = df[df["datetime"] >= start_dt]

        if end_date:
            end_dt = pd.to_datetime(end_date)
            df = df[df["datetime"] <= end_dt]

        # Keep only required columns in order
        df = df[self.REQUIRED_COLUMNS].copy()

        if len(df) == 0:
            raise ValueError("No data available after filtering")

        self.data = df
        return df

    def get_bar(self, index: int) -> Optional[Dict]:
        """Get bar at index as dict"""
        if self.data is None or index >= len(self.data):
            return None

        row = self.data.iloc[index]
        return {
            "datetime": row["datetime"],
            "open": row["open"],
            "high": row["high"],
            "low": row["low"],
            "close": row["close"],
            "volume": row["volume"],
        }

    def __len__(self) -> int:
        """Return number of bars"""
        return len(self.data) if self.data is not None else 0

    def __iter__(self):
        """Iterate over bars"""
        if self.data is None:
            return iter([])

        for idx in range(len(self.data)):
            yield self.get_bar(idx)


def generate_sample_data(
    symbol: str = "SPY",
    start_date: str = "2015-01-01",
    end_date: str = "2024-12-31",
    initial_price: float = 200.0,
) -> pd.DataFrame:
    """
    Generate synthetic OHLCV data for testing

    Uses random walk with drift and realistic OHLC relationships
    """
    import numpy as np

    dates = pd.date_range(start=start_date, end=end_date, freq="D")

    # Remove weekends (simple approximation)
    dates = dates[dates.dayofweek < 5]

    n = len(dates)

    # Generate random walk for close prices
    np.random.seed(42)
    returns = np.random.normal(0.0005, 0.01, n)  # Small positive drift
    prices = initial_price * np.exp(np.cumsum(returns))

    # Generate OHLC
    data = []
    for i, date in enumerate(dates):
        close = prices[i]
        open_price = close + np.random.normal(0, 0.005 * close)

        # High/Low should bracket open and close
        high_base = max(open_price, close)
        low_base = min(open_price, close)

        high = high_base + abs(np.random.normal(0, 0.005 * close))
        low = low_base - abs(np.random.normal(0, 0.005 * close))

        volume = int(abs(np.random.normal(100_000_000, 20_000_000)))

        data.append(
            {
                "datetime": date,
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume,
            }
        )

    return pd.DataFrame(data)
