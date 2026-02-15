"""
Test commission and slippage calculations
"""

import pytest
from datetime import datetime

from src.backtester.orders import Order, OrderType, OrderSide
from src.backtester.broker import ExecutionModel


def test_commission_per_fill():
    """Test fixed commission per fill"""
    exec_model = ExecutionModel(commission_per_fill=5.0, commission_pct=0.0)

    commission = exec_model.calculate_commission(fill_price=100.0, quantity=10)
    assert commission == 5.0


def test_commission_percent():
    """Test percentage commission"""
    exec_model = ExecutionModel(commission_per_fill=0.0, commission_pct=0.1)

    # 10 shares @ $100 = $1000, 0.1% = $1.00
    commission = exec_model.calculate_commission(fill_price=100.0, quantity=10)
    assert commission == 1.0


def test_commission_combined():
    """Test combined fixed + percentage commission"""
    exec_model = ExecutionModel(commission_per_fill=1.0, commission_pct=0.1)

    # 10 shares @ $100 = $1000
    # Fixed: $1.00
    # Percent: $1.00 (0.1% of $1000)
    # Total: $2.00
    commission = exec_model.calculate_commission(fill_price=100.0, quantity=10)
    assert commission == 2.0


def test_slippage_bps():
    """Test slippage in basis points"""
    exec_model = ExecutionModel(slippage_bps=10.0, slippage_fixed=0.0)

    # 10 shares @ $100 = $1000, 10 bps = 0.1% = $1.00
    slippage = exec_model.calculate_slippage(fill_price=100.0, quantity=10, side=OrderSide.BUY)
    assert slippage == 1.0


def test_slippage_fixed():
    """Test fixed slippage per share"""
    exec_model = ExecutionModel(slippage_bps=0.0, slippage_fixed=0.05)

    # 10 shares @ $0.05 per share = $0.50
    slippage = exec_model.calculate_slippage(fill_price=100.0, quantity=10, side=OrderSide.BUY)
    assert slippage == 0.5


def test_slippage_combined():
    """Test combined bps + fixed slippage"""
    exec_model = ExecutionModel(slippage_bps=10.0, slippage_fixed=0.05)

    # 10 shares @ $100 = $1000
    # BPS: $1.00 (10 bps of $1000)
    # Fixed: $0.50 (10 shares * $0.05)
    # Total: $1.50
    slippage = exec_model.calculate_slippage(fill_price=100.0, quantity=10, side=OrderSide.BUY)
    assert slippage == 1.5


def test_fill_total_cost():
    """Test that Fill.total_cost includes price + commission + slippage"""
    exec_model = ExecutionModel(commission_per_fill=1.0, slippage_bps=1.0)

    order = Order(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.MARKET,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}
    next_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}

    fill = exec_model.try_fill_market(order, current_bar, next_bar, datetime(2024, 1, 2))

    # Price: 100 shares @ $100 = $10,000
    # Commission: $1.00
    # Slippage: 1 bp of $10,000 = $1.00
    # Total: $10,002.00
    assert fill is not None
    assert fill.fill_price == 100.0
    assert fill.commission == 1.0
    assert abs(fill.slippage - 1.0) < 0.01
    assert abs(fill.total_cost - 10002.0) < 0.01


def test_net_price():
    """Test that Fill.net_price is effective price per share"""
    exec_model = ExecutionModel(commission_per_fill=2.0, slippage_bps=10.0)

    order = Order(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.MARKET,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}
    next_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}

    fill = exec_model.try_fill_market(order, current_bar, next_bar, datetime(2024, 1, 2))

    # Price: $100.00
    # Commission: $2.00 / 100 = $0.02 per share
    # Slippage: 10 bps = $0.10 per share
    # Net: $100.12 per share
    assert fill is not None
    net_price = fill.net_price
    expected_net = (100.0 * 100 + 2.0 + 10.0) / 100
    assert abs(net_price - expected_net) < 0.01
