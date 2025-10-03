import heapq

class StockPrice:
    def __init__(self) -> None:
        self.timeStamps = {}
        self.max_time = 0
        self.max_heap = []
        self.min_heap = []
    
    def update(self, timestamp: int, price: int)->None:
        self.timeStamps[timestamp] = price
        
        heapq.heappush(self.max_heap, (-price, timestamp))
        heapq.heappush(self.min_heap, (price, timestamp))
        
        self.max_time = max(self.max_time, timestamp)
    
    def current(self)->int:
        return self.timeStamps[self.max_time]
    
    def maximum(self)->int:
        while self.max_heap:
            neg_price, timestamp = self.max_heap[0]

            if -neg_price == self.timeStamps[timestamp]:
                return -neg_price
            
            heapq.heappop(self.max_heap)

        raise IndexError("no prices available")
    
    def minimum(self)->int:
        while self.min_heap:
            price, timestamp = self.min_heap[0]

            if price == self.timeStamps[timestamp]:
                return price
            heapq.heappop(self.min_heap)
        raise IndexError("no prices available")

# Your StockPrice object will be instantiated and called as such:
# obj = StockPrice()
# obj.update(timestamp,price)
# param_2 = obj.current()
# param_3 = obj.maximum()
# param_4 = obj.minimum()