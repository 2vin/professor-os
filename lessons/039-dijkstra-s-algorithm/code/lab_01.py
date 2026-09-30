import heapq


def dijkstra(graph, start, goal):
    """Return the cheapest path and its total cost."""
    if start not in graph or goal not in graph:
        raise ValueError("start and goal must be graph keys")

    for node, neighbors in graph.items():
        for neighbor, edge_cost in neighbors:
            if neighbor not in graph:
                raise ValueError(
                    "neighbor {!r} is not a graph key".format(neighbor)
                )
            if edge_cost < 0:
                raise ValueError("Dijkstra requires nonnegative edge costs")

    distances = {}
    previous = {}

    for node in graph:
        distances[node] = float("inf")
        previous[node] = None

    distances[start] = 0.0
    priority_queue = [(0.0, start)]

    while priority_queue:
        current_cost, current = heapq.heappop(priority_queue)

        # Ignore an older queue entry if a cheaper route was found later.
        if current_cost > distances[current]:
            continue

        if current == goal:
            break

        for neighbor, edge_cost in graph[current]:
            candidate_cost = current_cost + edge_cost

            if candidate_cost < distances[neighbor]:
                distances[neighbor] = candidate_cost
                previous[neighbor] = current
                heapq.heappush(
                    priority_queue,
                    (candidate_cost, neighbor)
                )

    if distances[goal] == float("inf"):
        return [], float("inf")

    path = []
    node = goal

    while node is not None:
        path.append(node)
        node = previous[node]

    path.reverse()
    return path, distances[goal]


def build_graph():
    """Create RoboRover's weighted map. Costs are travel times in seconds."""
    return {
        "S": [("A", 2.0), ("B", 5.0)],
        "A": [("B", 1.0), ("C", 4.0)],
        "B": [("C", 1.0), ("D", 5.0)],
        "C": [("D", 1.0), ("G", 7.0)],
        "D": [("G", 2.0)],
        "G": []
    }


def run_experiment(graph, label, start="S", goal="G"):
    path, cost = dijkstra(graph, start, goal)
    print(label)
    print("Path:", " -> ".join(path) if path else "(unreachable)")
    print("Estimated travel time: {:.1f} s".format(cost))
    print()

    return path, cost


def main():
    graph = build_graph()

    path, cost = run_experiment(
        graph,
        "Experiment 1: normal floor"
    )

    assert path == ["S", "A", "B", "C", "D", "G"]
    assert abs(cost - 7.0) < 1e-9

    # Simulate a muddy connection from C to D.
    muddy_graph = build_graph()
    muddy_graph["C"] = [("D", 6.0), ("G", 7.0)]

    muddy_path, muddy_cost = run_experiment(
        muddy_graph,
        "Experiment 2: C -> D becomes muddy"
    )

    assert muddy_path == ["S", "A", "B", "D", "G"]
    assert abs(muddy_cost - 10.0) < 1e-9

    # Verify the unreachable-goal behavior.
    unreachable_graph = build_graph()
    unreachable_graph["X"] = []

    unreachable_path, unreachable_cost = run_experiment(
        unreachable_graph,
        "Experiment 3: X is unreachable",
        goal="X"
    )

    assert unreachable_path == []
    assert unreachable_cost == float("inf")

    print("All verified assertions passed.")


if __name__ == "__main__":
    main()
