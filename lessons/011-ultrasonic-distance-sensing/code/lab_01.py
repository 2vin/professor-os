import math
import matplotlib.pyplot as plt

# Approximate speed of sound in air at room temperature.
SPEED_OF_SOUND_M_PER_S = 343.0

# RoboRover's actual distance from the wall at several moments.
true_distances = [2.00, 1.50, 1.00, 0.75, 0.50, 0.25]

# Small measurement offsets imitate sensor noise or calibration error.
measurement_offsets = [0.00, 0.03, -0.02, 0.02, -0.03, 0.03]

# Convert the actual one-way distance into a round-trip echo time.
echo_times = []
for distance in true_distances:
    time_seconds = (2.0 * distance) / SPEED_OF_SOUND_M_PER_S
    echo_times.append(time_seconds)

# Convert each simulated echo time back into an estimated range.
measured_distances = []
for index in range(len(echo_times)):
    estimated_range = (
        SPEED_OF_SOUND_M_PER_S * echo_times[index] / 2.0
        + measurement_offsets[index]
    )
    measured_distances.append(estimated_range)

# RoboRover stops if its estimated range is below this threshold.
STOP_DISTANCE_M = 0.60
actions = []
for distance in measured_distances:
    if distance < STOP_DISTANCE_M:
        actions.append("STOP")
    else:
        actions.append("GO")

# Executable checks verify the important numerical claims.
assert math.isclose(echo_times[0], 4.0 / 343.0, rel_tol=1e-12)
assert math.isclose(measured_distances[0], 2.00, rel_tol=1e-12)
assert math.isclose(measured_distances[1], 1.53, rel_tol=1e-12)
assert actions.count("STOP") == 2
assert actions[-1] == "STOP"

print("Distance (m) | Echo time (ms) | Estimated range (m) | Action")
for index in range(len(true_distances)):
    print(
        "{:12.2f} | {:14.3f} | {:19.2f} | {}".format(
            true_distances[index],
            echo_times[index] * 1000.0,
            measured_distances[index],
            actions[index]
        )
    )

print("All numerical checks passed.")
print("STOP actions:", actions.count("STOP"))

# Plot actual and estimated distances.
time_step_numbers = list(range(1, len(true_distances) + 1))

plt.plot(
    time_step_numbers,
    true_distances,
    marker="o",
    label="Actual distance"
)
plt.plot(
    time_step_numbers,
    measured_distances,
    marker="s",
    label="Estimated range"
)
plt.axhline(
    STOP_DISTANCE_M,
    color="red",
    linestyle="--",
    label="Stop threshold"
)

plt.xlabel("Measurement number")
plt.ylabel("Distance from wall (m)")
plt.title("RoboRover Ultrasonic Range Simulation")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
