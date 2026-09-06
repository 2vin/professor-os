def calibrate_threshold_high_dark(floor_readings, line_readings):
    if not floor_readings or not line_readings:
        raise ValueError("Calibration samples must not be empty.")

    floor_mean = sum(floor_readings) / float(len(floor_readings))
    line_mean = sum(line_readings) / float(len(line_readings))

    if line_mean <= floor_mean:
        raise ValueError("Expected line readings to exceed floor readings.")

    return (floor_mean + line_mean) / 2.0
