import math
import matplotlib.pyplot as plt


def clamp(value, low, high):
    return max(low, min(high, value))


def settling_time(time_values, position_values, target,
                  tolerance=0.02, minimum_dwell=0.5):
    """Return first entry into the band that lasts for minimum_dwell seconds."""
    band = tolerance * abs(target)
    if band == 0.0:
        raise ValueError("This helper requires a nonzero target.")

    required_samples = max(
        1,
        int(math.ceil(minimum_dwell /
                      (time_values[1] - time_values[0])))
    )

    for index in range(len(position_values)):
        end = min(index + required_samples, len(position_values))
        window = position_values[index:end]
        if len(window) < required_samples:
            continue
        if all(abs(position - target) <= band for position in window):
            return time_values[index]

    return None


def simulate(controller_name, kp, ki, kd, measurement_noise=0.0,
             anti_windup=True):
    dt = 0.02
    duration = 12.0
    target = 1.0
    disturbance = -0.12
    drag = 0.35
    command_limit = 1.0

    position = 0.0
    velocity = 0.0
    integral = 0.0
    previous_error = target

    data = {
        "name": controller_name,
        "time": [], "position": [], "error": [],
        "p": [], "i": [], "d": [],
        "raw_command": [], "command": [], "integral": [],
        "saturated": []
    }

    steps = int(duration / dt)

    for step in range(steps + 1):
        current_time = step * dt
        measured_position = (
            position + measurement_noise *
            math.sin(40.0 * current_time)
        )
        error = target - measured_position

        trial_integral = integral + error * dt
        derivative = (error - previous_error) / dt

        p_contribution = kp * error
        trial_i_contribution = ki * trial_integral
        d_contribution = kd * derivative
        trial_raw = (
            p_contribution + trial_i_contribution + d_contribution
        )

        same_direction_saturation = (
            abs(trial_raw) > command_limit
            and trial_raw * error > 0.0
        )

        if not anti_windup or not same_direction_saturation:
            integral = trial_integral

        i_contribution = ki * integral
        raw_command = p_contribution + i_contribution + d_contribution
        command = clamp(raw_command, -command_limit, command_limit)

        data["time"].append(current_time)
        data["position"].append(position)
        data["error"].append(error)
        data["p"].append(p_contribution)
        data["i"].append(i_contribution)
        data["d"].append(d_contribution)
        data["raw_command"].append(raw_command)
        data["command"].append(command)
        data["integral"].append(integral)
        data["saturated"].append(abs(raw_command) > command_limit)

        if step == steps:
            break

        acceleration = command + disturbance - drag * velocity
        velocity += acceleration * dt
        position += velocity * dt
        previous_error = error

    return data


controllers = {
    "P": (1.8, 0.0, 0.0),
    "PI": (1.8, 0.8, 0.0),
    "PID": (1.8, 0.8, 0.35),
}

results = {}
for name, gains in controllers.items():
    results[name] = simulate(name, *gains)

noisy_results = {}
for name in ("PI", "PID"):
    noisy_results[name + " noisy"] = simulate(
        name + " noisy", *controllers[name], measurement_noise=0.005
    )

# Controlled comparison: PI with and without anti-windup.
windup_results = {
    "PI anti-windup": simulate(
        "PI anti-windup", 1.8, 0.8, 0.0, anti_windup=True
    ),
    "PI no anti-windup": simulate(
        "PI no anti-windup", 1.8, 0.8, 0.0, anti_windup=False
    ),
}

expected_points = int(12.0 / 0.02) + 1
for collection in (results, noisy_results, windup_results):
    for data in collection.values():
        assert len(data["time"]) == expected_points
        for key in ("position", "error", "p", "i", "d",
                    "raw_command", "command", "integral"):
            assert all(math.isfinite(value) for value in data[key])

print("Final errors and 2% settling times:")
for name, data in results.items():
    settling = settling_time(
        data["time"], data["position"], target=1.0
    )
    print("{}: measured_error={:.4f} m, settling={}".format(
        name, data["error"][-1], settling
    ))

print("\nMaximum absolute raw commands:")
for name, data in results.items():
    maximum = max(abs(value) for value in data["raw_command"])
    print("{}: {:.3f}".format(name, maximum))

# The noisy-command plot directly exposes the PI-versus-PID comparison.
plt.figure(figsize=(10, 5))
for name, data in noisy_results.items():
    plt.plot(data["time"], data["command"], label=name)
plt.xlabel("Time (s)")
plt.ylabel("Applied command (-1 to +1)")
plt.title("Noisy PI and PID commands")
plt.grid(True)
plt.legend()
plt.tight_layout()

# A numerical roughness measure supplements the plot. It is the mean
# absolute change between consecutive applied commands.
print("\nNoisy command roughness:")
roughness = {}
for name, data in noisy_results.items():
    changes = [
        abs(current - previous)
        for previous, current in zip(
            data["command"][:-1], data["command"][1:]
        )
    ]
    roughness[name] = sum(changes) / len(changes)
    print("{}: mean step change={:.6f}".format(name, roughness[name]))

# With these fixed gains and deterministic noise, derivative action should
# produce the larger command variation. Verify that stated comparison.
assert roughness["PID noisy"] > roughness["PI noisy"]

plt.figure(figsize=(12, 10))

plt.subplot(2, 2, 1)
for name, data in results.items():
    plt.plot(data["time"], data["position"], label=name)
plt.axhline(1.0, color="black", linestyle="--", label="target")
plt.xlabel("Time (s)")
plt.ylabel("True position (m)")
plt.title("Clean true-position responses")
plt.grid(True)
plt.legend()

plt.subplot(2, 2, 2)
for name, data in results.items():
    plt.plot(data["time"], data["p"], label=name + " P")
    plt.plot(data["time"], data["i"], "--", label=name + " I")
    plt.plot(data["time"], data["d"], ":", label=name + " D")
plt.xlabel("Time (s)")
plt.ylabel("Contribution")
plt.title("Individual controller contributions")
plt.grid(True)
plt.legend(fontsize=8)

plt.subplot(2, 2, 3)
for name, data in results.items():
    plt.plot(data["time"], data["raw_command"],
             label=name + " raw")
    plt.plot(data["time"], data["command"], "--",
             label=name + " limited")
plt.axhline(1.0, color="black", linestyle=":")
plt.axhline(-1.0, color="black", linestyle=":")
plt.xlabel("Time (s)")
plt.ylabel("Command (-1 to +1)")
plt.title("Raw and actuator-limited commands")
plt.grid(True)
plt.legend(fontsize=8)

plt.subplot(2, 2, 4)
for name, data in windup_results.items():
    plt.plot(data["time"], data["integral"], label=name)
plt.xlabel("Time (s)")
plt.ylabel("Integral state (m·s)")
plt.title("Anti-windup comparison")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
