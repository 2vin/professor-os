import math
import matplotlib.pyplot as plt


LINE_WIDTH = 0.020
SENSOR_OFFSET = 0.045
FORWARD_STEP = 0.020
TURN_STEP = 0.012
STEPS = 300


def calibrate_threshold(floor_readings, line_readings):
    if not floor_readings or not line_readings:
        raise ValueError("Both calibration sample sets must be non-empty.")

    floor_mean = sum(floor_readings) / float(len(floor_readings))
    line_mean = sum(line_readings) / float(len(line_readings))

    if floor_mean <= line_mean:
        raise ValueError("Expected floor readings to exceed line readings.")

    return (floor_mean + line_mean) / 2.0


def line_position(forward_distance):
    return 0.08 * math.sin(0.8 * forward_distance)


def sensor_reading(sensor_x, line_x):
    if abs(sensor_x - line_x) <= LINE_WIDTH / 2.0:
        return 200
    return 800


def detects_line(reading, threshold):
    return reading < threshold


def choose_steering(left, center, right, previous_steering):
    if center:
        return 0
    if left and right:
        return 0
    if left:
        return -1
    if right:
        return 1
    return previous_steering


def main():
    floor_samples = [775, 780, 785]
    line_samples = [215, 220, 225]
    threshold = calibrate_threshold(floor_samples, line_samples)

    assert math.isclose(threshold, 500.0, abs_tol=1e-12)

    robot_x = 0.040
    previous_steering = -1

    forward_positions = []
    robot_positions = []
    line_positions = []
    steering_commands = []

    for step in range(STEPS):
        forward_distance = step * FORWARD_STEP
        line_x = line_position(forward_distance)

        left_reading = sensor_reading(
            robot_x - SENSOR_OFFSET, line_x
        )
        center_reading = sensor_reading(robot_x, line_x)
        right_reading = sensor_reading(
            robot_x + SENSOR_OFFSET, line_x
        )

        left_detected = detects_line(left_reading, threshold)
        center_detected = detects_line(center_reading, threshold)
        right_detected = detects_line(right_reading, threshold)

        steering = choose_steering(
            left_detected,
            center_detected,
            right_detected,
            previous_steering
        )

        robot_x += steering * TURN_STEP
        previous_steering = steering

        forward_positions.append(forward_distance)
        robot_positions.append(robot_x)
        line_positions.append(line_x)
        steering_commands.append(steering)

    tracking_errors = [
        abs(robot_value - line_value)
        for robot_value, line_value
        in zip(robot_positions, line_positions)
    ]
    mean_absolute_error = (
        sum(tracking_errors) / float(len(tracking_errors))
    )
    maximum_error = max(tracking_errors)

    assert len(forward_positions) == STEPS
    assert len(robot_positions) == STEPS
    assert len(line_positions) == STEPS
    assert len(steering_commands) == STEPS
    assert all(math.isfinite(value) for value in robot_positions)
    assert set(steering_commands).issubset(set([-1, 0, 1]))
    assert all(math.isfinite(value) for value in tracking_errors)
    assert mean_absolute_error >= 0.0
    assert maximum_error >= mean_absolute_error

    assert steering_commands[:3] == [-1, -1, -1]
    assert math.isclose(robot_positions[0], 0.028, abs_tol=1e-12)
    assert math.isclose(robot_positions[1], 0.016, abs_tol=1e-12)
    assert math.isclose(robot_positions[2], 0.004, abs_tol=1e-12)

    print("Calibration threshold:", threshold)
    print("Simulation completed.")
    print("Recorded positions:", len(robot_positions))
    print("First three steering commands:", steering_commands[:3])
    print("First three robot positions:",
          [round(value, 3) for value in robot_positions[:3]])
    print("Mean absolute tracking error (m):",
          round(mean_absolute_error, 4))
    print("Maximum tracking error (m):",
          round(maximum_error, 4))
    print("Allowed steering commands:", sorted(set(steering_commands)))

    plt.figure(figsize=(9, 5))
    plt.plot(
        forward_positions,
        line_positions,
        label="dark line",
        linewidth=2
    )
    plt.plot(
        forward_positions,
        robot_positions,
        label="RoboRover centre",
        linewidth=2
    )
    plt.xlabel("Forward distance (m)")
    plt.ylabel("Sideways position (m)")
    plt.title("Virtual three-sensor line follower")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
