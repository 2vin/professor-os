import heapq
import itertools

GRID = [
    "..........",
    ".#######..",
    ".......#..",
    ".#######..",
    ".........."
]

START = (0, 0)
GOAL = (9, 4)
HEURISTIC_WEIGHT = 1.0


def inside(grid, x, y):
    return 0 <= y < len(grid) and 0 <= x < len(grid[0])


def open_cell(grid, x, y):
    return inside(grid, x, y) and grid[y][x] != "#"


def neighbors(grid, node):
    x, y = node
    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

    for dx, dy in directions:
        next_x = x + dx
        next_y = y + dy
        if open_cell(grid, next_x, next_y):
            yield (next_x, next_y)


def manhattan(node, goal):
    return abs(node[0] - goal[0]) + abs(node[1] - goal[1])


def search(grid, start, goal, heuristic_weight):
    frontier = []
    counter = itertools.count()

    best_cost = {start: 0}
    came_from = {start: None}

    start_priority = heuristic_weight * manhattan(start, goal)
    heapq.heappush(frontier, (start_priority, next(counter), start))

    expanded = 0

    while frontier:
        priority, _, current = heapq.heappop(frontier)

        expected_priority = (
            best_cost[current]
            + heuristic_weight * manhattan(current, goal)
        )

        if priority != expected_priority:
            continue

        expanded += 1

        if current == goal:
            break

        for neighbor in neighbors(grid, current):
            new_cost = best_cost[current] + 1

            if neighbor not in best_cost or new_cost < best_cost[neighbor]:
                best_cost[neighbor] = new_cost
                came_from[neighbor] = current

                estimate = manhattan(neighbor, goal)
                next_priority = new_cost + heuristic_weight * estimate

                heapq.heappush(
                    frontier,
                    (next_priority, next(counter), neighbor)
                )

    if goal not in came_from:
        return None, None, expanded

    path = []
    current = goal

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path, best_cost[goal], expanded


def draw_path(grid, path):
    picture = [list(row) for row in grid]

    for x, y in path:
        if (x, y) != START and (x, y) != GOAL:
            picture[y][x] = "*"

    picture[START[1]][START[0]] = "S"
    picture[GOAL[1]][GOAL[0]] = "G"

    for row in picture:
        print("".join(row))


def main():
    dijkstra_path, dijkstra_cost, dijkstra_expanded = search(
        GRID, START, GOAL, 0.0
    )

    astar_path, astar_cost, astar_expanded = search(
        GRID, START, GOAL, HEURISTIC_WEIGHT
    )

    assert dijkstra_path is not None
    assert astar_path is not None
    assert dijkstra_cost == len(dijkstra_path) - 1
    assert astar_cost == len(astar_path) - 1
    assert astar_cost == dijkstra_cost
    assert HEURISTIC_WEIGHT == 1.0

    print("Dijkstra cost:", dijkstra_cost, "cells")
    print("Dijkstra expanded:", dijkstra_expanded, "cells")
    print("A* cost:", astar_cost, "cells")
    print("A* expanded:", astar_expanded, "cells")
    print()
    print("A* path:")
    draw_path(GRID, astar_path)


if __name__ == "__main__":
    main()
