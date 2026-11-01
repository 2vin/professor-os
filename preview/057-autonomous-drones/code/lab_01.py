import random
import matplotlib.pyplot as plt

# Physical parameters
mass = 1.0                 # kg
gravity = 9.81             # m/s^2
dt = 0.02                  # s
duration = 8.0             # s
target_altitude = 2.0      # m

# Controller parameters
kp = 18.0                  # N/m
kd = 7.0                   # N/(m/s)

random.seed(4)

altitude = 0.0
vertical_speed = 0.0       # simulated true internal state

times = []
altitudes = []
measured_altitudes = []
thrusts = []

steps = int(duration / dt)

for step in range(steps):
    time = step * dt

    # Noisy altitude measurement.
    measured_altitude = altitude + random.uniform(-0.03, 0.03)
    error = target_altitude - measured_altitude

    # True simulated velocity supplies the damping-like term.
    thrust = mass * gravity + kp * error - kd * vertical_speed

    # Model actuator limits.
    thrust = max(0.0, min(2.0 * mass * gravity, thrust))

    # Simplified vertical dynamics.
    acceleration = thrust / mass - gravity
    vertical_speed += acceleration * dt
    altitude += vertical_speed * dt

    times.append(time)
    altitudes.append(altitude)
    measured_altitudes.append(measured_altitude)
    thrusts.append(thrust)

assert len(times) == steps
assert len(altitudes) == steps
assert len(measured_altitudes) == steps
assert len(thrusts) == steps
assert 1.5 < altitudes[-1] < 2.5
assert min(thrusts) >= 0.0
assert max(thrusts) <= 2.0 * mass * gravity

print("Final altitude: {:.3f} m".format(altitudes[-1]))
print("Final altitude error: {:.3f} m".format(
    target_altitude - altitudes[-1]
))

figure, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True)

axes[0].plot(
    times,
    altitudes,
    linestyle="-",
    marker="",
    label="true altitude"
)
axes[0].plot(
    times,
    measured_altitudes,
    linestyle=":",
    marker="",
    alpha=0.65,
    label="noisy sensor altitude"
)
axes[0].axhline(
    target_altitude,
    color="black",
    linestyle="--",
    label="target altitude"
)
axes[0].set_ylabel("Altitude (m)")
axes[0].set_title("RoboRover altitude control")
axes[0].grid(True)
axes[0].legend()

axes[1].plot(
    times,
    thrusts,
    color="darkorange",
    linestyle="-",
    marker="",
    label="commanded thrust"
)
axes[1].axhline(
    2.0 * mass * gravity,
    color="red",
    linestyle="--",
    label="maximum thrust"
)
axes[1].set_xlabel("Time (s)")
axes[1].set_ylabel("Thrust (N)")
axes[1].grid(True)
axes[1].legend()

plt.tight_layout()
plt.show()
