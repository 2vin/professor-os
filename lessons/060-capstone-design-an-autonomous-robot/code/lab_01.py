from __future__ import print_function


def planned_energy(drive_power_w, computer_power_w, mission_time_s,
                   reserve_fraction):
    if drive_power_w < 0.0 or computer_power_w < 0.0:
        raise ValueError("power values must be nonnegative")
    if mission_time_s < 0.0:
        raise ValueError("mission_time_s must be nonnegative")
    if not 0.0 <= reserve_fraction < 1.0:
        raise ValueError("reserve_fraction must be in [0, 1)")

    E_used_j = (
        drive_power_w + computer_power_w
    ) * mission_time_s
    return E_used_j / (1.0 - reserve_fraction)


def simulate_mission(goal_m, obstacle_m, sensor_range_m,
                     speed_mps, time_step_s, sensor_valid=True,
                     battery_capacity_j=1200.0,
                     reserve_fraction=0.20,
                     drive_power_w=9.0,
                     computer_power_w=2.0,
                     max_steps=120):
    if goal_m <= 0.0:
        raise ValueError("goal_m must be positive")
    if obstacle_m <= 0.0:
        raise ValueError("obstacle_m must be positive")
    if sensor_range_m < 0.0:
        raise ValueError("sensor_range_m must be nonnegative")
    if speed_mps < 0.0:
        raise ValueError("speed_mps must be nonnegative")
    if time_step_s <= 0.0:
        raise ValueError("time_step_s must be positive")
    if speed_mps * time_step_s > sensor_range_m:
        raise ValueError(
            "one movement step must not exceed sensor range"
        )
    if battery_capacity_j < 0.0:
        raise ValueError("battery_capacity_j must be nonnegative")
    if drive_power_w < 0.0 or computer_power_w < 0.0:
        raise ValueError("power values must be nonnegative")
    if max_steps < 0:
        raise ValueError("max_steps must be nonnegative")
    if not 0.0 <= reserve_fraction < 1.0:
        raise ValueError("reserve_fraction must be in [0, 1)")

    position_m = 0.0
    E_start_j = battery_capacity_j
    E_used_j = 0.0
    steps = 0
    status = "RUNNING"
    E_step_j = (
        drive_power_w + computer_power_w
    ) * time_step_s
    E_reserve_j = reserve_fraction * E_start_j

    while status == "RUNNING" and steps < max_steps:
        distance_to_obstacle_m = obstacle_m - position_m

        # Safety has priority over goal completion.
        if not sensor_valid:
            status = "SAFE_STOP_SENSOR_FAILURE"
        elif distance_to_obstacle_m <= sensor_range_m:
            status = "SAFE_STOP_OBSTACLE"
        elif position_m >= goal_m:
            status = "MISSION_COMPLETE"
        else:
            predicted_E_used_j = E_used_j + E_step_j
            predicted_E_remaining_j = (
                E_start_j - predicted_E_used_j
            )

            if predicted_E_remaining_j < E_reserve_j:
                status = "SAFE_STOP_LOW_BATTERY"
            else:
                position_m = round(
                    position_m + speed_mps * time_step_s, 10
                )
                E_used_j = round(
                    E_used_j + E_step_j, 10
                )
                steps += 1

                if position_m >= goal_m:
                    status = "MISSION_COMPLETE"

    if status == "RUNNING":
        status = "TIMEOUT"

    E_remaining_j = E_start_j - E_used_j

    return {
        "position_m": position_m,
        "energy_used_j": E_used_j,
        "energy_remaining_j": round(E_remaining_j, 10),
        "reserve_limit_j": round(E_reserve_j, 10),
        "steps": steps,
        "status": status,
        # Reference-point clearance, not physical front clearance.
        "idealized_reference_clearance_m": round(
            obstacle_m - position_m, 10
        )
    }


def main():
    energy_plan_j = planned_energy(9.0, 2.0, 80.0, 0.20)
    assert abs(energy_plan_j - 1100.0) < 1e-9

    clear_run = simulate_mission(
        goal_m=2.0, obstacle_m=3.0, sensor_range_m=0.4,
        speed_mps=0.2, time_step_s=0.1
    )
    assert clear_run["status"] == "MISSION_COMPLETE"
    assert clear_run["steps"] == 100
    assert abs(clear_run["position_m"] - 2.0) < 1e-9
    assert clear_run["energy_remaining_j"] / 1200.0 >= 0.20

    obstacle_run = simulate_mission(
        goal_m=2.0, obstacle_m=1.5, sensor_range_m=0.4,
        speed_mps=0.2, time_step_s=0.1
    )
    assert obstacle_run["status"] == "SAFE_STOP_OBSTACLE"
    assert abs(obstacle_run["position_m"] - 1.1) < 1e-9
    assert abs(
        obstacle_run["idealized_reference_clearance_m"] - 0.4
    ) < 1e-9

    sensor_failure_run = simulate_mission(
        goal_m=2.0, obstacle_m=3.0, sensor_range_m=0.4,
        speed_mps=0.2, time_step_s=0.1, sensor_valid=False
    )
    assert sensor_failure_run["status"] == "SAFE_STOP_SENSOR_FAILURE"
    assert sensor_failure_run["steps"] == 0

    low_battery_run = simulate_mission(
        goal_m=2.0, obstacle_m=3.0, sensor_range_m=0.4,
        speed_mps=0.2, time_step_s=0.1,
        battery_capacity_j=120.0
    )
    assert low_battery_run["status"] == "SAFE_STOP_LOW_BATTERY"
    assert low_battery_run["steps"] == 87
    assert abs(low_battery_run["energy_remaining_j"] - 24.3) < 1e-9
    assert (
        low_battery_run["energy_remaining_j"]
        >= low_battery_run["reserve_limit_j"]
    )

    timeout_run = simulate_mission(
        goal_m=3.0, obstacle_m=4.0, sensor_range_m=0.4,
        speed_mps=0.2, time_step_s=0.1, max_steps=100
    )
    assert timeout_run["status"] == "TIMEOUT"
    assert timeout_run["steps"] == 100

    validation_errors = [
        ({"goal_m": -1.0}, "goal"),
        ({"speed_mps": -0.1}, "speed"),
        ({"time_step_s": -0.1}, "time"),
        ({"obstacle_m": -1.0}, "obstacle"),
        ({"speed_mps": 5.0}, "step-range")
    ]
    for changes, label in validation_errors:
        arguments = {
            "goal_m": 2.0,
            "obstacle_m": 3.0,
            "sensor_range_m": 0.4,
            "speed_mps": 0.2,
            "time_step_s": 0.1
        }
        arguments.update(changes)
        try:
            simulate_mission(**arguments)
        except ValueError:
            pass
        else:
            raise AssertionError(
                "expected validation error for " + label
            )

    print("Energy plan:", energy_plan_j, "J")
    print("Clear run:", clear_run)
    print("Obstacle run:", obstacle_run)
    print("Sensor failure run:", sensor_failure_run)
    print("Low-battery run:", low_battery_run)
    print("Timeout run:", timeout_run)
    print("Movement-step constraint check passed.")
    print("Input validation checks passed.")
    print("All capstone checks passed.")


if __name__ == "__main__":
    main()
