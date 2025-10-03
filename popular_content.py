"""
1. content ids are positive integers
2. popularity can't be negative
3. what do we do when there is a tie (do we return any of them) or
should we break tie based on recency
4. return content with highest popuarity > 1
"""

# simple solution
"""
dict : id -> count
heap : (-count, -time, contentid)

lazy deletion

log(H)
"""

import heapq

class PopularContent:
    def __init__(self) -> None:
        self.counts = {} # plain dict — use .get(...) to read safely
        self.time = 0
        self.heap = []

    def _heap_push(self, contentId, count):
        # store (-count, -time, contentId) so largest count & most recent come first
        heapq.heappush(self.heap, (-count, -self.time, contentId))

    def increasePopularity(self, contentId):
        self.time += 1
        self.counts[contentId] = self.counts.get(contentId, 0) + 1
        self._heap_push(contentId, self.counts[contentId])

    def decreasePopularity(self, contentId):
        # if not tracked, nothing to do
        if contentId not in self.counts:
            return

        if self.counts[contentId] <= 1:
            del self.counts[contentId]
        else:
            self.counts[contentId] -= 1

        self.time += 1
        # push updated state only if count > 0
        if contentId in self.counts:
            self._heap_push(contentId, self.counts[contentId])

    def getMostPopular(self):
        # Clean stale entries lazily and return the highest current positive count
        while self.heap:
            neg_cnt, neg_time, c_id = self.heap[0]
            heap_cnt = -neg_cnt # convert back to positive
            true_cnt = self.counts.get(c_id, 0) # safe lookup without creating keys

            if heap_cnt == true_cnt and heap_cnt > 0:
                return c_id

            heapq.heappop(self.heap) # stale entry; drop it

        return -1


# -------------------------
# Example usage
# -------------------------
if __name__ == "__main__":
    t = PopularContent()
    t.increasePopularity(7)
    t.increasePopularity(7)
    t.increasePopularity(8)
    print(t.getMostPopular())   # 7
    t.increasePopularity(8)
    t.increasePopularity(8)
    print(t.getMostPopular())   # 8
    t.decreasePopularity(8)
    t.decreasePopularity(8)
    print(t.getMostPopular())   # 7
    t.decreasePopularity(7)
    t.decreasePopularity(7)
    t.decreasePopularity(8)
    print(t.getMostPopular())   # -1
