# Python 3.7-compatible graph search example

GRAPH = {
    "Dock": [("Junction", 2), ("Hall", 5)],
    "Junction": [("Dock", 2), ("Ramp", 3), ("Hall", 4)],
    "Ramp": [("Junction", 3), ("Bay", 4)],
    "Hall": [("Dock", 5), ("Junction", 4), ("Bay", 2)],
    "Bay": [("Ramp", 4), ("Hall", 2)]
}


def find_routes(graph, current, goal, visited, route, cost):
    """Return every simple route from current to goal."""
    visited.add(current)
    route.append(current)

    if current == goal:
        routes = [(list(route), cost)]
    else:
        routes = []
        for neighbor, edge_cost in graph[current]:
            if neighbor not in visited:
                new_cost = cost + edge_cost
                routes.extend(
                    find_routes(
                        graph,
                        neighbor,
                        goal,
                        visited,
                        route,
                        new_cost
                    )
                )

    route.pop()
    visited.remove(current)
    return routes


def main():
    routes = find_routes(
        GRAPH,
        "Dock",
        "Bay",
        set(),
        [],
        0
    )

    routes.sort(key=lambda item: item[1])

    print("Routes from Dock to Bay:")
    for path, cost in routes:
        print(" -> ".join(path), "=", cost, "m")

    best_path, best_cost = routes[0]
    print("Best route:", " -> ".join(best_path))
    print("Best cost:", best_cost, "m")

    # These assertions verify the exact claims made by this program.
    assert best_path == ["Dock", "Hall", "Bay"]
    assert best_cost == 7
    assert len(routes) == 4


if __name__ == "__main__":
    main()
