import heapq

INF = float('inf')
# can i assume service id are 0 indexed
def findMintimeBwServices(n, src, edges, dst = None):
    adj = [[] for _ in range(n)]

    for u, v, w in edges:
        adj[u].append((v, w))
    
    min_time = [INF]*n
    pq = []

    heapq.heappush(pq, (0, src))
    min_time[src] = 0

    while pq:
        service_time, service = heapq.heappop(pq)

        if min_time[service] < service_time : #outdated entry
            continue

        if dst is not None and service == dst:
            return service_time

        for ns, time in adj[service]:
            if min_time[ns] > service_time + time:
                min_time[ns] = service_time + time
                heapq.heappush(pq, (min_time[ns], ns))
    
    return min_time if dst is None else INF
        



if __name__ == "__main__":
    edges = [[0 , 1, 3], [0, 2, 2], [0, 3, 6], [1, 3, 2], [1, 0, 3],[2, 0, 2], [2, 3, 1], [3, 1, 2], [3, 0, 6], [3, 2, 1]
    ]

    n = 4

    queries = [[0, 3], [1, 2], [1, 3]]

    cache = {}
    answers = []

    for src, dst in queries:
        if src not in cache:
            cache[src] = findMintimeBwServices(n, src, edges, 
                                               dst = None)
        answers.append(cache[src][dst])
    
    print([answer for answer in answers])


"""
time per query if not cached
V * (log (h_size) + (v-1)*log(h_size))
v^2*log(h_size= v^2)
2*v^2*logv
time : E*logv

space = o(E) + o(v) + o(heapsize = v^2 = E) = o(E)
"""