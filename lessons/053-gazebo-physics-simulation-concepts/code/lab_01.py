import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

WORLD_WIDTH = 10.0
WORLD_HEIGHT = 6.0

ROVER_RADIUS = 0.25
ROVER_X_START = 1.0
ROVER_Y_START = 3.0

OBSTACLE_LEFT = 4.0
OBSTACLE_RIGHT = 5.0
OBSTACLE_BOTTOM = 2.0
OBSTACLE_TOP = 4.0

SPEED = 0.55
TIME_STEP = 0.20
NUMBER_OF_STEPS = 40
SENSOR_MAX_RANGE = 3.0


def circle_rectangle_overlap(cx, cy, radius,
                             left, right, bottom, top):
    """Return True only when a circle overlaps a rectangle.

    Exact geometric tangency is accepted as non-overlap by this
    teaching model, so the final comparison is strict: <.
    """
    closest_x = max(left, min(cx, right))
    closest_y = max(bottom, min(cy, top))

    dx = cx - closest_x
    dy = cy - closest_y
    distance_squared = dx * dx + dy * dy

    return distance_squared < radius * radius


def forward_sensor_distance(x, y):
    """Return an ideal forward measurement in metres."""
    if OBSTACLE_BOTTOM <= y <= OBSTACLE_TOP and x < OBSTACLE_LEFT:
        distance = OBSTACLE_LEFT - x
        return min(distance, SENSOR_MAX_RANGE)

    return SENSOR_MAX_RANGE


def run_simulation():
    x = ROVER_X_START
    y = ROVER_Y_START
    movement_per_step = SPEED * TIME_STEP

    path = [(x, y)]
    sensor_readings = []
    accepted_moves = 0
    blocked_moves = 0

    for step in range(NUMBER_OF_STEPS):
        sensor_reading = forward_sensor_distance(x, y)
        sensor_readings.append(sensor_reading)

        proposed_x = x + movement_per_step
        proposed_y = y

        overlaps_obstacle = circle_rectangle_overlap(
            proposed_x,
            proposed_y,
            ROVER_RADIUS,
            OBSTACLE_LEFT,
            OBSTACLE_RIGHT,
            OBSTACLE_BOTTOM,
            OBSTACLE_TOP
        )

        if overlaps_obstacle:
            blocked_moves += 1
        else:
            x = proposed_x
            y = proposed_y
            accepted_moves += 1

        path.append((x, y))

    final_sensor_reading = forward_sensor_distance(x, y)

    print("Final rover center: x={:.2f} m, y={:.2f} m".format(x, y))
    print("Accepted moves:", accepted_moves)
    print("Blocked moves:", blocked_moves)
    print("Final forward sensor reading: {:.2f} m".format(
        final_sensor_reading
    ))

    # These checks verify the exact claims made by this program.
    assert accepted_moves == 25
    assert blocked_moves == 15
    assert round(x, 2) == 3.75
    assert round(y, 2) == 3.00
    assert round(final_sensor_reading, 2) == 0.25
    assert len(path) == NUMBER_OF_STEPS + 1
    assert len(sensor_readings) == NUMBER_OF_STEPS

    figure, axis = plt.subplots(figsize=(10, 6))
    axis.set_xlim(0, WORLD_WIDTH)
    axis.set_ylim(0, WORLD_HEIGHT)
    axis.set_aspect("equal")
    axis.set_xlabel("x position (m)")
    axis.set_ylabel("y position (m)")
    axis.set_title("RoboRover: simulated world, overlap test, and sensor")

    obstacle_width = OBSTACLE_RIGHT - OBSTACLE_LEFT
    obstacle_height = OBSTACLE_TOP - OBSTACLE_BOTTOM

    obstacle = Rectangle(
        (OBSTACLE_LEFT, OBSTACLE_BOTTOM),
        obstacle_width,
        obstacle_height,
        facecolor="steelblue",
        edgecolor="black",
        label="collision obstacle"
    )
    axis.add_patch(obstacle)

    path_x = [point[0] for point in path]
    path_y = [point[1] for point in path]
    axis.plot(path_x, path_y, color="darkgreen", label="rover path")

    rover = Circle(
        (x, y),
        ROVER_RADIUS,
        facecolor="limegreen",
        edgecolor="black",
        label="RoboRover collision body"
    )
    axis.add_patch(rover)

    sensor_end_x = x + final_sensor_reading
    axis.plot(
        [x, sensor_end_x],
        [y, y],
        color="darkorange",
        linewidth=3,
        label="forward sensor ray"
    )

    axis.legend(loc="upper left")
    axis.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    run_simulation()
