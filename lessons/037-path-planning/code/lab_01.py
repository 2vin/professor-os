import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Each grid move represents this physical distance.
cell_size_m = 0.5

# RoboRover's start and goal cells.
start = (1, 1)
goal = (7, 5)

# A rectangular obstacle occupying nine cells.
obstacles = set()
for x in range(3, 6):
    for y in range(2, 5):
        obstacles.add((x, y))

# A hand-designed path from start to goal.
path = [
    (1, 1), (2, 1),
    (2, 2), (2, 3), (2, 4), (2, 5),
    (3, 5), (4, 5), (5, 5), (6, 5), (7, 5)
]

def is_single_grid_step(a, b):
    """Return True only when a and b are horizontally or vertically adjacent."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return dx + dy == 1

# Verify the endpoints.
assert path[0] == start
assert path[-1] == goal

# Verify that no path cell is an obstacle.
collision_cells = [cell for cell in path if cell in obstacles]
assert collision_cells == []

# Verify that every consecutive pair is one valid grid move apart.
invalid_steps = [
    (a, b) for a, b in zip(path, path[1:])
    if not is_single_grid_step(a, b)
]
assert invalid_steps == []

# Count movements between consecutive path cells.
move_count = len(path) - 1
path_length_m = move_count * cell_size_m

# Verify the exact results for this planned route.
assert move_count == 10
assert path_length_m == 5.0

print("Path is collision-free and uses valid one-cell moves.")
print("Number of moves:", move_count)
print("Planned center-to-center distance: {:.1f} m".format(path_length_m))

# Draw the grid.
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 9)
ax.set_ylim(0, 7)
ax.set_aspect("equal")

# Draw obstacle cells.
for x, y in obstacles:
    ax.add_patch(Rectangle(
        (x - 0.5, y - 0.5), 1, 1,
        facecolor="dimgray",
        edgecolor="black"
    ))

# Draw the path as connected line segments.
path_x = [cell[0] for cell in path]
path_y = [cell[1] for cell in path]
ax.plot(path_x, path_y, color="seagreen", linewidth=3, marker="o")

# Mark start and goal.
ax.scatter([start[0]], [start[1]], color="royalblue", s=130, zorder=3)
ax.scatter([goal[0]], [goal[1]], color="gold", edgecolors="black",
           s=180, marker="*", zorder=3)

ax.text(start[0] + 0.12, start[1] + 0.12, "Start")
ax.text(goal[0] + 0.12, goal[1] + 0.12, "Goal")

ax.set_xticks(range(0, 9))
ax.set_yticks(range(0, 7))
ax.set_xlabel("Grid x-coordinate")
ax.set_ylabel("Grid y-coordinate")
ax.set_title("RoboRover's Planned Path")
ax.grid(True)
plt.show()
