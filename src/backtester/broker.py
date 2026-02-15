"""
Broker and Portfolio management
"""

from typing import Dict, List, Optional
from datetime import datetime
import copy

from .orders import Order, Fill, Position, OrderSide, OrderType


class ExecutionModel:
    """
    Handles order execution with fees and slippage

    Default behavior:
    - Market orders fill at NEXT bar open (t+1)
    - Limit orders fill if price touches limit
    - Stop orders fill if price crosses stop
    """

    def __init__(
        self,
        commission_per_fill: float = 1.0,
        commission_pct: float = 0.0,
        slippage_bps: float = 1.0,
        slippage_fixed: float = 0.0,
        fill_at_next_open: bool = True,  # False = fill at next close
    ):
        self.commission_per_fill = commission_per_fill
        self.commission_pct = commission_pct
        self.slippage_bps = slippage_bps
        self.slippage_fixed = slippage_fixed
        self.fill_at_next_open = fill_at_next_open

    def calculate_commission(self, fill_price: float, quantity: int) -> float:
        """Calculate commission for a fill"""
        fixed = self.commission_per_fill
        pct = (fill_price * quantity) * (self.commission_pct / 100.0)
        return fixed + pct

    def calculate_slippage(self, fill_price: float, quantity: int, side: OrderSide) -> float:
        """
        Calculate slippage cost (always positive cost)

        For buys: we pay more
        For sells: we receive less
        """
        bps_cost = (fill_price * quantity) * (self.slippage_bps / 10000.0)
        fixed_cost = self.slippage_fixed * quantity
        return bps_cost + fixed_cost

    def try_fill_market(
        self, order: Order, bar: Dict, next_bar: Optional[Dict], timestamp: datetime
    ) -> Optional[Fill]:
        """
        Fill market order at next bar

        Args:
            order: The market order
            bar: Current bar (order placed here)
            next_bar: Next bar (order fills here)
            timestamp: Fill timestamp
        """
        if next_bar is None:
            return None  # No next bar available

        # Fill at next open or next close
        fill_price = next_bar["open"] if self.fill_at_next_open else next_bar["close"]

        commission = self.calculate_commission(fill_price, order.quantity)
        slippage = self.calculate_slippage(fill_price, order.quantity, order.side)

        return Fill(
            order=order,
            fill_price=fill_price,
            fill_quantity=order.quantity,
            fill_timestamp=timestamp,
            commission=commission,
            slippage=slippage,
        )

    def try_fill_limit(
        self, order: Order, bar: Dict, next_bar: Optional[Dict], timestamp: datetime
    ) -> Optional[Fill]:
        """
        Fill limit order if price touches limit on next bar

        Buy limit: fills if low <= limit_price
        Sell limit: fills if high >= limit_price
        """
        if next_bar is None:
            return None

        limit_price = order.limit_price

        if order.side == OrderSide.BUY:
            # Buy limit fills if price goes to or below limit
            if next_bar["low"] <= limit_price:
                fill_price = min(limit_price, next_bar["open"])
            else:
                return None
        else:
            # Sell limit fills if price goes to or above limit
            if next_bar["high"] >= limit_price:
                fill_price = max(limit_price, next_bar["open"])
            else:
                return None

        commission = self.calculate_commission(fill_price, order.quantity)
        slippage = self.calculate_slippage(fill_price, order.quantity, order.side)

        return Fill(
            order=order,
            fill_price=fill_price,
            fill_quantity=order.quantity,
            fill_timestamp=timestamp,
            commission=commission,
            slippage=slippage,
        )

    def try_fill_stop(
        self, order: Order, bar: Dict, next_bar: Optional[Dict], timestamp: datetime
    ) -> Optional[Fill]:
        """
        Fill stop order if price crosses stop on next bar

        Buy stop: fills if high >= stop_price (breakout)
        Sell stop: fills if low <= stop_price (stop loss)
        """
        if next_bar is None:
            return None

        stop_price = order.stop_price

        if order.side == OrderSide.BUY:
            # Buy stop fills if price goes to or above stop
            if next_bar["high"] >= stop_price:
                fill_price = max(stop_price, next_bar["open"])
            else:
                return None
        else:
            # Sell stop fills if price goes to or below stop
            if next_bar["low"] <= stop_price:
                fill_price = min(stop_price, next_bar["open"])
            else:
                return None

        commission = self.calculate_commission(fill_price, order.quantity)
        slippage = self.calculate_slippage(fill_price, order.quantity, order.side)

        return Fill(
            order=order,
            fill_price=fill_price,
            fill_quantity=order.quantity,
            fill_timestamp=timestamp,
            commission=commission,
            slippage=slippage,
        )


class Portfolio:
    """
    Tracks cash, positions, and equity
    """

    def __init__(self, initial_cash: float = 100000.0):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, Position] = {}
        self.equity_history: List[Dict] = []

    def get_position(self, symbol: str) -> Position:
        """Get position for symbol (creates if doesn't exist)"""
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        return self.positions[symbol]

    def apply_fill(self, fill: Fill):
        """Apply a fill to the portfolio"""
        position = self.get_position(fill.order.symbol)

        if fill.order.side == OrderSide.BUY:
            # Deduct cash
            self.cash -= fill.total_cost
            position.update(fill)
        else:
            # Add cash (proceeds minus costs)
            proceeds = fill.fill_price * fill.fill_quantity
            costs = fill.commission + fill.slippage
            self.cash += proceeds - costs
            position.update(fill)

    def get_market_value(self, prices: Dict[str, float]) -> float:
        """Calculate total market value of positions"""
        total = 0.0
        for symbol, position in self.positions.items():
            if position.quantity > 0 and symbol in prices:
                total += position.quantity * prices[symbol]
        return total

    def get_equity(self, prices: Dict[str, float]) -> float:
        """Calculate total equity (cash + positions)"""
        return self.cash + self.get_market_value(prices)

    def get_exposure(self, prices: Dict[str, float]) -> float:
        """Calculate exposure as fraction of equity"""
        equity = self.get_equity(prices)
        if equity <= 0:
            return 0.0
        return self.get_market_value(prices) / equity

    def record_equity(self, timestamp: datetime, prices: Dict[str, float]):
        """Record equity snapshot"""
        equity = self.get_equity(prices)
        market_value = self.get_market_value(prices)
        self.equity_history.append(
            {
                "timestamp": timestamp,
                "equity": equity,
                "cash": self.cash,
                "market_value": market_value,
            }
        )


class Broker:
    """
    Handles order submission and execution
    """

    def __init__(
        self,
        portfolio: Portfolio,
        execution_model: Optional[ExecutionModel] = None,
    ):
        self.portfolio = portfolio
        self.execution_model = execution_model or ExecutionModel()
        self.pending_orders: List[Order] = []
        self.filled_orders: List[Fill] = []
        self.order_counter = 0
        self.fill_counter = 0

    def submit_order(self, order: Order):
        """Submit an order for execution"""
        order.order_id = self.order_counter
        self.order_counter += 1
        self.pending_orders.append(order)

    def process_orders(
        self, current_bar: Dict, next_bar: Optional[Dict], timestamp: datetime
    ):
        """
        Process pending orders and generate fills

        Orders placed on bar t attempt to fill on bar t+1
        """
        new_pending = []

        for order in self.pending_orders:
            fill = None

            if order.order_type == OrderType.MARKET:
                fill = self.execution_model.try_fill_market(
                    order, current_bar, next_bar, timestamp
                )
            elif order.order_type == OrderType.LIMIT:
                fill = self.execution_model.try_fill_limit(
                    order, current_bar, next_bar, timestamp
                )
            elif order.order_type == OrderType.STOP:
                fill = self.execution_model.try_fill_stop(
                    order, current_bar, next_bar, timestamp
                )

            if fill:
                fill.fill_id = self.fill_counter
                self.fill_counter += 1
                self.portfolio.apply_fill(fill)
                self.filled_orders.append(fill)
            else:
                # Keep in pending (for limit/stop orders that haven't triggered)
                # In this simple implementation, we only keep them for one bar
                # A more sophisticated system would keep them until cancelled
                pass

        # Clear pending orders (simple one-bar-only pending logic)
        self.pending_orders = []
