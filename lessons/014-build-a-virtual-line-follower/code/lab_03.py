import math


def calibrate_threshold(floor_readings, line_readings):
    if not floor_readings or not line_readings:
        raise ValueError("Calibration samples must not be empty.")

    floor_mean = sum(floor_readings) / float(len(floor_readings))
    line_mean = sum(line_readings) / float(len(line_readings))

    if floor_mean <= line_mean:
        raise ValueError("Expected floor readings to exceed line readings.")

    return (floor_mean + line_mean) / 2.0


floor_samples = [775, 780, 785]
line_samples = [215, 220, 225]
threshold = calibrate_threshold(floor_samples, line_samples)

assert math.isclose(threshold, 500.0, abs_tol=1e-12)
print(threshold)
