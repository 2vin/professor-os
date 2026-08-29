import math
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

# Each coordinate represents a point location in the map frame.
# For RoboRover, this point is its modelled centre.
rover = (1, -1)

targets = {
    "A": (4, 3),
    "B": (-1, 1),
    "C": (1, -6),
    "D": (7, 7)
}

distances = {}

for name, (x, y) in targets.items():
    horizontal_difference = x - rover[0]
    vertical_difference = y - rover[1]
    distance = math.sqrt(
        horizontal_difference ** 2 + vertical_difference ** 2
    )
    distances[name] = distance
    print("{}: ({}, {}) -> {:.3f} units from RoboRover".format(
        name, x, y, distance
    ))

assert math.isclose(distances["A"], 5.0)
assert math.isclose(distances["B"], math.sqrt(8.0))
assert math.isclose(distances["C"], 5.0)
assert math.isclose(distances["D"], 10.0)

closest_name = min(distances, key=distances.get)
farthest_name = max(distances, key=distances.get)

print("Closest target: {}".format(closest_name))
print("Farthest target: {}".format(farthest_name))
print("Verified: A and C are exactly 5 units from RoboRover.")

assert closest_name == "B"
assert farthest_name == "D"

fig, ax = plt.subplots()
ax.axhline(0, color="black", linewidth=0.8)
ax.axvline(0, color="black", linewidth=0.8)

for name, (x, y) in targets.items():
    ax.scatter(x, y, marker="o", s=80)
    ax.text(x + 0.15, y + 0.15, name)

rover_x, rover_y = rover
ax.scatter(
    rover_x, rover_y, color="red", marker="X", s=120,
    label="RoboRover"
)
ax.text(rover_x + 0.15, rover_y + 0.15, "RoboRover")

ax.scatter(0, 0, color="black", marker="+", s=100, label="origin")
ax.text(0.15, 0.15, "origin")

# A and C are both exactly 5 units from RoboRover.
# Draw their shared distance boundary to make that equality visible.
distance_boundary = Circle(
    (rover_x, rover_y),
    radius=5.0,
    fill=False,
    linestyle="--",
    linewidth=1.2,
    color="tab:purple",
    label="5-unit boundary"
)
ax.add_patch(distance_boundary)

ax.set_title("RoboRover's Coordinate Map")
ax.set_xlabel("x coordinate (units)")
ax.set_ylabel("y coordinate (units)")
ax.set_aspect("equal", adjustable="box")
ax.set_xlim(-5, 8)
ax.set_ylim(-7, 8)
ax.grid(True)
ax.legend()
plt.show()
