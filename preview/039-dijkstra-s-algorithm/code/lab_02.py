import heapq


def dijkstra(graph, start, goal):
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0.0
    queue = [(0.0, start)]

    while queue:
        cost, node = heapq.heappop(queue)
        if cost > distances[node]:
            continue
        if node == goal:
            break

        for neighbor, edge_cost in graph[node]:
            candidate = cost + edge_cost
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))

    if distances[goal] == float("inf"):
        return [], float("inf")

    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = previous[node]

    path.reverse()
    return path, distances[goal]


graph = {
    "S": [("A", 2.0), ("B", 5.0)],
    "A": [("B", 1.0), ("C", 4.0)],
    "B": [("C", 1.0), ("D", 2.0)],
    "C": [("D", 1.0), ("G", 7.0)],
    "D": [("G", 2.0)],
    "G": []
}

new_path, new_cost = dijkstra(graph, "S", "G")

assert new_path == ["S", "A", "B", "D", "G"]
assert abs(new_cost - 7.0) < 1e-9
