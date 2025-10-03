"""
1. time stamps are unique integer keys for entries
&upsert update the price for same time stamp

upsert & getmax

2. how freq read and writes are?
"""

import heapq
from typing import Optional

class CommodityHeap:
    def __init__(self) -> None:
        self.timeStamps: dict[int, int] = {}   # timestamp -> latest price
        self.max_heap: list[tuple[int,int]] = []  # (-price, timestamp)

    def update(self, timestamp: int, price: int) -> None:
        self.timeStamps[timestamp] = price
        heapq.heappush(self.max_heap, (-price, timestamp))

    def maximum(self) -> Optional[int]:
        if not self.timeStamps:
            return None
        while self.max_heap:
            neg_price, ts = self.max_heap[0]
            price = -neg_price
            if self.timeStamps.get(ts) == price:
                return price
            heapq.heappop(self.max_heap)  # stale
        return None

"""
Can we reduce the time complexity of the getMaxCommodityPrice to O(1)
if the language does not support it? This can be done using a variable 
to keep the maxPrice value, but we need to update it when performing the 
upsert operations.
"""


class Commodity:
    def __init__(self):
        self.timeStamps = {}       # timestamp -> price
        self.price_count = {}      # price -> how many timestamps have this price
        self.max_price = None      # cached max

    def _recompute_max(self):
        if not self.timeStamps:
            self.max_price = None
        else:
            self.max_price = max(self.timeStamps.values())

    def update(self, timestamp, price):
        # if timestamp already existed, reduce count of its old price
        if timestamp in self.timeStamps:
            old = self.timeStamps[timestamp]
            self.price_count[old] -= 1
            if self.price_count[old] == 0:
                del self.price_count[old]

        # set new price
        self.timeStamps[timestamp] = price
        self.price_count[price] = self.price_count.get(price, 0) + 1

        # update cached max
        if self.max_price is None or price > self.max_price:
            self.max_price = price
        elif self.max_price not in self.price_count:
            self._recompute_max()

    def get_max(self):
        return self.max_price
