import math

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.patches import Patch, Rectangle

# Grid dimensions: columns run left-right, rows run bottom-top.
WIDTH = 12
HEIGHT = 9
MAX_RANGE_CELLS = 8
CELL_SIZE = 0.25
GRID_ORIGIN = (0.0, 0.0)


def world_to_grid(x, y, resolution, origin=(0.0, 0.0)):
    """Convert a world-frame position to (column, row) indices."""
    column = math.floor((x - origin[0]) / resolution)
    row = math.floor((y - origin[1]) / resolution)
    return column, row


# RoboRover's physical starting position, expressed in the grid frame.
ROVER_WORLD_X = 0.75
ROVER_WORLD_Y = 1.00
ROVER_X, ROVER_Y = world_to_grid(
    ROVER_WORLD_X,
    ROVER_WORLD_Y,
    CELL_SIZE,
    GRID_ORIGIN
)

# Verify the physical-to-grid conversion used by the simulation.
assert (ROVER_X, ROVER_Y) == (3, 4)

# Build the hidden environment.
# 0 means physically free; 1 means physically occupied.
environment = [[0 for x in range(WIDTH)] for y in range(HEIGHT)]

# Add walls around the boundary.
for x in range(WIDTH):
    environment[0][x] = 1
    environment[HEIGHT - 1][x] = 1

for y in range(HEIGHT):
    environment[y][0] = 1
    environment[y][WIDTH - 1] = 1

# Add a rectangular crate.
crate_cells = [(7, 4), (7, 5), (8, 4), (8, 5)]
for x, y in crate_cells:
    environment[y][x] = 1

# Validate the configured starting position before marking it free.
assert 0 <= ROVER_X < WIDTH
assert 0 <= ROVER_Y < HEIGHT
assert environment[ROVER_Y][ROVER_X] == 0, (
    "RoboRover's starting cell must be physically free."
)

# RoboRover starts with no map knowledge.
occupancy_map = [[-1 for x in range(WIDTH)] for y in range(HEIGHT)]

# Eight directions: four cardinal and four diagonal.
directions = [
    (-1, 0), (1, 0), (0, -1), (0, 1),
    (-1, -1), (-1, 1), (1, -1), (1, 1)
]

# The robot's own cell is known to be free.
occupancy_map[ROVER_Y][ROVER_X] = 0

# Simulate one ray in each direction.
for dx, dy in directions:
    for step in range(1, MAX_RANGE_CELLS + 1):
        x = ROVER_X + dx * step
        y = ROVER_Y + dy * step

        # Stop if the ray leaves the grid.
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            break

        if environment[y][x] == 1:
            # The beam hit an obstacle.
            occupancy_map[y][x] = 1
            break
        else:
            # The beam traveled through this cell.
            occupancy_map[y][x] = 0

# Basic verification of the simulation's meaning.
assert occupancy_map[ROVER_Y][ROVER_X] == 0
assert any(
    occupancy_map[y][x] == 1
    for y in range(HEIGHT)
    for x in range(WIDTH)
)
assert all(
    occupancy_map[y][x] in (-1, 0, 1)
    for y in range(HEIGHT)
    for x in range(WIDTH)
)

known_cells = sum(
    occupancy_map[y][x] != -1
    for y in range(HEIGHT)
    for x in range(WIDTH)
)

# With the original constants, the eight rays visit 29 distinct cells,
# plus the known starting cell, for 30 known cells total.
assert known_cells == 30
print("Known cells:", known_cells)
print("Expected known cells for the original constants: 30")
print("Unknown cells:", WIDTH * HEIGHT - known_cells)
print("The verification checks passed.")

# Display the hidden environment and the partial occupancy grid.
fig, axes = plt.subplots(1, 2, figsize=(11, 5))

axes[0].imshow(environment, origin="lower", cmap="Greys", vmin=0, vmax=1)
axes[0].scatter([ROVER_X], [ROVER_Y], c="blue", s=90, label="RoboRover")
axes[0].set_title("Hidden physical environment")
axes[0].set_xlabel("Column")
axes[0].set_ylabel("Row")
axes[0].legend()

map_colors = ["lightgray", "white", "firebrick"]
map_cmap = ListedColormap(map_colors)
map_norm = BoundaryNorm([-1.5, -0.5, 0.5, 1.5], map_cmap.N)

axes[1].imshow(
    occupancy_map,
    origin="lower",
    cmap=map_cmap,
    norm=map_norm
)
axes[1].scatter([ROVER_X], [ROVER_Y], c="blue", s=90, label="RoboRover")
axes[1].set_title("RoboRover's partial occupancy grid")
axes[1].set_xlabel("Column")
axes[1].set_ylabel("Row")

# imshow does not render hatch patterns. Add one Rectangle patch per
# unknown cell so that the plotted cells themselves, not only the legend,
# display the hatch pattern.
for y in range(HEIGHT):
    for x in range(WIDTH):
        if occupancy_map[y][x] == -1:
            axes[1].add_patch(
                Rectangle(
                    (x - 0.5, y - 0.5),
                    1,
                    1,
                    facecolor="none",
                    edgecolor="black",
                    hatch="///",
                    linewidth=0
                )
            )

map_legend = [
    Patch(facecolor="lightgray", edgecolor="black", hatch="///",
          label="Unknown (-1)"),
    Patch(facecolor="white", edgecolor="black",
          label="Free (0)"),
    Patch(facecolor="firebrick", edgecolor="black",
          label="Occupied (1)")
]
axes[1].legend(handles=map_legend, loc="upper right")

plt.tight_layout()
plt.show()
