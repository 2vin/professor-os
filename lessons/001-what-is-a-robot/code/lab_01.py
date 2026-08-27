import matplotlib.pyplot as plt

TIME_STEP_S = 1.0
SPEED_M_PER_S = 0.5

def simulate(commands):
    """Return position after each command, including the starting position."""
    positions = [0.0]
    position_m = 0.0

    for command in commands:
        position_m += command * SPEED_M_PER_S * TIME_STEP_S
        positions.append(position_m)

    return positions

# The human operator chooses these commands:
# 1 means forward, 0 means stop.
human_commands = [1, 0, 1, 0]

# The stored program chooses these commands in advance.
preprogrammed_commands = [1, 1, 1, 0]

# The environment reports an obstacle during time steps 3 and 4.
obstacle_detected = [False, False, True, True]

# Autonomous software selects its own command from the measurements.
autonomous_commands = []
for obstacle in obstacle_detected:
    if obstacle:
        autonomous_commands.append(0)
    else:
        autonomous_commands.append(1)

runs = {
    "human-directed": simulate(human_commands),
    "preprogrammed": simulate(preprogrammed_commands),
    "autonomous": simulate(autonomous_commands),
}

final_positions_m = {}
for name, positions in runs.items():
    final_positions_m[name] = positions[-1]

# Executable verification of the exact results.
assert autonomous_commands == [1, 1, 0, 0]
assert final_positions_m["human-directed"] == 1.0
assert final_positions_m["preprogrammed"] == 1.5
assert final_positions_m["autonomous"] == 1.0

print("Autonomous commands:", autonomous_commands)
print("Final positions (m):", final_positions_m)
print("Verified: all final positions match the model.")

time_s = [0.0, 1.0, 2.0, 3.0, 4.0]

for name, positions in runs.items():
    plt.plot(time_s, positions, marker="o", label=name)

plt.title("RoboRover: same hardware, different decision authority")
plt.xlabel("Time (s)")
plt.ylabel("Position (m)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()
