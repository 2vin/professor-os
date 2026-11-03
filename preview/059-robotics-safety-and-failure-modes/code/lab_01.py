# Python 3.7-compatible RoboRover safety monitor simulation

import math


def safety_monitor(speed_command, sensor_a, sensor_b, sensor_time,
                   current_time, maximum_sensor_age, obstacle_limit,
                   maximum_speed, disagreement_limit, stop_latched):
    """Return (allowed_speed, new_latch, reason)."""

    values = (
        speed_command, sensor_a, sensor_b, sensor_time, current_time,
        maximum_sensor_age, obstacle_limit, maximum_speed,
        disagreement_limit
    )
    if not all(math.isfinite(value) for value in values):
        return 0.0, True, "non-finite value"

    if (maximum_sensor_age < 0.0 or obstacle_limit < 0.0 or
            maximum_speed < 0.0 or disagreement_limit < 0.0):
        return 0.0, True, "invalid safety parameter"

    if stop_latched:
        return 0.0, True, "latched stop"

    if speed_command < 0.0:
        return 0.0, True, "negative command rejected"

    allowed_speed = min(speed_command, maximum_speed)
    reason = "accepted"
    if allowed_speed < speed_command:
        reason = "speed limited"

    sensor_age = current_time - sensor_time
    if sensor_age < 0.0 or sensor_age > maximum_sensor_age:
        return 0.0, True, "stale sensor data"

    if sensor_a < 0.10 or sensor_b < 0.10:
        return 0.0, True, "sensor below valid range"

    if sensor_a > 5.0 or sensor_b > 5.0:
        return 0.0, True, "sensor above valid range"

    # Check disagreement before averaging.
    if abs(sensor_a - sensor_b) > disagreement_limit:
        return 0.0, True, "sensor disagreement"

    # The obstacle check uses the average only after agreement passes.
    # This simplified check ignores robot geometry, sensor offset,
    # uncertainty, and braking distance.
    average_distance = (sensor_a + sensor_b) / 2.0
    if average_distance < obstacle_limit:
        return 0.0, True, "obstacle too close"

    return allowed_speed, False, reason


def main():
    time_step = 0.10
    maximum_sensor_age = 0.15
    obstacle_limit = 0.80
    maximum_speed = 0.60
    disagreement_limit = 0.15

    commands = [0.40, 0.50, 0.70, 0.80, 0.60, 0.40, 0.30, 0.00]
    sensor_a = [2.00, 1.95, 1.90, 1.20, 1.10, 1.00, 0.95, 0.90]
    sensor_b = [2.05, 1.98, 1.88, 0.79, 1.12, 1.02, 0.97, 0.91]
    sensor_times = [0.00, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70]

    stop_latched = False
    idealized_commanded_distance = 0.0
    speeds = []
    reasons = []

    for step in range(len(commands)):
        current_time = step * time_step
        allowed, stop_latched, reason = safety_monitor(
            commands[step], sensor_a[step], sensor_b[step],
            sensor_times[step], current_time, maximum_sensor_age,
            obstacle_limit, maximum_speed, disagreement_limit,
            stop_latched
        )

        # Teaching-model integration: commanded speed x time step.
        # This is not measured travel or a stopping-distance calculation.
        idealized_commanded_distance += allowed * time_step
        speeds.append(allowed)
        reasons.append(reason)

        print("step={0}, command={1:.2f}, allowed={2:.2f}, reason={3}".format(
            step, commands[step], allowed, reason
        ))

    print("idealized commanded distance={0:.2f} m".format(
        idealized_commanded_distance
    ))

    assert speeds == [0.40, 0.50, 0.60, 0.00,
                      0.00, 0.00, 0.00, 0.00]
    assert reasons[2] == "speed limited"
    assert reasons[3] == "sensor disagreement"
    assert stop_latched is True
    assert abs(idealized_commanded_distance - 0.15) < 1e-9

    nan_result = safety_monitor(
        0.40, float("nan"), 1.00, 0.00, 0.00,
        maximum_sensor_age, obstacle_limit, maximum_speed,
        disagreement_limit, False
    )
    infinity_result = safety_monitor(
        0.40, 1.00, 1.00, 0.00, float("inf"),
        maximum_sensor_age, obstacle_limit, maximum_speed,
        disagreement_limit, False
    )
    assert nan_result == (0.0, True, "non-finite value")
    assert infinity_result == (0.0, True, "non-finite value")

    # Additional executable checks for negative commands and stale data.
    negative_result = safety_monitor(
        -0.10, 1.00, 1.00, 0.00, 0.00,
        maximum_sensor_age, obstacle_limit, maximum_speed,
        disagreement_limit, False
    )
    stale_result = safety_monitor(
        0.40, 1.00, 1.00, 0.00, 0.20,
        maximum_sensor_age, obstacle_limit, maximum_speed,
        disagreement_limit, False
    )
    assert negative_result == (0.0, True, "negative command rejected")
    assert stale_result == (0.0, True, "stale sensor data")

    print("All safety checks passed.")


if __name__ == "__main__":
    main()
