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
        self.cash = cash
        self.shares = shares if shares else {}

    # Cash getter
    @property
    def cash(self):
        return self._cash

    # Cash setter
    @cash.setter
    def cash(self, value):
        if value < 0:
            raise ValueError("Cash cannot be negative")
        self._cash = value

    # Buy shares of security
    def buy(self, ticker: str, shares: float, price: float):
        cost = shares * price
        # Reject if order is too expensive
        if cost > self.cash:
            raise InsufficientFundsError(f"Order cost is {cost:.2f} but available cash is {self.cash:.2f}")
        if ticker not in self.shares:
            self.shares[ticker] = []
        self.shares[ticker].append(Lot(shares, price))
        self.cash -= cost