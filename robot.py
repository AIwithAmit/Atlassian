from collections import defaultdict, deque


def find_starts_and_destinations(edges)->dict[str, list[str]]:
    graph = defaultdict(list)
    indeg = defaultdict(int)
    outdeg = defaultdict(int)
    nodes = set()

    for u, v in edges:
        graph[u].append(v)
        outdeg[u] += 1
        indeg[v] += 1
        nodes.add(u)
        nodes.add(v)
    
    starts = [node for node in nodes if node not in indeg]
    sinks = {node for node in nodes if node not in outdeg}

    memo = {} # node -> set of reachable sinks

    def dfs(node):
        if node in memo:
            return memo[node]
        result = set()
        if node in sinks:
            result.add(node)
        elif node in graph:
            for nbr in graph[node]:
                result |= dfs(nbr)

        memo[node] = result
        return result
    
    result_map = {}
    for start in starts:
        result_map[start] = sorted(dfs(start))
    
    return result_map


if __name__ == "__main__":
    # Example test
    paths = [
        ["B", "K"], ["C", "K"], ["E", "L"], ["F", "G"], ["J", "M"],
        ["E", "F"], ["C", "G"], ["A", "B"], ["A", "C"], ["G", "H"], ["G", "I"]
    ]

    print(find_starts_and_destinations(paths))