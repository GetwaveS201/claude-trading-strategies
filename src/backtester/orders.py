"""
Order and Fill objects for the backtesting engine
"""

from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class OrderType(Enum):
    """Order types supported by the engine"""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class OrderSide(Enum):
    """Order side"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """
    Represents a trading order

    Orders are placed on bar t and (by default) fill on bar t+1
    """
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    timestamp: datetime
    limit_price: Optional[float] = None  # For limit orders
    stop_price: Optional[float] = None   # For stop orders
    order_id: Optional[int] = None

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError(f"Order quantity must be positive, got {self.quantity}")

        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("Limit orders require limit_price")

        if self.order_type == OrderType.STOP and self.stop_price is None:
            raise ValueError("Stop orders require stop_price")


@dataclass
class Fill:
    """
    Represents a filled order

    Fills occur on bar t+1 after order placement (by default)
    """
    order: Order
    fill_price: float
    fill_quantity: int
    fill_timestamp: datetime
    commission: float
    slippage: float
    fill_id: Optional[int] = None

    @property
    def total_cost(self) -> float:
        """Total cost including price, commission, and slippage"""
        gross = self.fill_price * self.fill_quantity
        return gross + self.commission + self.slippage

    @property
    def net_price(self) -> float:
        """Effective price per share including all costs"""
        return self.total_cost / self.fill_quantity if self.fill_quantity > 0 else 0.0


@dataclass
class Position:
    """
    Represents a position in a symbol
    """
    symbol: str
    quantity: int = 0
    avg_price: float = 0.0

    @property
    def market_value(self) -> float:
        """Current market value (requires current price)"""
        return self.quantity * self.avg_price

    def is_flat(self) -> bool:
        """Check if position is closed"""
        return self.quantity == 0

    def update(self, fill: Fill):
        """Update position from a fill"""
        if fill.order.side == OrderSide.BUY:
            # Add to position
            total_cost = self.quantity * self.avg_price + fill.total_cost
            self.quantity += fill.fill_quantity
            self.avg_price = total_cost / self.quantity if self.quantity > 0 else 0.0
        else:
            # Reduce position
            self.quantity -= fill.fill_quantity
            if self.quantity == 0:
                self.avg_price = 0.0
