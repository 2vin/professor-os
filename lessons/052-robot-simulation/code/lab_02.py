import matplotlib.pyplot as plt


def simulate(sensor_bias):
    wall_position = 2.0
    time_step = 0.5
    forward_speed = 0.4
    stop_distance = 0.7

    time_values = [0.0]
    position_values = [0.0]
    command_values = []
    measured_distance_values = []

    position = 0.0
    current_time = 0.0

    while current_time < 10.0:
        true_distance = wall_position - position
        measured_distance = max(0.0, true_distance + sensor_bias)

        # This represents a message published on /roborover/range.
        measured_distance_values.append(measured_distance)

        # This represents a controller publishing /roborover/cmd_speed.
        if measured_distance > stop_distance:
            command_speed = forward_speed
        else:
            command_speed = 0.0

        command_values.append(command_speed)

        position = position + command_speed * time_step
        current_time = current_time + time_step

        position_values.append(position)
        time_values.append(current_time)

        if command_speed == 0.0:
            break

    path_length = sum(command * time_step for command in command_values)

    return {
        "time": time_values,
        "position": position_values,
        "commands": command_values,
        "measured_distance": measured_distance_values,
        "path_length": path_length
    }


ideal_run = simulate(sensor_bias=0.0)
biased_run = simulate(sensor_bias=-0.2)

# These checks verify the exact claims made by this experiment.
assert round(ideal_run["position"][-1], 2) == 1.40
assert round(biased_run["position"][-1], 2) == 1.20
assert round(ideal_run["path_length"], 2) == 1.40
assert round(biased_run["path_length"], 2) == 1.20

print("Ideal final position: {:.2f} m".format(ideal_run["position"][-1]))
print("Biased final position: {:.2f} m".format(biased_run["position"][-1]))
print("Ideal path length: {:.2f} m".format(ideal_run["path_length"]))
print("Biased path length: {:.2f} m".format(biased_run["path_length"]))
print("Verification passed.")

plt.figure(figsize=(8, 5))
plt.plot(
    ideal_run["time"],
    ideal_run["position"],
    marker="o",
    label="Ideal sensor"
)
plt.plot(
    biased_run["time"],
    biased_run["position"],
    marker="s",
    label="Sensor bias = -0.2 m"
)
plt.axhline(2.0, color="black", linestyle="--", label="Wall at 2.0 m")
plt.xlabel("Simulation time (s)")
plt.ylabel("RoboRover position (m)")
plt.title("RoboRover simulation: sensor bias changes stopping position")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
