from portfolio import Portfolio


class PositionSizer:
    def __init__(self, portfolio: Portfolio, sizer_type: str, sizer_amount: float):
        self._portfolio = portfolio
        self._sizer_type = sizer_type

        # Validate sizer amount based on sizer type
        match self._sizer_type:
            case 'cash':
                if sizer_amount <= 0:
                    raise ValueError("Fixed sizer amount must be positive")
            case 'fractional':
                if not (0 <= sizer_amount <= 1):
                    raise ValueError("Fractional sizer amount must be between 0 and 1")
            case 'share':
                if sizer_amount <= 0:
                    raise ValueError("Share count sizer amount must be positive")
            case _:
                raise ValueError(f"Sizer type must be one of 'fixed', 'fractional', or 'share', got '{sizer_type}'")

        self._sizer_amount = sizer_amount

    # sizer_type getter
    @property
    def sizer_type(self):
        return self._sizer_type

    # sizer_amount getter
    @property
    def sizer_amount(self):
        return self._sizer_amount

    def size(self, price: float = None) -> float:
        """Calculate the cash amount to be invested based on the sizer type and amount."""
        match self._sizer_type:
            # Return hard cash amount
            case 'cash':
                return self._sizer_amount
            # Return fraction of current portfolio cash
            case 'fractional':
                return self._portfolio.cash * self._sizer_amount
            # Return dollar cost of buying N shares at the given price
            case 'share':
                if price is None:
                    raise ValueError("Price must be provided for share count sizer")
                if price <= 0:
                    raise ValueError(f"Price must be positive, got {price}")
                return self._sizer_amount * price