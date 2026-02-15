"""
Performance reporting and visualization
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from .broker import Broker, Portfolio
from .orders import OrderSide


class PerformanceMetrics:
    """Calculate performance metrics from backtest results"""

    def __init__(self, portfolio: Portfolio, broker: Broker):
        self.portfolio = portfolio
        self.broker = broker
        self.equity_df = self._build_equity_df()
        self.trades_df = self._build_trades_df()

    def _build_equity_df(self) -> pd.DataFrame:
        """Build equity curve DataFrame"""
        if not self.portfolio.equity_history:
            return pd.DataFrame()

        df = pd.DataFrame(self.portfolio.equity_history)
        df["returns"] = df["equity"].pct_change()
        df["cum_returns"] = (1 + df["returns"]).cumprod() - 1
        df["drawdown"] = (df["equity"] - df["equity"].cummax()) / df["equity"].cummax()
        return df

    def _build_trades_df(self) -> pd.DataFrame:
        """Build trades DataFrame with P&L"""
        fills = self.broker.filled_orders

        if not fills:
            return pd.DataFrame()

        # Group fills into trades (entry -> exit pairs)
        trades = []
        position = 0
        entry_price = 0.0
        entry_timestamp = None
        entry_qty = 0

        for fill in fills:
            if fill.order.side == OrderSide.BUY:
                if position == 0:
                    # New entry
                    position = fill.fill_quantity
                    entry_price = fill.net_price
                    entry_timestamp = fill.fill_timestamp
                    entry_qty = fill.fill_quantity
                else:
                    # Add to position (average in)
                    total_cost = position * entry_price + fill.fill_quantity * fill.net_price
                    position += fill.fill_quantity
                    entry_price = total_cost / position
            else:  # SELL
                if position > 0:
                    # Exit (full or partial)
                    exit_qty = min(fill.fill_quantity, position)
                    exit_price = fill.fill_price
                    exit_timestamp = fill.fill_timestamp

                    # Calculate P&L
                    pnl = (exit_price - entry_price) * exit_qty
                    pnl_pct = (exit_price / entry_price - 1) * 100

                    trades.append(
                        {
                            "entry_time": entry_timestamp,
                            "exit_time": exit_timestamp,
                            "entry_price": entry_price,
                            "exit_price": exit_price,
                            "quantity": exit_qty,
                            "pnl": pnl,
                            "pnl_pct": pnl_pct,
                            "duration_days": (exit_timestamp - entry_timestamp).days,
                        }
                    )

                    position -= exit_qty
                    if position == 0:
                        entry_price = 0.0
                        entry_timestamp = None

        return pd.DataFrame(trades)

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate all performance metrics"""
        if self.equity_df.empty:
            return self._empty_metrics()

        metrics = {}

        # Basic stats
        initial_equity = self.portfolio.initial_cash
        final_equity = self.equity_df["equity"].iloc[-1]
        total_return = (final_equity / initial_equity - 1) * 100

        metrics["initial_equity"] = initial_equity
        metrics["final_equity"] = final_equity
        metrics["total_return_pct"] = total_return

        # Time-based metrics
        start_date = self.equity_df["timestamp"].iloc[0]
        end_date = self.equity_df["timestamp"].iloc[-1]
        days = (end_date - start_date).days
        years = days / 365.25

        metrics["start_date"] = start_date.strftime("%Y-%m-%d")
        metrics["end_date"] = end_date.strftime("%Y-%m-%d")
        metrics["duration_days"] = days

        # CAGR
        if years > 0:
            cagr = (pow(final_equity / initial_equity, 1 / years) - 1) * 100
        else:
            cagr = 0.0
        metrics["cagr"] = cagr

        # Drawdown
        max_dd = self.equity_df["drawdown"].min() * 100
        metrics["max_drawdown_pct"] = max_dd

        # Risk-adjusted returns
        returns = self.equity_df["returns"].dropna()
        if len(returns) > 0:
            mean_return = returns.mean()
            std_return = returns.std()

            # Sharpe (annualized, assuming daily data)
            if std_return > 0:
                sharpe = (mean_return / std_return) * np.sqrt(252)
            else:
                sharpe = 0.0
            metrics["sharpe_ratio"] = sharpe

            # Sortino (annualized, assuming daily data)
            negative_returns = returns[returns < 0]
            if len(negative_returns) > 0:
                downside_std = negative_returns.std()
                if downside_std > 0:
                    sortino = (mean_return / downside_std) * np.sqrt(252)
                else:
                    sortino = 0.0
            else:
                sortino = 0.0
            metrics["sortino_ratio"] = sortino
        else:
            metrics["sharpe_ratio"] = 0.0
            metrics["sortino_ratio"] = 0.0

        # Trade statistics
        if not self.trades_df.empty:
            metrics["num_trades"] = len(self.trades_df)

            wins = self.trades_df[self.trades_df["pnl"] > 0]
            losses = self.trades_df[self.trades_df["pnl"] < 0]

            metrics["num_wins"] = len(wins)
            metrics["num_losses"] = len(losses)
            metrics["win_rate_pct"] = (len(wins) / len(self.trades_df)) * 100 if len(self.trades_df) > 0 else 0

            if len(wins) > 0:
                metrics["avg_win"] = wins["pnl"].mean()
                metrics["avg_win_pct"] = wins["pnl_pct"].mean()
            else:
                metrics["avg_win"] = 0.0
                metrics["avg_win_pct"] = 0.0

            if len(losses) > 0:
                metrics["avg_loss"] = losses["pnl"].mean()
                metrics["avg_loss_pct"] = losses["pnl_pct"].mean()
            else:
                metrics["avg_loss"] = 0.0
                metrics["avg_loss_pct"] = 0.0

            # Profit factor
            gross_profit = wins["pnl"].sum() if len(wins) > 0 else 0
            gross_loss = abs(losses["pnl"].sum()) if len(losses) > 0 else 0
            if gross_loss > 0:
                metrics["profit_factor"] = gross_profit / gross_loss
            else:
                metrics["profit_factor"] = 0.0

            # Exposure
            in_market_bars = (self.equity_df["market_value"] > 0).sum()
            total_bars = len(self.equity_df)
            metrics["exposure_pct"] = (in_market_bars / total_bars) * 100 if total_bars > 0 else 0
        else:
            metrics["num_trades"] = 0
            metrics["num_wins"] = 0
            metrics["num_losses"] = 0
            metrics["win_rate_pct"] = 0
            metrics["avg_win"] = 0
            metrics["avg_win_pct"] = 0
            metrics["avg_loss"] = 0
            metrics["avg_loss_pct"] = 0
            metrics["profit_factor"] = 0
            metrics["exposure_pct"] = 0

        return metrics

    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics dict"""
        return {
            "initial_equity": self.portfolio.initial_cash,
            "final_equity": self.portfolio.initial_cash,
            "total_return_pct": 0.0,
            "cagr": 0.0,
            "max_drawdown_pct": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "num_trades": 0,
            "win_rate_pct": 0.0,
            "profit_factor": 0.0,
            "exposure_pct": 0.0,
        }


class Reporter:
    """Generate reports and visualizations"""

    def __init__(self, portfolio: Portfolio, broker: Broker, config: Dict[str, Any]):
        self.portfolio = portfolio
        self.broker = broker
        self.config = config
        self.metrics_calc = PerformanceMetrics(portfolio, broker)

    def save_results(self, output_dir: Path):
        """Save all results to output directory"""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save config
        with open(output_dir / "config.json", "w") as f:
            json.dump(self.config, f, indent=2, default=str)

        # Save equity curve
        equity_df = self.metrics_calc.equity_df
        if not equity_df.empty:
            equity_df.to_csv(output_dir / "equity.csv", index=False)

        # Save trades
        trades_df = self.metrics_calc.trades_df
        if not trades_df.empty:
            trades_df.to_csv(output_dir / "trades.csv", index=False)

        # Save metrics
        metrics = self.metrics_calc.calculate_metrics()
        with open(output_dir / "summary.json", "w") as f:
            json.dump(metrics, f, indent=2, default=str)

        # Generate charts
        charts_dir = output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        self.generate_charts(charts_dir)

        return metrics

    def generate_charts(self, charts_dir: Path):
        """Generate visualization charts"""
        equity_df = self.metrics_calc.equity_df
        trades_df = self.metrics_calc.trades_df

        if equity_df.empty:
            return

        # Try to get price data from broker fills
        price_data = self._reconstruct_price_data()

        # Calculate metrics
        metrics = self.metrics_calc.calculate_metrics()

        # Use professional TradingView-style visualization
        from .visualization import TradingViewChart

        tv_chart = TradingViewChart(equity_df, trades_df, price_data, metrics)

        # 1. Main professional chart (price + equity + underwater) with metrics overlay
        tv_chart.create_professional_chart(charts_dir / "professional_overview.png")

        # 2. Metrics dashboard
        tv_chart.create_metrics_dashboard(metrics, charts_dir / "metrics_dashboard.png")

        # 3. Trade analysis
        if not trades_df.empty:
            tv_chart.create_trade_analysis(charts_dir / "trade_analysis.png")

        # Also keep legacy charts for compatibility
        self._generate_legacy_charts(charts_dir, equity_df, trades_df)

    def _reconstruct_price_data(self):
        """Reconstruct price data from equity history and fills"""
        # Build price timeline from broker fills
        fills = self.broker.filled_orders
        equity_df = self.metrics_calc.equity_df

        if not fills:
            # Use equity as proxy for price
            return pd.DataFrame({
                'datetime': equity_df['timestamp'],
                'close': equity_df['equity'] / 100  # Normalize
            })

        # Extract price points from fills
        price_points = []
        for fill in fills:
            price_points.append({
                'datetime': fill.fill_timestamp,
                'close': fill.fill_price
            })

        if price_points:
            price_df = pd.DataFrame(price_points)
            price_df = price_df.sort_values('datetime')

            # Merge with equity timeline and forward fill
            full_timeline = pd.DataFrame({'datetime': equity_df['timestamp']})
            merged = full_timeline.merge(price_df, on='datetime', how='left')
            merged['close'] = merged['close'].ffill().bfill()

            return merged
        else:
            return pd.DataFrame({
                'datetime': equity_df['timestamp'],
                'close': equity_df['equity'] / 100
            })

    def _generate_legacy_charts(self, charts_dir: Path, equity_df, trades_df):
        """Generate original simple charts for backwards compatibility"""
        # 1. Equity curve
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(equity_df["timestamp"], equity_df["equity"], linewidth=2, color='#2962FF')
        ax.set_title("Equity Curve", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Equity ($)")
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(charts_dir / "equity_curve.png", dpi=150)
        plt.close()

        # 2. Drawdown curve
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.fill_between(
            equity_df["timestamp"],
            equity_df["drawdown"] * 100,
            0,
            color="red",
            alpha=0.3,
        )
        ax.plot(equity_df["timestamp"], equity_df["drawdown"] * 100, color="red", linewidth=2)
        ax.set_title("Drawdown", fontsize=14, fontweight="bold")
        ax.set_xlabel("Date")
        ax.set_ylabel("Drawdown (%)")
        ax.grid(True, alpha=0.3)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(charts_dir / "drawdown.png", dpi=150)
        plt.close()

        # 3. Returns distribution
        if len(equity_df) > 1:
            returns = equity_df["returns"].dropna() * 100
            if len(returns) > 0:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.hist(returns, bins=50, alpha=0.7, edgecolor="black", color='#2962FF')
                ax.axvline(returns.mean(), color="red", linestyle="--", linewidth=2, label=f"Mean: {returns.mean():.2f}%")
                ax.set_title("Returns Distribution", fontsize=14, fontweight="bold")
                ax.set_xlabel("Daily Return (%)")
                ax.set_ylabel("Frequency")
                ax.legend()
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(charts_dir / "returns_distribution.png", dpi=150)
                plt.close()

    def print_summary(self):
        """Print summary to console"""
        metrics = self.metrics_calc.calculate_metrics()

        print("\n" + "=" * 60)
        print("BACKTEST SUMMARY")
        print("=" * 60)
        print(f"Period: {metrics.get('start_date', 'N/A')} to {metrics.get('end_date', 'N/A')}")
        print(f"Duration: {metrics.get('duration_days', 0)} days")
        print()
        print("PERFORMANCE")
        print("-" * 60)
        print(f"Initial Equity:     ${metrics.get('initial_equity', 0):,.2f}")
        print(f"Final Equity:       ${metrics.get('final_equity', 0):,.2f}")
        print(f"Total Return:       {metrics.get('total_return_pct', 0):.2f}%")
        print(f"CAGR:               {metrics.get('cagr', 0):.2f}%")
        print(f"Max Drawdown:       {metrics.get('max_drawdown_pct', 0):.2f}%")
        print(f"Sharpe Ratio:       {metrics.get('sharpe_ratio', 0):.2f}")
        print(f"Sortino Ratio:      {metrics.get('sortino_ratio', 0):.2f}")
        print()
        print("TRADES")
        print("-" * 60)
        print(f"Total Trades:       {metrics.get('num_trades', 0)}")
        print(f"Wins:               {metrics.get('num_wins', 0)}")
        print(f"Losses:             {metrics.get('num_losses', 0)}")
        print(f"Win Rate:           {metrics.get('win_rate_pct', 0):.2f}%")
        print(f"Profit Factor:      {metrics.get('profit_factor', 0):.2f}")
        print(f"Avg Win:            ${metrics.get('avg_win', 0):.2f} ({metrics.get('avg_win_pct', 0):.2f}%)")
        print(f"Avg Loss:           ${metrics.get('avg_loss', 0):.2f} ({metrics.get('avg_loss_pct', 0):.2f}%)")
        print(f"Exposure:           {metrics.get('exposure_pct', 0):.2f}%")
        print("=" * 60)
        print()
