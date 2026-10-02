import numpy as np


def minimum_clearance(path, obstacles, obstacle_radius):
    clearances = []

    for position in path:
        for obstacle in obstacles:
            center_distance = np.linalg.norm(position - obstacle)
            clearances.append(center_distance - obstacle_radius)

    if not clearances:
        return float("inf")

    return min(clearances)


known_path = np.array([
    [0.0, 0.0],
    [2.0, 0.0]
])

known_obstacles = np.array([
    [1.0, 0.0]
])

known_clearance = minimum_clearance(
    known_path, known_obstacles, 0.25
)

assert abs(known_clearance - 0.75) < 1e-12
print("Verified point-sampled minimum clearance:",
      known_clearance, "m")
