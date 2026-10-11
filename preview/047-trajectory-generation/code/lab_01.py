import numpy as np
import matplotlib.pyplot as plt

# Motion specification
x0 = 0.0       # starting position, metres
xf = 1.2       # final position, metres
T = 4.0        # total time, seconds
dt = 0.02      # sampling interval, seconds

# Time samples, including the final time
time = np.arange(0.0, T + dt, dt)
s = time / T
distance = xf - x0

# Quintic smoothstep and its first two derivatives
p = 10.0 * s**3 - 15.0 * s**4 + 6.0 * s**5
dp_ds = 30.0 * s**2 - 60.0 * s**3 + 30.0 * s**4
d2p_ds2 = 60.0 * s - 180.0 * s**2 + 120.0 * s**3

# Position, velocity, and acceleration
position = x0 + distance * p
velocity = (distance / T) * dp_ds
acceleration = (distance / (T * T)) * d2p_ds2

# Verify important mathematical claims
assert abs(position[0] - x0) < 1e-12
assert abs(position[-1] - xf) < 1e-12
assert abs(velocity[0]) < 1e-12
assert abs(velocity[-1]) < 1e-12
assert abs(acceleration[0]) < 1e-12
assert abs(acceleration[-1]) < 1e-12

# Verify the worked example at t = 1.0 seconds
one_second_index = int(round(1.0 / dt))
assert abs(position[one_second_index] - 0.12421875) < 1e-10
assert abs(velocity[one_second_index] - 0.31640625) < 1e-10
assert abs(acceleration[one_second_index] - 0.421875) < 1e-10

# Verify the midpoint values
midpoint_index = int(round(2.0 / dt))
assert abs(position[midpoint_index] - 0.6) < 1e-10
assert abs(velocity[midpoint_index] - 0.5625) < 1e-10
assert abs(acceleration[midpoint_index]) < 1e-10

# Verify the analytical peak acceleration magnitude.
# The sampled maximum is slightly lower or equal because the samples
# need not fall exactly at the analytical extrema.
analytical_peak_acceleration = (
    (10.0 / np.sqrt(3.0)) * abs(distance) / (T * T)
)
assert abs(analytical_peak_acceleration - 0.4330127019) < 1e-10
assert np.max(np.abs(acceleration)) <= analytical_peak_acceleration + 1e-12

print("All trajectory checks passed.")
print("At 1.0 s: position = {:.8f} m, velocity = {:.8f} m/s, acceleration = {:.8f} m/s^2".format(
    position[one_second_index],
    velocity[one_second_index],
    acceleration[one_second_index]
))
print("At 2.0 s: position = {:.8f} m, velocity = {:.8f} m/s, acceleration = {:.8f} m/s^2".format(
    position[midpoint_index],
    velocity[midpoint_index],
    acceleration[midpoint_index]
))
print("Analytical peak acceleration magnitude = {:.8f} m/s^2".format(
    analytical_peak_acceleration
))

# Plot the three motion quantities
figure, axes = plt.subplots(3, 1, figsize=(9, 8), sharex=True)

axes[0].plot(time, position, color="navy")
axes[0].set_ylabel("Position (m)")
axes[0].grid(True)

axes[1].plot(time, velocity, color="darkgreen")
axes[1].set_ylabel("Velocity (m/s)")
axes[1].grid(True)

axes[2].plot(time, acceleration, color="darkred")
axes[2].set_ylabel("Acceleration (m/s^2)")
axes[2].set_xlabel("Time (s)")
axes[2].grid(True)

figure.suptitle("RoboRover Quintic Trajectory")
figure.tight_layout()
plt.show()
