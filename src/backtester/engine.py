"""
Main backtest engine - event-driven bar-by-bar execution
"""

from typing import Dict, Optional, Type, Any
from datetime import datetime
import json
from pathlib import Path

from .data import DataFeed
from .broker import Broker, Portfolio, ExecutionModel
from .orders import Order, OrderSide, OrderType


class Context:
    """
    Context object passed to strategy on each bar

    Provides access to current bar, portfolio, and order submission
    """

    def __init__(
        self,
        symbol: str,
        bar: Dict,
        bar_index: int,
        portfolio: Portfolio,
        broker: Broker,
    ):
        self.symbol = symbol
        self.bar = bar
        self.bar_index = bar_index
        self.portfolio = portfolio
        self.broker = broker

        # Current prices
        self.open = bar["open"]
        self.high = bar["high"]
        self.low = bar["low"]
        self.close = bar["close"]
        self.volume = bar["volume"]
        self.datetime = bar["datetime"]

    @property
    def equity(self) -> float:
        """Current equity"""
        prices = {self.symbol: self.close}
        return self.portfolio.get_equity(prices)

    @property
    def cash(self) -> float:
        """Current cash"""
        return self.portfolio.cash

    @property
    def position(self) -> int:
        """Current position quantity"""
        return self.portfolio.get_position(self.symbol).quantity

    def buy(
        self,
        quantity: Optional[int] = None,
        percent: Optional[float] = None,
        risk_pct: Optional[float] = None,
        stop_distance: Optional[float] = None,
    ):
        """
        Submit a buy market order

        Args:
            quantity: Fixed number of shares
            percent: Percent of equity to invest (0-100)
            risk_pct: Risk percent (requires stop_distance)
            stop_distance: Dollar distance to stop loss
        """
        qty = self._calculate_quantity(quantity, percent, risk_pct, stop_distance)
        if qty > 0:
            order = Order(
                symbol=self.symbol,
                side=OrderSide.BUY,
                quantity=qty,
                order_type=OrderType.MARKET,
                timestamp=self.datetime,
            )
            self.broker.submit_order(order)

    def sell(self, quantity: Optional[int] = None):
        """
        Submit a sell market order

        Args:
            quantity: Number of shares (default: all)
        """
        if quantity is None:
            quantity = self.position

        if quantity > 0:
            order = Order(
                symbol=self.symbol,
                side=OrderSide.SELL,
                quantity=quantity,
                order_type=OrderType.MARKET,
                timestamp=self.datetime,
            )
            self.broker.submit_order(order)

    def buy_limit(self, quantity: int, limit_price: float):
        """Submit a buy limit order"""
        if quantity > 0:
            order = Order(
                symbol=self.symbol,
                side=OrderSide.BUY,
                quantity=quantity,
                order_type=OrderType.LIMIT,
                limit_price=limit_price,
                timestamp=self.datetime,
            )
            self.broker.submit_order(order)

    def sell_limit(self, quantity: int, limit_price: float):
        """Submit a sell limit order"""
        if quantity > 0:
            order = Order(
                symbol=self.symbol,
                side=OrderSide.SELL,
                quantity=quantity,
                order_type=OrderType.LIMIT,
                limit_price=limit_price,
                timestamp=self.datetime,
            )
            self.broker.submit_order(order)

    def buy_stop(self, quantity: int, stop_price: float):
        """Submit a buy stop order"""
        if quantity > 0:
            order = Order(
                symbol=self.symbol,
                side=OrderSide.BUY,
                quantity=quantity,
                order_type=OrderType.STOP,
                stop_price=stop_price,
                timestamp=self.datetime,
            )
            self.broker.submit_order(order)

    def sell_stop(self, quantity: int, stop_price: float):
        """Submit a sell stop order"""
        if quantity > 0:
            order = Order(
                symbol=self.symbol,
                side=OrderSide.SELL,
                quantity=quantity,
                order_type=OrderType.STOP,
                stop_price=stop_price,
                timestamp=self.datetime,
            )
            self.broker.submit_order(order)

    def _calculate_quantity(
        self,
        quantity: Optional[int],
        percent: Optional[float],
        risk_pct: Optional[float],
        stop_distance: Optional[float],
    ) -> int:
        """Calculate order quantity from various sizing methods"""
        if quantity is not None:
            return quantity

        if percent is not None:
            # Percent of equity
            target_value = self.equity * (percent / 100.0)
            qty = int(target_value / self.close)
            return qty

        if risk_pct is not None and stop_distance is not None:
            # Risk-based sizing
            risk_amount = self.equity * (risk_pct / 100.0)
            qty = int(risk_amount / stop_distance)
            return qty

        return 0


class Strategy:
    """
    Base class for trading strategies

    Subclass this and implement on_start() and on_bar()
    """

    def __init__(self, **params):
        """Initialize strategy with parameters"""
        self.params = params

    def on_start(self):
        """Called once before backtest starts"""
        pass

    def on_bar(self, context: Context):
        """
        Called on each bar

        Args:
            context: Context object with bar data and order methods
        """
        raise NotImplementedError("Strategies must implement on_bar()")

    def on_end(self):
        """Called once after backtest ends"""
        pass


class BacktestRunner:
    """
    Main backtest engine - runs strategies bar-by-bar
    """

    def __init__(
        self,
        strategy_class: Type[Strategy],
        data_feed: DataFeed,
        initial_cash: float = 100000.0,
        commission_per_fill: float = 1.0,
        commission_pct: float = 0.0,
        slippage_bps: float = 1.0,
        slippage_fixed: float = 0.0,
        **strategy_params,
    ):
        """
        Initialize backtest runner

        Args:
            strategy_class: Strategy class to run
            data_feed: DataFeed with loaded data
            initial_cash: Starting capital
            commission_per_fill: Fixed commission per fill
            commission_pct: Commission as percent of trade value
            slippage_bps: Slippage in basis points
            slippage_fixed: Fixed slippage per share
            **strategy_params: Parameters passed to strategy
        """
        self.strategy_class = strategy_class
        self.data_feed = data_feed
        self.strategy_params = strategy_params

        # Initialize trading components
        self.portfolio = Portfolio(initial_cash=initial_cash)
        self.execution_model = ExecutionModel(
            commission_per_fill=commission_per_fill,
            commission_pct=commission_pct,
            slippage_bps=slippage_bps,
            slippage_fixed=slippage_fixed,
        )
        self.broker = Broker(self.portfolio, self.execution_model)

        # Strategy instance
        self.strategy: Optional[Strategy] = None

    def run(self) -> Dict[str, Any]:
        """
        Run the backtest

        Returns:
            Dict with results
        """
        if self.data_feed.data is None or len(self.data_feed) == 0:
            raise ValueError("No data loaded in DataFeed")

        # Initialize strategy
        self.strategy = self.strategy_class(**self.strategy_params)
        self.strategy.on_start()

        symbol = self.data_feed.symbol

        # Main event loop - iterate bar by bar
        for i in range(len(self.data_feed)):
            current_bar = self.data_feed.get_bar(i)
            next_bar = self.data_feed.get_bar(i + 1) if i + 1 < len(self.data_feed) else None

            # Create context for this bar
            context = Context(
                symbol=symbol,
                bar=current_bar,
                bar_index=i,
                portfolio=self.portfolio,
                broker=self.broker,
            )

            # Call strategy
            self.strategy.on_bar(context)

            # Process pending orders (will attempt to fill on next bar)
            if next_bar:
                self.broker.process_orders(
                    current_bar=current_bar,
                    next_bar=next_bar,
                    timestamp=next_bar["datetime"],
                )

            # Record equity
            prices = {symbol: current_bar["close"]}
            self.portfolio.record_equity(current_bar["datetime"], prices)

        # Strategy cleanup
        self.strategy.on_end()

        # Return results
        return {
            "portfolio": self.portfolio,
            "broker": self.broker,
            "strategy": self.strategy,
        }
