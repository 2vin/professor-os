import random
import matplotlib.pyplot as plt

# Desired distance from RoboRover to the wall, in metres.
target_distance = 0.50

# The rover is allowed to be this far above or below the target.
deadband = 0.03

# Simulation time step, in seconds.
dt = 0.10

# Maximum forward or backward speed, in metres per second.
speed = 0.25

# Starting true distance from the wall, in metres.
distance = 1.20

# A local random generator makes the experiment repeatable.
rng = random.Random(4)

times = []
distances = []
commands = []

for step in range(120):
    time = step * dt

    # Simulate an imperfect distance sensor.
    noise = rng.uniform(-0.015, 0.015)
    measured_distance = distance + noise

    error = measured_distance - target_distance

    # Feedback controller:
    # positive velocity moves toward the wall,
    # negative velocity moves away from the wall.
    if error > deadband:
        velocity = speed
        command = "forward"
    elif error < -deadband:
        velocity = -speed
        command = "backward"
    else:
        velocity = 0.0
        command = "stop"

    # Update the true distance using velocity and time.
    distance = distance - velocity * dt

    # Do not allow the simulated rover to pass through the wall.
    if distance < 0.05:
        distance = 0.05

    times.append(time)
    distances.append(distance)
    commands.append(command)

# Executable verification of the experiment's exact structural claims.
assert len(times) == 120
assert len(distances) == 120
assert len(commands) == 120
assert min(distances) >= 0.05
assert abs(distances[-1] - target_distance) <= 0.10

print("Simulation completed.")
print("Final true distance: {:.3f} m".format(distances[-1]))
print("Final error from target: {:.3f} m".format(
    distances[-1] - target_distance
))

plt.plot(times, distances, label="true distance")
plt.axhline(target_distance, color="red", linestyle="--",
            label="target distance")
plt.xlabel("Time (s)")
plt.ylabel("Distance from wall (m)")
plt.title("RoboRover feedback simulation")
plt.legend()
plt.grid(True)
plt.show()
