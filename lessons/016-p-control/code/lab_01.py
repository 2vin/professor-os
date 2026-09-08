import matplotlib.pyplot as plt


def clamp(value, low, high):
    """Keep value between low and high."""
    return max(low, min(value, high))


def simulate_p_control(kp, target, start, dt, steps, max_speed):
    """Simulate position control with a proportional controller."""
    time_values = []
    position_values = []
    command_values = []

    position = start

    for step in range(steps + 1):
        time_now = step * dt
        error = target - position
        requested_speed = kp * error
        actual_speed = clamp(requested_speed, -max_speed, max_speed)

        time_values.append(time_now)
        position_values.append(position)
        command_values.append(actual_speed)

        # Move the simple robot for one time step, except after the
        # final recorded sample.
        if step < steps:
            position = position + actual_speed * dt

    return time_values, position_values, command_values


target = 1.0
start = 0.0
dt = 0.05
steps = 200
max_speed = 0.60

low_kp = 0.8
high_kp = 2.0

low_gain_data = simulate_p_control(
    kp=low_kp,
    target=target,
    start=start,
    dt=dt,
    steps=steps,
    max_speed=max_speed
)

high_gain_data = simulate_p_control(
    kp=high_kp,
    target=target,
    start=start,
    dt=dt,
    steps=steps,
    max_speed=max_speed
)

low_times, low_positions, low_commands = low_gain_data
high_times, high_positions, high_commands = high_gain_data

# Verification checks: these prove properties of this simulation.
tolerance = 1e-12

expected_low_initial = clamp(
    low_kp * (target - start),
    -max_speed,
    max_speed
)
expected_high_initial = clamp(
    high_kp * (target - start),
    -max_speed,
    max_speed
)

assert abs(low_commands[0] - expected_low_initial) <= tolerance
assert abs(high_commands[0] - expected_high_initial) <= tolerance
assert abs(low_positions[-1] - target) < 0.01
assert abs(high_positions[-1] - target) < 0.01
assert abs(low_commands[-1]) < 0.01
assert abs(high_commands[-1]) < 0.01

print("Verification passed.")
print("Low-gain initial command: {:.3f} m/s".format(low_commands[0]))
print("High-gain initial command: {:.3f} m/s".format(high_commands[0]))
print("Low-gain final position: {:.3f} m".format(low_positions[-1]))
print("High-gain final position: {:.3f} m".format(high_positions[-1]))

figure, axes = plt.subplots(2, 1, figsize=(9, 8), sharex=True)

axes[0].plot(low_times, low_positions, label="Kp = 0.8 per second")
axes[0].plot(
    high_times,
    high_positions,
    label="Kp = 2.0 per second"
)
axes[0].axhline(
    target,
    color="black",
    linestyle="--",
    label="target = 1.0 m"
)
axes[0].set_ylabel("Position (m)")
axes[0].set_title("RoboRover Position and Command with Proportional Control")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(
    low_times,
    low_commands,
    label="Kp = 0.8 per second"
)
axes[1].plot(
    high_times,
    high_commands,
    label="Kp = 2.0 per second"
)
axes[1].axhline(
    max_speed,
    color="black",
    linestyle="--",
    label="speed limit"
)
axes[1].axhline(-max_speed, color="black", linestyle=":")
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Command (m/s)")
axes[1].legend()
axes[1].grid(True)

figure.tight_layout()
plt.show()
