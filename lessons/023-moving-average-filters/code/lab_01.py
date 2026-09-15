import matplotlib.pyplot as plt


def moving_average(values, window_size):
    """Return a trailing moving average using available startup values."""
    if window_size <= 0:
        raise ValueError("window_size must be positive")

    filtered = []

    for index in range(len(values)):
        start = max(0, index - window_size + 1)
        window = values[start:index + 1]
        average = sum(window) / len(window)
        filtered.append(average)

    return filtered


# Simulated distance measurements from RoboRover's sensor.
# The intended wall distance is near 100 cm, with noise and one large spike.
raw_distance_cm = [
    100, 104, 96, 101, 130, 99,
    102, 98, 100, 97, 103, 101
]

WINDOW_SIZE = 3
filtered_distance_cm = moving_average(raw_distance_cm, WINDOW_SIZE)

# Executable checks for the worked idea.
assert filtered_distance_cm[0] == 100.0
assert filtered_distance_cm[1] == 102.0
assert filtered_distance_cm[2] == 100.0
assert filtered_distance_cm[4] == 109.0
assert len(filtered_distance_cm) == len(raw_distance_cm)

print("Raw distance at reading 5: {:.2f} cm".format(raw_distance_cm[4]))
print("Filtered distance at reading 5: {:.2f} cm".format(
    filtered_distance_cm[4]
))
print("All moving-average checks passed.")

sample_numbers = list(range(1, len(raw_distance_cm) + 1))

plt.figure(figsize=(9, 5))
plt.plot(
    sample_numbers,
    raw_distance_cm,
    "o-",
    label="Raw sensor distance"
)
plt.plot(
    sample_numbers,
    filtered_distance_cm,
    "s-",
    label="3-sample moving average"
)
plt.axhline(
    100,
    color="gray",
    linestyle="--",
    label="Reference distance: 100 cm"
)

plt.title("RoboRover Distance Sensor Smoothing")
plt.xlabel("Sensor reading number")
plt.ylabel("Distance (cm)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
