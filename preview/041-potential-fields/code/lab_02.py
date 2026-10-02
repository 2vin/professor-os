import numpy as np


def repulsive_force(position, obstacle, radius, k_rep,
                    influence_distance):
    offset = position - obstacle
    center_distance = np.linalg.norm(offset)

    if center_distance <= radius:
        return np.zeros(2), True

    clearance = center_distance - radius

    if clearance >= influence_distance:
        return np.zeros(2), False

    factor = k_rep * (
        1.0 / clearance - 1.0 / influence_distance
    )
    unit_away = offset / center_distance
    return factor * unit_away / (clearance ** 2), False


def total_force(position, goal, obstacles, obstacle_radius,
                k_att, k_rep, influence_distance):
    force = k_att * (goal - position)

    for obstacle in obstacles:
        obstacle_force, collision = repulsive_force(
            position, obstacle, obstacle_radius, k_rep,
            influence_distance
        )

        if collision:
            return np.zeros(2), True

        force += obstacle_force

    return force, False


def point_to_segment_distance(point, segment_start, segment_end):
    segment = segment_end - segment_start
    length_squared = np.dot(segment, segment)

    if length_squared == 0.0:
        return np.linalg.norm(point - segment_start)

    parameter = np.dot(point - segment_start, segment)
    parameter /= length_squared
    parameter = min(1.0, max(0.0, parameter))

    closest_point = segment_start + parameter * segment
    return np.linalg.norm(point - closest_point)


def segment_clearance(segment_start, segment_end, obstacles,
                      obstacle_radius):
    if len(obstacles) == 0:
        return float("inf")

    clearances = []

    for obstacle in obstacles:
        distance = point_to_segment_distance(
            obstacle, segment_start, segment_end
        )
        clearances.append(distance - obstacle_radius)

    return min(clearances)


def simulate(start, goal, obstacles, obstacle_radius=0.45,
             steps=500, step_size=0.08, k_att=1.0, k_rep=0.12,
             influence_distance=1.8, goal_tolerance=0.12,
             force_tolerance=1e-9):
    position = start.copy()
    path = [position.copy()]
    reason = "maximum_steps"

    for _ in range(steps):
        if np.linalg.norm(goal - position) <= goal_tolerance:
            reason = "reached_goal"
            break

        force, collision = total_force(
            position, goal, obstacles, obstacle_radius,
            k_att, k_rep, influence_distance
        )

        if collision:
            reason = "collision"
            break

        force_size = np.linalg.norm(force)

        if force_size < force_tolerance:
            reason = "near_zero_net_force"
            break

        candidate = position + step_size * force / force_size
        clearance = segment_clearance(
            position, candidate, obstacles, obstacle_radius
        )

        position = candidate
        path.append(position.copy())

        if clearance <= 0.0:
            reason = "collision"
            break

    else:
        reason = "maximum_steps"

    if (reason != "collision" and
            np.linalg.norm(goal - position) <= goal_tolerance):
        reason = "reached_goal"

    return np.array(path), reason


def minimum_clearance(path, obstacles, obstacle_radius):
    if len(obstacles) == 0:
        return float("inf")

    clearances = []

    for position in path:
        for obstacle in obstacles:
            clearances.append(
                np.linalg.norm(position - obstacle) - obstacle_radius
            )

    for index in range(len(path) - 1):
        clearances.append(
            segment_clearance(
                path[index], path[index + 1],
                obstacles, obstacle_radius
            )
        )

    return min(clearances)


start = np.array([0.8, 0.8], dtype=float)
goal = np.array([8.5, 8.0], dtype=float)

test_obstacles = np.array([
    [4.6, 4.4]
], dtype=float)

test_path, test_reason = simulate(
    start, goal, test_obstacles,
    obstacle_radius=0.45,
    k_rep=0.12,
    influence_distance=1.8
)

test_clearance = minimum_clearance(
    test_path, test_obstacles, 0.45
)

assert test_path.ndim == 2
assert test_path.shape[1] == 2
assert test_reason in (
    "reached_goal",
    "collision",
    "near_zero_net_force",
    "maximum_steps"
)

if test_reason == "collision":
    assert test_clearance <= 0.0

print("Direct-obstacle test:", test_reason)
print("Direct-obstacle minimum swept clearance:",
      round(test_clearance, 3), "m")
