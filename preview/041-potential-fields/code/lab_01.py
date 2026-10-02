import math
import numpy as np
import matplotlib.pyplot as plt


def attractive_force(position, goal, k_att):
    """Return attraction toward the goal."""
    return k_att * (goal - position)


def repulsive_force(position, obstacle, radius, k_rep,
                    influence_distance):
    """
    Return (force, collision).

    Obstacles are circular. The force uses clearance from the
    obstacle boundary, not distance from the obstacle center.
    """
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
    force = factor * unit_away / (clearance ** 2)
    return force, False


def total_force(position, goal, obstacles, obstacle_radius,
                k_att, k_rep, influence_distance):
    force = attractive_force(position, goal, k_att)

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
    """Return the minimum distance from a point to a line segment."""
    segment = segment_end - segment_start
    segment_length_squared = np.dot(segment, segment)

    if segment_length_squared == 0.0:
        return np.linalg.norm(point - segment_start)

    projection = np.dot(point - segment_start, segment)
    parameter = projection / segment_length_squared
    parameter = min(1.0, max(0.0, parameter))

    closest_point = segment_start + parameter * segment
    return np.linalg.norm(point - closest_point)


def segment_clearance(segment_start, segment_end, obstacles,
                      obstacle_radius):
    """
    Return the minimum boundary clearance along one motion segment.

    A value <= 0 means that the segment intersects or touches a
    modeled circular obstacle.
    """
    if len(obstacles) == 0:
        return float("inf")

    clearances = []

    for obstacle in obstacles:
        center_distance = point_to_segment_distance(
            obstacle, segment_start, segment_end
        )
        clearances.append(center_distance - obstacle_radius)

    return min(clearances)


def minimum_clearance(path, obstacles, obstacle_radius):
    """
    Return the smallest boundary clearance along the swept path.

    This checks both path points and every segment between consecutive
    path points, so a large step cannot hide an intersection.
    """
    if len(obstacles) == 0:
        return float("inf")

    clearances = []

    for position in path:
        for obstacle in obstacles:
            center_distance = np.linalg.norm(position - obstacle)
            clearances.append(center_distance - obstacle_radius)

    for index in range(len(path) - 1):
        clearances.append(
            segment_clearance(
                path[index], path[index + 1],
                obstacles, obstacle_radius
            )
        )

    return min(clearances)


def simulate(start, goal, obstacles, obstacle_radius=0.45,
             steps=500, step_size=0.08, k_att=1.0, k_rep=0.12,
             influence_distance=1.8, goal_tolerance=0.12,
             force_tolerance=1e-9):
    position = start.copy()
    path = [position.copy()]
    termination_reason = "maximum_steps"

    for _ in range(steps):
        if np.linalg.norm(goal - position) <= goal_tolerance:
            termination_reason = "reached_goal"
            break

        force, collision = total_force(
            position, goal, obstacles, obstacle_radius,
            k_att, k_rep, influence_distance
        )

        if collision:
            termination_reason = "collision"
            break

        force_size = np.linalg.norm(force)

        # A near-zero force is treated as a local-minimum or
        # stalled-controller condition. Normalizing such a vector
        # would amplify numerical noise into an arbitrary heading.
        if force_size < force_tolerance:
            termination_reason = "near_zero_net_force"
            break

        # Kinematic controller:
        # force magnitude sets direction, while step_size sets
        # the distance traveled during this update.
        direction = force / force_size
        candidate = position + step_size * direction

        # Swept collision check: test the complete segment from the
        # current position to the candidate, not only the endpoint.
        candidate_clearance = segment_clearance(
            position, candidate, obstacles, obstacle_radius
        )

        position = candidate
        path.append(position.copy())

        if candidate_clearance <= 0.0:
            termination_reason = "collision"
            break

    else:
        termination_reason = "maximum_steps"

    if (termination_reason != "collision" and
            np.linalg.norm(goal - position) <= goal_tolerance):
        termination_reason = "reached_goal"

    return np.array(path), termination_reason


def field_vector(position, goal, obstacles, obstacle_radius,
                 k_att, k_rep, influence_distance):
    """Return a field vector, with zero inside a modeled obstacle."""
    force, collision = total_force(
        position, goal, obstacles, obstacle_radius,
        k_att, k_rep, influence_distance
    )

    if collision:
        return np.zeros(2)

    return force


def draw_circle(axis, center, radius, color, label=None):
    angles = np.linspace(0.0, 2.0 * math.pi, 100)
    x_values = center[0] + radius * np.cos(angles)
    y_values = center[1] + radius * np.sin(angles)
    axis.plot(
        x_values, y_values, color=color, linewidth=2.0,
        label=label
    )


def draw_vector_field(axis, goal, obstacles, obstacle_radius,
                      k_att, k_rep, influence_distance):
    x_values = np.linspace(0.4, 9.0, 20)
    y_values = np.linspace(0.4, 9.0, 20)
    grid_x, grid_y = np.meshgrid(x_values, y_values)

    vector_x = np.zeros_like(grid_x)
    vector_y = np.zeros_like(grid_y)

    for row in range(grid_x.shape[0]):
        for column in range(grid_x.shape[1]):
            position = np.array([
                grid_x[row, column],
                grid_y[row, column]
            ])

            vector = field_vector(
                position, goal, obstacles, obstacle_radius,
                k_att, k_rep, influence_distance
            )

            magnitude = np.linalg.norm(vector)

            if magnitude > 0.0:
                # Normalize for readable arrows. This is a display
                # choice and does not change the simulation. Arrow
                # lengths therefore do not represent force magnitude.
                vector_x[row, column] = vector[0] / magnitude
                vector_y[row, column] = vector[1] / magnitude

    axis.quiver(
        grid_x, grid_y, vector_x, vector_y,
        color="gray", alpha=0.55, angles="xy",
        scale_units="xy", scale=9.0, width=0.002
    )


def main():
    start = np.array([0.8, 0.8], dtype=float)
    goal = np.array([8.5, 8.0], dtype=float)

    obstacles = np.array([
        [3.2, 3.4],
        [5.3, 5.4],
        [5.5, 2.5]
    ], dtype=float)

    obstacle_radius = 0.45

    path, termination_reason = simulate(
        start, goal, obstacles,
        obstacle_radius=obstacle_radius
    )

    assert path.ndim == 2
    assert path.shape[1] == 2
    assert len(path) >= 1
    assert termination_reason in (
        "reached_goal",
        "collision",
        "near_zero_net_force",
        "maximum_steps"
    )

    smallest_clearance = minimum_clearance(
        path, obstacles, obstacle_radius
    )

    # A reported collision must agree with the swept-path clearance.
    if termination_reason == "collision":
        assert smallest_clearance <= 0.0

    print("Simulation steps:", len(path) - 1)
    print("Termination reason:", termination_reason)
    print("Minimum swept boundary clearance (m):",
          round(smallest_clearance, 3))

    figure, axis = plt.subplots(figsize=(7, 7))

    draw_vector_field(
        axis, goal, obstacles, obstacle_radius,
        k_att=1.0, k_rep=0.12, influence_distance=1.8
    )

    axis.plot(
        path[:, 0], path[:, 1], color="blue",
        linewidth=2.0, label="RoboRover path"
    )
    axis.scatter(
        start[0], start[1], color="black", s=60,
        label="Start", zorder=3
    )
    axis.scatter(
        goal[0], goal[1], color="green", s=90,
        label="Goal", zorder=3
    )

    for index, obstacle in enumerate(obstacles):
        label = "Modeled obstacle" if index == 0 else None
        draw_circle(
            axis, obstacle, obstacle_radius,
            color="red", label=label
        )

    axis.set_xlim(0.0, 9.5)
    axis.set_ylim(0.0, 9.5)
    axis.set_aspect("equal", adjustable="box")
    axis.set_xlabel("x position (m)")
    axis.set_ylabel("y position (m)")
    axis.set_title("RoboRover: Potential-Field Vector Field and Path")
    axis.grid(True, alpha=0.3)
    axis.legend()
    plt.show()


if __name__ == "__main__":
    main()
