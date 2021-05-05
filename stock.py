"""file containing the dataclass Stock"""
from typing import Optional


class Stock:
    """stock dataclass, used to contain information of a specific stock"""
    ticker = None
    mentions = 0.0
    sentiment = 0.0

    def __init__(self, ticker: Optional[str]):
        self.ticker = ticker

    def add_to_mentions(self, n: int):
        """add the amount given to the mentions field"""
        self.mentions = self.mentions + n
