from abc import ABC, abstractmethod
from pandas import DataFrame, Timestamp, Timedelta
from sympy.plotting.intervalmath import interval


# base strategy class
class Strategy(ABC):
    history_buffer: int = 0
    @abstractmethod
    def decide(self, history: DataFrame, current_date: Timestamp, portfolio: str) -> str:
        pass

# DCA strategy
class DCAStrategy(Strategy):
    INTERVAL_DAYS = {'1d': 1, '5d': 5, '1mo': 30.44, '3mo': 91.3, '6mo': 182.6, '1y': 365.25}

    def __init__(self, interval: str = '1mo'):
        # will default to monthly if invalid interval is provided
        self.interval = interval if interval in ['1d', '5d', '1mo', '3mo', '6mo', '1y'] else '1mo'
        self.last_buy = None

    # buy when interval passes
    def decide(self, history, current_date, portfolio):
        if not self.last_buy or (current_date - self.last_buy).days >= self.INTERVAL_DAYS[self.interval]:
            self.last_buy = current_date
            return 'buy'
        return 'hold'