"""file containing the dataclass Stock"""
from typing import Optional


class Stock:
    """stock dataclass, used to contain information of a specific stock"""
    _ticker = None
    _mentions = 0
    _total_sentiment = 0.0

    def __init__(self, ticker: Optional[str]):
        self._ticker = ticker

    def add_to_mentions(self, n: int):
        """add the n given to the mentions field"""
        self._mentions = self._mentions + n

    def add_sentiment(self, s: float):
        """add the s given to the total_sentiment field"""
        self._total_sentiment = self._total_sentiment + s

    def get_average_sentiment(self) -> float:
        """return the average sentiment. return 0 if mentions = 0"""
        if self._mentions == 0:
            return 0.0
        else:
            return self._total_sentiment / self._mentions
