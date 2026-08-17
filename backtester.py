from pandas import Timestamp

from portfolio import Portfolio, InsufficientFundsError
from position_sizer import PositionSizer
from strategy import Strategy
from data import Data
import analytics

# Backtester class
class Backtester:
    def __init__(self,
                 ticker: str = 'AAPL',
                 start_date: Timestamp=Timestamp(f"{Timestamp.now().year}-01-01"),
                 end_date: Timestamp=Timestamp.now(),
                 strategy: Strategy=Strategy,
                 portfolio: Portfolio=Portfolio,
                 position_sizer: PositionSizer=PositionSizer):

        self.start_date = start_date
        self.end_date = end_date
        self.strategy = strategy
        self.ticker = ticker
        self.portfolio = portfolio
        self.position_sizer = position_sizer

        # retrieve data from sqlite
        self.data = Data(self.ticker, self.start_date, self.end_date)
        self.data = self.data.retrieve_rows(ticker, start_date, end_date)
        self.data.columns = self.data.columns.get_level_values(0)


    def run(self):
        """Simulate trading and execute buy orders based on the strategy."""
        # Record initial state
        if not self.data.empty:
            initial_date = self.data.iloc[0]["date"]
            # Before the first bar, we just have initial cash
            self.portfolio.history.append((initial_date, self.portfolio.cash))

        # iterate through each row in the data
        for i in range(len(self.data) - 1): # stop at the penultimate row because we trade on the next open
            try:
                # trigger buy signal
                # history passed to decide excludes the current bar i to avoid look-ahead bias
                if self.strategy.decide(self.data.iloc[:i], Timestamp(self.data.iloc[i]["date"]), self.portfolio) == "buy":
                    # Use the position sizer to determine the cash amount to invest
                    # We use the close price of day i as our reference for sizing
                    price_now = self.data.iloc[i]["close"]
                    amount_to_invest = self.position_sizer.size(price_now)
                    
                    # Execute trade at the NEXT day's OPEN price
                    price_next_open = self.data.iloc[i+1]["open"]
                    shares_to_buy = amount_to_invest / price_next_open
                    
                    self.portfolio.buy(self.ticker,
                                       shares_to_buy,
                                       price_next_open,
                                       date=self.data.iloc[i+1]["date"]
                    )

                current_total_value = analytics.net_worth(self.data.iloc[:i+1], self.portfolio)
                self.portfolio.history.append((self.data.iloc[i]["date"], current_total_value))

            # skip buy order if insufficient funds
            except InsufficientFundsError:
                print("Insufficient funds, skipping...")
                continue
        
        # Final update for the last day
        if not self.data.empty:
            last_idx = len(self.data) - 1
            current_total_value = analytics.net_worth(self.data.iloc[:last_idx+1], self.portfolio)
            self.portfolio.history.append((self.data.iloc[last_idx]["date"], current_total_value))
