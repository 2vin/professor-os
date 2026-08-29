try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

# Robot and experiment settings
speed_m_per_s = 0.75
time_step_s = 0.5
starting_position_m = 0.0
target_position_m = 4.5

# Preconditions for this exact-step experiment
assert speed_m_per_s > 0
assert time_step_s > 0
assert target_position_m >= starting_position_m

# Ideal constant-speed prediction
predicted_time_s = (
    target_position_m - starting_position_m
) / speed_m_per_s

steps_exact = predicted_time_s / time_step_s
number_of_steps = int(round(steps_exact))

# This simple experiment requires the target time to be an exact
# whole number of time steps.
assert abs(steps_exact - number_of_steps) < 1e-9

times_s = []
positions_m = []

for step in range(number_of_steps + 1):
    time_s = step * time_step_s
    position_m = starting_position_m + speed_m_per_s * time_s

    times_s.append(time_s)
    positions_m.append(position_m)

# Verification checks: these prove the exact claims made by this experiment.
assert len(positions_m) == number_of_steps + 1
assert round(positions_m[-1], 10) == round(target_position_m, 10)
assert round(times_s[-1], 10) == round(predicted_time_s, 10)

print("Number of recorded positions:", len(positions_m))
print("Predicted arrival time:", predicted_time_s, "s")
print("Final time:", times_s[-1], "s")
print("Final position:", positions_m[-1], "m")
print(
    "RoboRover reaches",
    target_position_m,
    "m at:",
    times_s[-1],
    "s",
)

if plt is not None:
    plt.plot(times_s, positions_m, marker="o")
    plt.xlabel("Time (s)")
    plt.ylabel("Position along track (m)")
    plt.title("RoboRover: Position versus Time")
    plt.grid(True)
    plt.show()
else:
    print("matplotlib is unavailable; graph omitted.")
