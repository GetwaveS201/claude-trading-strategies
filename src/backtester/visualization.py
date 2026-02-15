"""
Advanced visualization matching TradingView quality
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional


class TradingViewChart:
    """
    Professional-grade charts matching TradingView aesthetics
    """

    def __init__(self, equity_df: pd.DataFrame, trades_df: pd.DataFrame, price_data: pd.DataFrame, metrics: Optional[Dict] = None):
        self.equity_df = equity_df
        self.trades_df = trades_df
        self.price_data = price_data
        self.metrics = metrics or {}

        # TradingView color scheme
        self.bg_color = '#131722'
        self.grid_color = '#2A2E39'
        self.text_color = '#D1D4DC'
        self.equity_color = '#2962FF'
        self.profit_color = '#089981'
        self.loss_color = '#F23645'
        self.buy_color = '#089981'
        self.sell_color = '#F23645'

    def create_professional_chart(self, output_path: Path):
        """
        Create TradingView-style multi-panel chart with metrics overlay
        """
        fig = plt.figure(figsize=(20, 12), facecolor=self.bg_color)

        # Create grid: 3 rows (price, equity, underwater)
        gs = fig.add_gridspec(3, 1, height_ratios=[2, 2, 1], hspace=0.05)

        ax_price = fig.add_subplot(gs[0])
        ax_equity = fig.add_subplot(gs[1], sharex=ax_price)
        ax_underwater = fig.add_subplot(gs[2], sharex=ax_price)

        # 1. PRICE CHART with trade markers
        self._plot_price_chart(ax_price)

        # 2. EQUITY CHART with underwater shading
        self._plot_equity_chart(ax_equity)

        # 3. UNDERWATER EQUITY (Drawdown)
        self._plot_underwater_chart(ax_underwater)

        # 4. Add TradingView-style metrics table overlay
        if self.metrics:
            self._add_metrics_table_overlay(ax_price)

        # Style all axes
        for ax in [ax_price, ax_equity, ax_underwater]:
            self._style_axis(ax)

        # Only show x-axis labels on bottom chart
        ax_price.tick_params(labelbottom=False)
        ax_equity.tick_params(labelbottom=False)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bg_color, edgecolor='none')
        plt.close()

    def _plot_price_chart(self, ax):
        """Plot price with buy/sell markers"""
        # Price line
        ax.plot(self.price_data['datetime'], self.price_data['close'],
                color=self.equity_color, linewidth=1.5, alpha=0.9, label='Price')

        # Trade markers
        if not self.trades_df.empty:
            # Entry points
            entries = self.trades_df.copy()
            ax.scatter(entries['entry_time'], entries['entry_price'],
                      marker='^', s=100, color=self.buy_color,
                      edgecolors='white', linewidths=1, zorder=5,
                      label='Buy', alpha=0.9)

            # Exit points
            exits = self.trades_df.copy()
            ax.scatter(exits['exit_time'], exits['exit_price'],
                      marker='v', s=100, color=self.sell_color,
                      edgecolors='white', linewidths=1, zorder=5,
                      label='Sell', alpha=0.9)

        ax.set_ylabel('Price', color=self.text_color, fontsize=11, fontweight='bold')
        ax.legend(loc='upper left', framealpha=0.2, facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color)
        ax.set_title('Price & Trades', color=self.text_color, fontsize=14,
                    fontweight='bold', pad=10)

    def _plot_equity_chart(self, ax):
        """Plot equity curve with win/loss bars"""
        # Equity line
        ax.plot(self.equity_df['timestamp'], self.equity_df['equity'],
                color=self.equity_color, linewidth=2, label='Equity')

        # Fill to initial capital
        initial = self.equity_df['equity'].iloc[0]
        ax.fill_between(self.equity_df['timestamp'], self.equity_df['equity'], initial,
                        where=(self.equity_df['equity'] >= initial),
                        color=self.profit_color, alpha=0.2, interpolate=True)
        ax.fill_between(self.equity_df['timestamp'], self.equity_df['equity'], initial,
                        where=(self.equity_df['equity'] < initial),
                        color=self.loss_color, alpha=0.2, interpolate=True)

        # Trade bars at bottom
        if not self.trades_df.empty:
            self._plot_trade_bars(ax)

        ax.set_ylabel('Equity ($)', color=self.text_color, fontsize=11, fontweight='bold')
        ax.legend(loc='upper left', framealpha=0.2, facecolor=self.bg_color,
                 edgecolor=self.grid_color, labelcolor=self.text_color)
        ax.set_title('Equity Curve', color=self.text_color, fontsize=14,
                    fontweight='bold', pad=10)

    def _plot_trade_bars(self, ax):
        """Plot trade P&L bars at bottom of equity chart"""
        y_min, y_max = ax.get_ylim()
        bar_height = (y_max - y_min) * 0.05

        for _, trade in self.trades_df.iterrows():
            color = self.profit_color if trade['pnl'] > 0 else self.loss_color

            # Draw vertical bar
            ax.plot([trade['exit_time'], trade['exit_time']],
                   [y_min, y_min + bar_height * abs(trade['pnl_pct']) / 5],
                   color=color, linewidth=2, alpha=0.6)

    def _plot_underwater_chart(self, ax):
        """Plot underwater equity (drawdown from peak)"""
        if 'drawdown' not in self.equity_df.columns:
            return

        # Drawdown as negative percentage
        drawdown_pct = self.equity_df['drawdown'] * 100

        # Fill area
        ax.fill_between(self.equity_df['timestamp'], drawdown_pct, 0,
                        color=self.loss_color, alpha=0.3)
        ax.plot(self.equity_df['timestamp'], drawdown_pct,
                color=self.loss_color, linewidth=1.5)

        ax.set_ylabel('Drawdown %', color=self.text_color, fontsize=11, fontweight='bold')
        ax.set_xlabel('Date', color=self.text_color, fontsize=11, fontweight='bold')
        ax.set_title('Underwater Equity', color=self.text_color, fontsize=14,
                    fontweight='bold', pad=10)

        # Set y-axis to show drawdown going down
        ax.set_ylim(min(drawdown_pct.min() * 1.1, -1), 1)

    def _style_axis(self, ax):
        """Apply TradingView styling to axis"""
        ax.set_facecolor(self.bg_color)
        ax.grid(True, alpha=0.1, color=self.grid_color, linewidth=0.5)

        # Spines
        for spine in ax.spines.values():
            spine.set_color(self.grid_color)
            spine.set_linewidth(1)

        # Tick colors
        ax.tick_params(colors=self.text_color, which='both', labelsize=9)

        # Date formatter
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))

    def create_metrics_dashboard(self, metrics: Dict, output_path: Path):
        """
        Create metrics table visualization matching TradingView
        """
        fig, ax = plt.subplots(figsize=(12, 8), facecolor=self.bg_color)
        ax.axis('off')

        # Organize metrics into sections
        sections = [
            {
                'title': 'PERFORMANCE',
                'metrics': [
                    ('Net Profit', f"${metrics.get('final_equity', 0) - metrics.get('initial_equity', 0):,.2f}"),
                    ('Total Return', f"{metrics.get('total_return_pct', 0):.2f}%"),
                    ('CAGR', f"{metrics.get('cagr', 0):.2f}%"),
                    ('Sharpe Ratio', f"{metrics.get('sharpe_ratio', 0):.3f}"),
                    ('Sortino Ratio', f"{metrics.get('sortino_ratio', 0):.3f}"),
                ]
            },
            {
                'title': 'RISK',
                'metrics': [
                    ('Max Drawdown', f"{metrics.get('max_drawdown_pct', 0):.2f}%"),
                    ('Avg Drawdown', f"{metrics.get('max_drawdown_pct', 0) / 2:.2f}%"),
                    ('Exposure', f"{metrics.get('exposure_pct', 0):.2f}%"),
                ]
            },
            {
                'title': 'TRADING',
                'metrics': [
                    ('Total Trades', f"{metrics.get('num_trades', 0)}"),
                    ('Winning Trades', f"{metrics.get('num_wins', 0)}"),
                    ('Losing Trades', f"{metrics.get('num_losses', 0)}"),
                    ('Win Rate', f"{metrics.get('win_rate_pct', 0):.2f}%"),
                    ('Profit Factor', f"{metrics.get('profit_factor', 0):.2f}"),
                ]
            },
            {
                'title': 'TRADE ANALYSIS',
                'metrics': [
                    ('Avg Win', f"${metrics.get('avg_win', 0):.2f}"),
                    ('Avg Win %', f"{metrics.get('avg_win_pct', 0):.2f}%"),
                    ('Avg Loss', f"${metrics.get('avg_loss', 0):.2f}"),
                    ('Avg Loss %', f"{metrics.get('avg_loss_pct', 0):.2f}%"),
                ]
            },
        ]

        # Draw sections
        y_pos = 0.95
        for section in sections:
            # Section title
            ax.text(0.05, y_pos, section['title'],
                   color=self.equity_color, fontsize=14, fontweight='bold',
                   transform=ax.transAxes)
            y_pos -= 0.05

            # Metrics
            for label, value in section['metrics']:
                ax.text(0.08, y_pos, label,
                       color=self.text_color, fontsize=11,
                       transform=ax.transAxes)

                # Color code values
                color = self.text_color
                if 'profit' in label.lower() or 'win' in label.lower() or 'return' in label.lower():
                    try:
                        val = float(value.replace('$', '').replace(',', '').replace('%', ''))
                        color = self.profit_color if val > 0 else self.loss_color
                    except:
                        pass

                ax.text(0.65, y_pos, value,
                       color=color, fontsize=11, fontweight='bold',
                       transform=ax.transAxes)
                y_pos -= 0.04

            y_pos -= 0.03

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bg_color, edgecolor='none')
        plt.close()

    def create_trade_analysis(self, output_path: Path):
        """
        Create trade distribution analysis
        """
        if self.trades_df.empty:
            return

        fig = plt.figure(figsize=(16, 10), facecolor=self.bg_color)
        gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # 1. P&L Distribution
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_pnl_distribution(ax1)

        # 2. Trade Duration
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_trade_duration(ax2)

        # 3. Cumulative P&L
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_cumulative_pnl(ax3)

        # 4. Win/Loss Streaks
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_win_loss_bars(ax4)

        for ax in [ax1, ax2, ax3, ax4]:
            self._style_axis(ax)

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, facecolor=self.bg_color, edgecolor='none')
        plt.close()

    def _plot_pnl_distribution(self, ax):
        """Plot P&L distribution histogram"""
        wins = self.trades_df[self.trades_df['pnl'] > 0]['pnl_pct']
        losses = self.trades_df[self.trades_df['pnl'] <= 0]['pnl_pct']

        bins = np.linspace(self.trades_df['pnl_pct'].min(),
                          self.trades_df['pnl_pct'].max(), 30)

        ax.hist(wins, bins=bins, color=self.profit_color, alpha=0.7, label='Wins')
        ax.hist(losses, bins=bins, color=self.loss_color, alpha=0.7, label='Losses')

        ax.axvline(0, color=self.text_color, linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('P&L %', color=self.text_color, fontsize=10)
        ax.set_ylabel('Frequency', color=self.text_color, fontsize=10)
        ax.set_title('P&L Distribution', color=self.text_color, fontsize=12, fontweight='bold')
        ax.legend(framealpha=0.2, facecolor=self.bg_color, labelcolor=self.text_color)

    def _plot_trade_duration(self, ax):
        """Plot trade duration histogram"""
        durations = self.trades_df['duration_days']

        ax.hist(durations, bins=20, color=self.equity_color, alpha=0.7, edgecolor='white')
        ax.set_xlabel('Duration (days)', color=self.text_color, fontsize=10)
        ax.set_ylabel('Frequency', color=self.text_color, fontsize=10)
        ax.set_title('Trade Duration', color=self.text_color, fontsize=12, fontweight='bold')

    def _plot_cumulative_pnl(self, ax):
        """Plot cumulative P&L per trade"""
        cum_pnl = self.trades_df['pnl'].cumsum()

        ax.plot(range(1, len(cum_pnl) + 1), cum_pnl,
                color=self.equity_color, linewidth=2)
        ax.fill_between(range(1, len(cum_pnl) + 1), cum_pnl, 0,
                        where=(cum_pnl >= 0),
                        color=self.profit_color, alpha=0.2)
        ax.fill_between(range(1, len(cum_pnl) + 1), cum_pnl, 0,
                        where=(cum_pnl < 0),
                        color=self.loss_color, alpha=0.2)

        ax.set_xlabel('Trade #', color=self.text_color, fontsize=10)
        ax.set_ylabel('Cumulative P&L ($)', color=self.text_color, fontsize=10)
        ax.set_title('Cumulative P&L by Trade', color=self.text_color, fontsize=12, fontweight='bold')

    def _plot_win_loss_bars(self, ax):
        """Plot sequential wins/losses"""
        colors = [self.profit_color if pnl > 0 else self.loss_color
                 for pnl in self.trades_df['pnl']]

        ax.bar(range(1, len(self.trades_df) + 1),
               self.trades_df['pnl'],
               color=colors, alpha=0.7, edgecolor='white', linewidth=0.5)

        ax.axhline(0, color=self.text_color, linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Trade #', color=self.text_color, fontsize=10)
        ax.set_ylabel('P&L ($)', color=self.text_color, fontsize=10)
        ax.set_title('Trade Sequence', color=self.text_color, fontsize=12, fontweight='bold')

    def _add_metrics_table_overlay(self, ax):
        """Add TradingView-style metrics table overlay on chart"""
        from matplotlib.patches import FancyBboxPatch

        # Extract metrics
        strat_ret = self.metrics.get('total_return_pct', 0.0)
        bh_ret = self.metrics.get('bh_return_pct', 0.0)
        ratio = self.metrics.get('ratio', 0.0)
        max_dd = self.metrics.get('max_drawdown_pct', 0.0)
        trades = self.metrics.get('total_trades', 0)
        win_rate = self.metrics.get('win_rate', 0.0)
        status = self.metrics.get('status', 'N/A')

        # Table position (top right)
        table_x = 0.70
        table_y = 0.97
        row_height = 0.04
        col_width = 0.12

        # Background box
        box = FancyBboxPatch(
            (table_x - 0.02, table_y - 0.35), 0.28, 0.33,
            boxstyle="round,pad=0.01",
            edgecolor=self.grid_color,
            facecolor=self.bg_color,
            alpha=0.85,
            transform=ax.transAxes,
            zorder=10
        )
        ax.add_patch(box)

        # Header
        ax.text(table_x, table_y, 'METRIC', fontsize=9, fontweight='bold',
               color=self.equity_color, transform=ax.transAxes, zorder=11)
        ax.text(table_x + col_width, table_y, 'VALUE', fontsize=9, fontweight='bold',
               color=self.equity_color, transform=ax.transAxes, zorder=11)

        # Metrics rows
        y = table_y - row_height

        # Strategy Return
        ax.text(table_x, y, 'Strategy Return %', fontsize=8,
               color=self.text_color, transform=ax.transAxes, zorder=11)
        color = self.profit_color if strat_ret > 0 else self.loss_color
        ax.text(table_x + col_width, y, f"{strat_ret:.2f}%", fontsize=8,
               color=color, fontweight='bold', transform=ax.transAxes, zorder=11)
        y -= row_height

        # B&H Return
        ax.text(table_x, y, 'Buy & Hold %', fontsize=8,
               color=self.text_color, transform=ax.transAxes, zorder=11)
        color = self.profit_color if bh_ret > 0 else self.loss_color
        ax.text(table_x + col_width, y, f"{bh_ret:.2f}%", fontsize=8,
               color=color, fontweight='bold', transform=ax.transAxes, zorder=11)
        y -= row_height

        # Ratio
        ax.text(table_x, y, 'Ratio (Strat/BH)', fontsize=8,
               color=self.text_color, transform=ax.transAxes, zorder=11)
        if pd.isna(ratio) or ratio != ratio:
            ratio_text = "N/A"
            color = self.text_color
        else:
            ratio_text = f"{ratio:.2f}x"
            color = self.profit_color if ratio >= 2.0 else self.loss_color
        ax.text(table_x + col_width, y, ratio_text, fontsize=9,
               color=color, fontweight='bold', transform=ax.transAxes, zorder=11)
        y -= row_height

        # Max DD
        ax.text(table_x, y, 'Max Drawdown %', fontsize=8,
               color=self.text_color, transform=ax.transAxes, zorder=11)
        color = self.loss_color if max_dd > 35 else self.text_color
        ax.text(table_x + col_width, y, f"{max_dd:.2f}%", fontsize=8,
               color=color, fontweight='bold', transform=ax.transAxes, zorder=11)
        y -= row_height

        # Trades
        ax.text(table_x, y, 'Total Trades', fontsize=8,
               color=self.text_color, transform=ax.transAxes, zorder=11)
        ax.text(table_x + col_width, y, f"{trades}", fontsize=8,
               color=self.text_color, fontweight='bold', transform=ax.transAxes, zorder=11)
        y -= row_height

        # Win Rate
        ax.text(table_x, y, 'Win Rate %', fontsize=8,
               color=self.text_color, transform=ax.transAxes, zorder=11)
        ax.text(table_x + col_width, y, f"{win_rate:.2f}%", fontsize=8,
               color=self.text_color, fontweight='bold', transform=ax.transAxes, zorder=11)
        y -= row_height * 1.5

        # Status
        ax.text(table_x, y, 'STATUS', fontsize=9, fontweight='bold',
               color=self.text_color, transform=ax.transAxes, zorder=11)
        status_color = self.profit_color if 'PASS' in status else self.loss_color
        ax.text(table_x + col_width, y, status, fontsize=9,
               color=status_color, fontweight='bold', transform=ax.transAxes, zorder=11)
