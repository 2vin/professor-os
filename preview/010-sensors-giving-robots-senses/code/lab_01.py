import math
import matplotlib.pyplot as plt

# Measurements are in metres.
known_distance = 0.50

reference_readings = [0.56, 0.54, 0.55, 0.57, 0.53]
test_readings = [1.08, 1.04, 1.06, 1.07, 1.05]

def average(values):
    """Return the arithmetic mean of a non-empty list of numbers."""
    return sum(values) / len(values)

# Estimate a constant sensor bias using the known reference.
reference_average = average(reference_readings)
bias = reference_average - known_distance

# Correct every later reading by subtracting the estimated bias.
corrected_readings = [reading - bias for reading in test_readings]

raw_average = average(test_readings)
corrected_average = average(corrected_readings)

print("Reference average: {:.2f} m".format(reference_average))
print("Estimated bias: {:.2f} m".format(bias))
print("Raw test average: {:.2f} m".format(raw_average))
print("Corrected test average: {:.2f} m".format(corrected_average))
print("Corrected readings:", ["{:.2f} m".format(x) for x in corrected_readings])

# Floating-point arithmetic can represent decimal values approximately,
# so compare calculated values with a small tolerance.
assert math.isclose(reference_average, 0.55)
assert math.isclose(bias, 0.05)
assert math.isclose(raw_average, 1.06)
expected_corrected = [1.03, 0.99, 1.01, 1.02, 1.00]
assert all(
    math.isclose(actual, expected)
    for actual, expected in zip(corrected_readings, expected_corrected)
)
assert math.isclose(corrected_average, 1.01)

# Plot each test reading before and after calibration.
trial_numbers = list(range(1, len(test_readings) + 1))

plt.plot(trial_numbers, test_readings, "o-", label="Raw readings")
plt.plot(trial_numbers, corrected_readings, "s-", label="Corrected readings")
plt.axhline(1.00, color="black", linestyle="--", label="Reference: 1.00 m")

plt.xlabel("Trial number")
plt.ylabel("Distance (m)")
plt.title("RoboRover Sensor Calibration")
plt.xticks(trial_numbers)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
