def run_rover():
    sensor_readings_cm = [72.0, 40.0, 18.0, 55.0]

    battery_points = 30.0
    drive_cost_points = 4.0
    slow_cost_points = 2.0
    clean_cost_points = 1.0

    drive_count = 0
    clean_count = 0

    for cycle_number in range(1, len(sensor_readings_cm) + 1):
        distance_cm = sensor_readings_cm[cycle_number - 1]

        if distance_cm >= 50.0:
            action = "drive"
            battery_points = battery_points - drive_cost_points
            drive_count = drive_count + 1
        elif distance_cm >= 20.0:
            action = "slow"
            battery_points = battery_points - slow_cost_points
        else:
            action = "clean"
            battery_points = battery_points - clean_cost_points
            clean_count = clean_count + 1

        print(
            "Cycle {}: sensor = {:.1f} cm, action = {}, "
            "battery = {:.1f} percentage points".format(
                cycle_number, distance_cm, action, battery_points
            )
        )

    print("Final battery: {:.1f} percentage points".format(battery_points))
    print("Drive actions:", drive_count)
    print("Clean actions:", clean_count)

    # Executable checks verify the numerical claims for this input.
    assert round(battery_points, 1) == 19.0
    assert drive_count == 2
    assert clean_count == 1


if __name__ == "__main__":
    run_rover()
