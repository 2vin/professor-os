import matplotlib.pyplot as plt

ROWS = 7
COLS = 9

# The map is stored as rows of cells.
# Each cell starts unknown.
world = [["?" for _ in range(COLS)] for _ in range(ROWS)]

def update_map(world, observations):
    """Apply (x, y, state) observations to the map."""
    for x, y, state in observations:
        if state not in ("free", "occupied"):
            raise ValueError("state must be 'free' or 'occupied'")
        if not (0 <= x < COLS and 0 <= y < ROWS):
            raise ValueError("observation is outside the map")
        world[y][x] = state

def count_states(world):
    counts = {"unknown": 0, "free": 0, "occupied": 0}
    for row in world:
        for cell in row:
            if cell == "?":
                counts["unknown"] += 1
            elif cell == "free":
                counts["free"] += 1
            elif cell == "occupied":
                counts["occupied"] += 1
    return counts

def display_symbol(state):
    if state == "free":
        return "."
    if state == "occupied":
        return "#"
    return "?"

# First sensor observation.
first_observation = [
    (1, 3, "free"),
    (2, 3, "free"),
    (3, 3, "occupied"),
    (1, 2, "free"),
    (1, 1, "occupied"),
]

# Second observation includes a repeated occupied cell.
second_observation = [
    (3, 3, "occupied"),
    (1, 4, "free"),
]

update_map(world, first_observation)
update_map(world, second_observation)

# Convert symbolic states into numbers for plotting.
# 1.0 = free, 0.0 = occupied, 0.5 = unknown.
plot_values = []
for row in world:
    numeric_row = []
    for cell in row:
        if cell == "free":
            numeric_row.append(1.0)
        elif cell == "occupied":
            numeric_row.append(0.0)
        else:
            numeric_row.append(0.5)
    plot_values.append(numeric_row)

counts = count_states(world)

# These assertions verify the exact map counts.
assert counts == {"unknown": 57, "free": 4, "occupied": 2}
assert world[3][3] == "occupied"
assert sum(counts.values()) == ROWS * COLS

print("Map counts:", counts)
print("Repeated occupied cell remains one occupied cell.")
print("Total cells:", sum(counts.values()))

plt.imshow(
    plot_values,
    cmap="gray",
    vmin=0.0,
    vmax=1.0,
    origin="lower",
    interpolation="nearest"
)

# RoboRover's drawing position is shown in map coordinates.
plt.scatter([1], [3], marker="o", s=120, color="tab:blue",
            label="RoboRover")

plt.xticks(range(COLS))
plt.yticks(range(ROWS))
plt.grid(True, color="black", linewidth=0.5, alpha=0.4)
plt.xlabel("Map x cell")
plt.ylabel("Map y cell")
plt.title("RoboRover's coarse occupancy sketch")
plt.legend()
plt.show()
