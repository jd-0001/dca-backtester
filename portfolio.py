from typing import NamedTuple

# Lot represents a single share of a security
class Lot(NamedTuple):
    shares: float
    price: float

# Custom exception for insufficient funds
class InsufficientFundsError(Exception):
    pass

# Portfolio class
class Portfolio:
    def __init__(self, cash: float = 100000, shares: dict[str, list[Lot]] = None):
        self._cash = cash
        self._initial_cash = cash
        self._cash_basis = 0
        self._shares = shares if shares else {}
        self.history = [] # List of (date, value) tuples
        self.trade_history = [] # List of (date, ticker, shares, price) tuples

    # Cash getter
    @property
    def cash(self):
        return self._cash

    # initial_cash getter
    @property
    def initial_cash(self):
        return self._initial_cash

    # cash_basis getter
    @property
    def cash_basis(self):
        return self._cash_basis

    # shares getter
    @property
    def shares(self):
        return self._shares

    # Cash setter
    @cash.setter
    def cash(self, value):
        if value < 0:
            raise ValueError("Cash cannot be negative")
        self._cash = value


    # Buy shares of security
    def buy(self, ticker: str, shares: float, price: float, date=None):
        """Execute a buy order for the specified number of shares of the given security."""
        cost = shares * price
        # Reject if order is too expensive
        if cost > self._cash:
            raise InsufficientFundsError(f"Order cost is {cost:,.2f} but available cash is {self._cash:,.2f}")
        if ticker not in self._shares:
            self._shares[ticker] = []
        self._shares[ticker].append(Lot(shares, price))
        self._cash -= cost
        self._cash_basis += cost
        self.trade_history.append((date, ticker, shares, price))