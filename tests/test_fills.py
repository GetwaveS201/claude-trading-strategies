"""
Test order fill logic
"""

import pytest
from datetime import datetime

from src.backtester.orders import Order, OrderType, OrderSide
from src.backtester.broker import ExecutionModel


def test_market_order_fills_next_bar():
    """Market orders should fill at next bar open by default"""
    exec_model = ExecutionModel(fill_at_next_open=True)

    order = Order(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.MARKET,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
    }

    next_bar = {
        "open": 100.8,
        "high": 102.0,
        "low": 100.5,
        "close": 101.5,
    }

    fill = exec_model.try_fill_market(order, current_bar, next_bar, datetime(2024, 1, 2))

    assert fill is not None
    assert fill.fill_price == 100.8  # Next bar open
    assert fill.fill_quantity == 100


def test_market_order_no_fill_without_next_bar():
    """Market orders should not fill if there's no next bar"""
    exec_model = ExecutionModel()

    order = Order(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.MARKET,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {
        "open": 100.0,
        "high": 101.0,
        "low": 99.0,
        "close": 100.5,
    }

    fill = exec_model.try_fill_market(order, current_bar, None, datetime(2024, 1, 2))

    assert fill is None


def test_buy_limit_fills_when_touched():
    """Buy limit should fill when price touches limit"""
    exec_model = ExecutionModel()

    order = Order(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.LIMIT,
        limit_price=99.5,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}
    next_bar = {"open": 100.0, "high": 100.5, "low": 99.0, "close": 100.0}

    fill = exec_model.try_fill_limit(order, current_bar, next_bar, datetime(2024, 1, 2))

    assert fill is not None
    assert fill.fill_price <= order.limit_price


def test_buy_limit_no_fill_when_not_touched():
    """Buy limit should not fill when price doesn't reach limit"""
    exec_model = ExecutionModel()

    order = Order(
        symbol="SPY",
        side=OrderSide.BUY,
        quantity=100,
        order_type=OrderType.LIMIT,
        limit_price=98.0,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}
    next_bar = {"open": 100.0, "high": 100.5, "low": 99.0, "close": 100.0}

    fill = exec_model.try_fill_limit(order, current_bar, next_bar, datetime(2024, 1, 2))

    assert fill is None


def test_sell_stop_fills_when_triggered():
    """Sell stop should fill when price crosses stop"""
    exec_model = ExecutionModel()

    order = Order(
        symbol="SPY",
        side=OrderSide.SELL,
        quantity=100,
        order_type=OrderType.STOP,
        stop_price=99.0,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {"open": 100.0, "high": 101.0, "low": 99.5, "close": 100.5}
    next_bar = {"open": 100.0, "high": 100.5, "low": 98.5, "close": 99.0}

    fill = exec_model.try_fill_stop(order, current_bar, next_bar, datetime(2024, 1, 2))

    assert fill is not None
    assert fill.fill_price <= order.stop_price


def test_sell_stop_no_fill_when_not_triggered():
    """Sell stop should not fill when price doesn't cross stop"""
    exec_model = ExecutionModel()

    order = Order(
        symbol="SPY",
        side=OrderSide.SELL,
        quantity=100,
        order_type=OrderType.STOP,
        stop_price=98.0,
        timestamp=datetime(2024, 1, 1),
    )

    current_bar = {"open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5}
    next_bar = {"open": 100.0, "high": 100.5, "low": 99.0, "close": 100.0}

    fill = exec_model.try_fill_stop(order, current_bar, next_bar, datetime(2024, 1, 2))

    assert fill is None
