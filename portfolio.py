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
        self._invested = 0
        self._shares = shares if shares else {}

    # Cash getter
    @property
    def cash(self):
        return self._cash

    # invested getter
    @property
    def invested(self):
        return self._invested

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
    def buy(self, ticker: str, shares: float, price: float):
        """Execute a buy order for the specified number of shares of the given security."""
        cost = shares * price
        # Reject if order is too expensive
        if cost > self._cash:
            raise InsufficientFundsError(f"Order cost is {cost:.2f} but available cash is {self._cash:.2f}")
        if ticker not in self._shares:
            self._shares[ticker] = []
        self._shares[ticker].append(Lot(shares, price))
        self._cash -= cost
        self._invested += cost