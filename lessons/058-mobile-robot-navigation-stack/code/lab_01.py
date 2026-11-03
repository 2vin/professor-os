from collections import deque

WIDTH = 8
HEIGHT = 6
START = (0, 0)
GOAL = (7, 5)

OBSTACLES = {
    (2, 0), (2, 1), (2, 2),
    (4, 2), (5, 2), (6, 2),
    (6, 3),
    (1, 4), (2, 4), (3, 4)
}

def neighbors(cell):
    x, y = cell
    candidates = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1)
    ]

    result = []
    for nx, ny in candidates:
        inside = 0 <= nx < WIDTH and 0 <= ny < HEIGHT
        if inside and (nx, ny) not in OBSTACLES:
            result.append((nx, ny))
    return result

def shortest_path(start, goal):
    queue = deque([start])
    previous = {start: None}

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for next_cell in neighbors(current):
            if next_cell not in previous:
                previous[next_cell] = current
                queue.append(next_cell)

    if goal not in previous:
        return []

    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = previous[current]

    path.reverse()
    return path

def draw_map(path, robot_cell):
    path_set = set(path)

    for y in range(HEIGHT - 1, -1, -1):
        row = []
        for x in range(WIDTH):
            cell = (x, y)

            if cell == robot_cell:
                row.append("R")
            elif cell == START:
                row.append("S")
            elif cell == GOAL:
                row.append("G")
            elif cell in OBSTACLES:
                row.append("#")
            elif cell in path_set:
                row.append("*")
            else:
                row.append(".")
        print(" ".join(row))
    print()

def main():
    path = shortest_path(START, GOAL)

    if not path:
        print("No route found.")
        return

    assert path[0] == START
    assert path[-1] == GOAL
    assert all(cell not in OBSTACLES for cell in path)

    print("Planned route:")
    print(path)
    print("Number of moves:", len(path) - 1)
    print()

    estimated_cell = START
    draw_map(path, estimated_cell)

    for target_cell in path[1:]:
        # This tuple is a symbolic one-cell grid displacement:
        # (dx, dy). It is not a velocity, wheel-speed, or
        # curvature command. This simulation does not model
        # heading or nonholonomic motion constraints.
        control_command = (
            target_cell[0] - estimated_cell[0],
            target_cell[1] - estimated_cell[1]
        )

        print(
            "Control command:",
            control_command,
            "toward",
            target_cell
        )

        # Simulated motion: the command succeeds by one grid cell.
        estimated_cell = target_cell

        # Simulated localization update from a landmark measurement.
        measured_cell = estimated_cell
        estimated_cell = measured_cell

        draw_map(path, estimated_cell)

    assert estimated_cell == GOAL
    print("Verification: RoboRover reached the goal cell.")

if __name__ == "__main__":
    main()
