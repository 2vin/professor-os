import random
import matplotlib.pyplot as plt


def weighted_filter(readings, alpha):
    """Return filtered readings using first-order exponential smoothing."""
    if not 0.0 <= alpha <= 1.0:
        raise ValueError("alpha must be between 0 and 1")

    if not readings:
        return []

    filtered = [readings[0]]

    for reading in readings[1:]:
        previous = filtered[-1]
        new_value = alpha * reading + (1.0 - alpha) * previous
        filtered.append(new_value)

    return filtered


# Part 1: verify the worked numerical example.
example_readings = [98.0, 103.0, 101.0, 99.0, 100.0]
example_average = sum(example_readings) / len(example_readings)

assert abs(example_average - 100.2) < 1e-9

example_filtered = weighted_filter(example_readings, 0.4)

# The first filtered value is the first raw reading.
assert abs(example_filtered[0] - 98.0) < 1e-9

# These assertions verify all five filtering calculations.
expected_filtered = [98.0, 100.0, 100.4, 99.84, 99.904]
for actual, expected in zip(example_filtered, expected_filtered):
    assert abs(actual - expected) < 1e-9

print("Example average:", example_average, "cm")
print("Example filtered values:",
      [round(value, 3) for value in example_filtered])

# Part 2: simulate a sensor measuring a fixed 100 cm distance.
random.seed(22)

true_distance = 100.0
number_of_readings = 80
noise_standard_deviation = 4.0
alpha = 0.25

times = list(range(number_of_readings))
raw_readings = []

for unused_index in times:
    noise = random.gauss(0.0, noise_standard_deviation)
    raw_readings.append(true_distance + noise)

filtered_readings = weighted_filter(raw_readings, alpha)

assert len(raw_readings) == number_of_readings
assert len(filtered_readings) == number_of_readings

print("Simulated readings:", len(raw_readings))
print("True distance:", true_distance, "cm")
print("Filter weight alpha:", alpha)

# Part 3: draw the result.
plt.figure(figsize=(10, 5))
plt.plot(times, raw_readings, "o-", markersize=3,
         alpha=0.45, label="raw sensor readings")
plt.plot(times, filtered_readings, linewidth=2,
         label="weighted filtered estimate")
plt.axhline(true_distance, color="black", linestyle="--",
            label="true distance")

plt.xlabel("Reading number")
plt.ylabel("Distance (cm)")
plt.title("RoboRover: noisy distance measurements")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
