import numpy as np

distance = 1.2
maximum_speed = 0.5
maximum_acceleration = 0.5

candidate_times = np.arange(0.01, 20.0 + 0.005, 0.01)

# For a quintic smoothstep:
# peak speed = (15/8) * distance / T
# peak acceleration magnitude = (10/sqrt(3)) * distance / T^2
peak_speeds = (15.0 / 8.0) * distance / candidate_times
peak_accelerations = (
    (10.0 / np.sqrt(3.0)) * distance / (candidate_times ** 2)
)

acceptable = (
    (peak_speeds <= maximum_speed) &
    (peak_accelerations <= maximum_acceleration)
)

if not np.any(acceptable):
    raise RuntimeError("No acceptable candidate duration was found.")

shortest_index = np.flatnonzero(acceptable)[0]
shortest_time = candidate_times[shortest_index]
shortest_speed = peak_speeds[shortest_index]
shortest_acceleration = peak_accelerations[shortest_index]

# The speed limit is active: 4.49 s is too fast, while 4.50 s
# is the first 0.01-second candidate satisfying both limits.
assert abs(shortest_time - 4.50) < 1e-12
assert peak_speeds[shortest_index - 1] > maximum_speed
assert shortest_speed <= maximum_speed
assert shortest_acceleration <= maximum_acceleration

# Verify the reported numerical values for the selected candidate.
assert abs(shortest_speed - (2.25 / 4.50)) < 1e-12
assert abs(
    shortest_acceleration
    - ((10.0 / np.sqrt(3.0)) * 1.2 / (4.50 ** 2))
) < 1e-12

print("Shortest tested duration: {:.2f} s".format(shortest_time))
print("Peak speed at that duration: {:.6f} m/s".format(shortest_speed))
print("Peak acceleration magnitude at that duration: {:.6f} m/s^2".format(
    shortest_acceleration
))
