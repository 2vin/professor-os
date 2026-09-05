import math
import matplotlib.pyplot as plt


WHEEL_RADIUS_M = 0.05
TICKS_PER_REV = 360.0
TRACK_WIDTH_M = 0.16


def ticks_to_distance(ticks):
    """Convert encoder ticks to signed wheel distance in meters."""
    return (ticks / TICKS_PER_REV) * 2.0 * math.pi * WHEEL_RADIUS_M


def update_pose(x, y, heading, left_ticks, right_ticks):
    """
    Update a differential-drive robot pose.

    x and y are meters.
    heading is radians, measured counterclockwise from the positive x-axis.
    """
    left_distance = ticks_to_distance(left_ticks)
    right_distance = ticks_to_distance(right_ticks)

    forward_distance = (left_distance + right_distance) / 2.0
    heading_change = (right_distance - left_distance) / TRACK_WIDTH_M

    # Use the midpoint heading for this short motion interval.
    midpoint_heading = heading + heading_change / 2.0

    new_x = x + forward_distance * math.cos(midpoint_heading)
    new_y = y + forward_distance * math.sin(midpoint_heading)
    new_heading = heading + heading_change

    return new_x, new_y, new_heading


def main():
    # Each tuple contains (left encoder ticks, right encoder ticks).
    motion_steps = [
        (360, 360),    # One wheel revolution: straight forward.
        (90, -90),     # Rotate in place.
        (180, 180)     # Half a revolution: forward in the new direction.
    ]

    x = 0.0
    y = 0.0
    heading = 0.0

    path_x = [x]
    path_y = [y]

    for left_ticks, right_ticks in motion_steps:
        x, y, heading = update_pose(
            x, y, heading, left_ticks, right_ticks
        )
        path_x.append(x)
        path_y.append(y)

    expected_distance_first_step = 2.0 * math.pi * WHEEL_RADIUS_M
    expected_turn = (
        -2.0 * ticks_to_distance(90) / TRACK_WIDTH_M
    )
    expected_final_x = (
        expected_distance_first_step
        + 0.5 * expected_distance_first_step * math.cos(expected_turn)
    )
    expected_final_y = (
        0.5 * expected_distance_first_step * math.sin(expected_turn)
    )

    # Executable checks for the numerical claims.
    assert math.isclose(
        path_x[1], expected_distance_first_step, rel_tol=1e-9
    )
    assert math.isclose(path_y[1], 0.0, abs_tol=1e-12)
    assert math.isclose(heading, expected_turn, rel_tol=1e-9)
    assert math.isclose(x, expected_final_x, rel_tol=1e-9)
    assert math.isclose(y, expected_final_y, rel_tol=1e-9)

    print("First straight distance: {:.6f} m".format(path_x[1]))
    print("Final estimated pose: x={:.6f} m, y={:.6f} m, heading={:.6f} rad".format(
        x, y, heading
    ))
    print("All odometry checks passed.")

    plt.figure(figsize=(7, 5))
    plt.plot(path_x, path_y, "o-", label="estimated RoboRover path")
    plt.scatter([0.0], [0.0], marker="s", s=80, label="start")
    plt.xlabel("x position (m)")
    plt.ylabel("y position (m)")
    plt.title("Encoder Odometry Simulation")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
