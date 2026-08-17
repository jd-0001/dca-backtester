from pandas import Timestamp

from backtester import Backtester
from portfolio import Portfolio
from position_sizer import PositionSizer
from strategy import DCAStrategy
import analytics

# Remove the comment to run the demo

# Invest via fixed cash amount
portfolio = Portfolio(48000)
backtester = Backtester(
    ticker='SPY',
    start_date=Timestamp("1986-01-01"),
    end_date=Timestamp("2026-01-01"),
    strategy=DCAStrategy('1y'),
    portfolio=portfolio,
    position_sizer=PositionSizer(portfolio, 'cash', 1200)
)

print("Original Value: ", portfolio.cash)
backtester.run()
returns = analytics.returns(backtester.portfolio, backtester.data.iloc[-1]['close'])
for key, value in returns.items():
    print(f"{key}: {value:,.2f}")

# Invest via fraction of portfolio value
portfolio = Portfolio(5000)
backtester = Backtester(
    ticker='SPY',
    start_date=Timestamp("2025-01-01"),
    end_date=Timestamp("2026-01-01"),
    strategy=DCAStrategy('1mo'),
    portfolio=portfolio,
    position_sizer=PositionSizer(portfolio, 'fractional', 0.03)
)
    
print("Original Value: ", portfolio.cash)
backtester.run()
returns = analytics.returns(backtester.portfolio, backtester.data.iloc[-1]['close'])
for key, value in returns.items():
    print(f"{key}: {value:,.2f}")

# Invest via fixed share amount
portfolio = Portfolio(5000)
backtester = Backtester(
    ticker='SPY',
    start_date=Timestamp("2025-01-01"),
    end_date=Timestamp("2026-01-01"),
    strategy=DCAStrategy('1mo'),
    portfolio=portfolio,
    position_sizer=PositionSizer(portfolio, 'share', 1)
)
    
print("Original Value: ", portfolio.cash)
backtester.run()
returns = analytics.returns(backtester.portfolio, backtester.data.iloc[-1]['close'])
for key, value in returns.items():
    print(f"{key}: {value:,.2f}")