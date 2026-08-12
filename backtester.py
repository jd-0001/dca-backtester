from pandas import Timestamp

from portfolio import Portfolio, InsufficientFundsError
from position_sizer import PositionSizer
from strategy import Strategy
from data import Data

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
        # iterate through each row in the data
        for i in range(len(self.data)):
            try:
                # trigger buy signal
                if self.strategy.decide(self.data.iloc[:i], Timestamp(self.data.iloc[i]["date"]), self.portfolio) == "buy":
                    # calculate the amount of shares to buy based on the position sizer
                    match self.position_sizer.sizer_type:
                        # invest a fixed amount of cash
                        case 'cash':
                            self.portfolio.buy(self.ticker,
                                               self.position_sizer.sizer_amount / self.data.iloc[i]["close"],
                                               self.data.iloc[i]["close"]
                            )
                        # invest a fraction of the total portfolio value in cash
                        case 'fractional':
                            self.portfolio.buy(self.ticker,
                                               (self.position_sizer.sizer_amount * self.net_worth()) / self.data.iloc[i]["close"],
                                               self.data.iloc[i]["close"]
                            )
                        # invest a fixed number of shares
                        case 'share':
                            self.portfolio.buy(self.ticker,
                                               self.position_sizer.sizer_amount,
                                               self.data.iloc[i]["close"])
            # skip buy order if insufficient funds
            except InsufficientFundsError:
                print("Insufficient funds, skipping...")
                continue

    # calculate net worth
    def net_worth(self):
        """Calculate the total value of the portfolio including cash and shares."""
        # get current share price
        current_price = self.data.iloc[-1]["close"]
        total_value = self.portfolio.cash

        # calculate sum of share values
        for ticker, lots in self.portfolio.shares.items():
            for lot in lots:
                current_value = lot.shares * current_price
                total_value += current_value
        return total_value

    # calculate returns
    def returns(self):
        """Calculate the returns on the total value of the portfolio."""
        invested = self.portfolio.invested
        net_worth = self.net_worth()
        return {
            "Cash Invested": invested,
            "Total Value": net_worth,
            "P&L": net_worth - (self.portfolio.cash + invested),
            "P&L Percentage": (net_worth - (self.portfolio.cash + invested)) / invested * 100
        }