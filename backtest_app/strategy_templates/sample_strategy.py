"""
Sample Moving Average Crossover Strategy
This is a simple strategy that buys when fast MA crosses above slow MA
and sells when fast MA crosses below slow MA
"""

import backtrader as bt


class MovingAverageCrossover(bt.Strategy):
    """
    Simple Moving Average Crossover Strategy

    Parameters:
    - fast_period: Period for fast moving average (default: 10)
    - slow_period: Period for slow moving average (default: 30)
    """

    params = (
        ('fast_period', 10),
        ('slow_period', 30),
    )

    def __init__(self):
        """Initialize indicators"""
        # Calculate moving averages
        self.fast_ma = bt.indicators.SMA(
            self.data.close,
            period=self.params.fast_period
        )
        self.slow_ma = bt.indicators.SMA(
            self.data.close,
            period=self.params.slow_period
        )

        # Crossover signal
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        """Execute on each bar"""
        # Check if we have an open position
        if not self.position:
            # No position - check for buy signal
            if self.crossover > 0:  # Fast MA crossed above slow MA
                # Buy with 95% of available cash
                size = int((self.broker.getcash() * 0.95) / self.data.close[0])
                if size > 0:
                    self.buy(size=size)
        else:
            # Have position - check for sell signal
            if self.crossover < 0:  # Fast MA crossed below slow MA
                # Sell entire position
                self.close()

    def log(self, txt):
        """Logging function"""
        dt = self.datas[0].datetime.date(0)
        print(f'{dt.isoformat()} {txt}')

    def notify_order(self, order):
        """Notify when orders are executed"""
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.2f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.2f}')

    def notify_trade(self, trade):
        """Notify when trades are closed"""
        if trade.isclosed:
            self.log(f'TRADE PROFIT, GROSS: {trade.pnl:.2f}, NET: {trade.pnlcomm:.2f}')
