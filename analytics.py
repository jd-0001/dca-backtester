from portfolio import Portfolio, Lot
import pandas as pd

def net_worth(data: pd.DataFrame, portfolio: Portfolio) -> float:
    """Calculate the total value of the portfolio including cash and shares."""
    # get current share price from the last row of data
    if data.empty:
        return portfolio.cash
        
    total_value = portfolio.cash

    # calculate sum of share values
    for ticker, lots in portfolio.shares.items():
        # NOTE: This implementation still assumes all shares are for the same ticker
        # passed in 'data'. If we have multiple tickers, we'd need a more robust lookup.
        # For now, we fix the redundant assignment inside the loop.
        current_price = data.iloc[-1]["close"]
        for lot in lots:
            current_value = lot.shares * current_price
            total_value += current_value
    return total_value

def returns(portfolio: Portfolio, current_price: float) -> dict:
    """Calculate the returns on the total value of the portfolio."""
    cash_basis = portfolio.cash_basis
    initial_cash = portfolio.initial_cash
    
    total_value = portfolio.cash
    for ticker, lots in portfolio.shares.items():
        for lot in lots:
            total_value += lot.shares * current_price
            
    net_worth_val = total_value
    
    pl = net_worth_val - initial_cash
    return {
        "Cash Invested": cash_basis,
        "Total Value": net_worth_val,
        "P&L": pl,
        "P&L Percentage": (pl / initial_cash * 100) if initial_cash != 0 else 0
    }