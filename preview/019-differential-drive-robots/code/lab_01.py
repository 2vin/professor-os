import math
import matplotlib.pyplot as plt


def differential_drive_motion(v_left, v_right, wheel_separation):
    """Return signed longitudinal velocity, angular speed, and turning radius."""
    forward_velocity = (v_right + v_left) / 2.0
    angular_speed = (v_right - v_left) / wheel_separation

    if abs(angular_speed) < 1e-12:
        turning_radius = float("inf")
    else:
        turning_radius = forward_velocity / angular_speed

    return forward_velocity, angular_speed, turning_radius


def pose_at_time(v_left, v_right, wheel_separation, time_seconds):
    """Calculate ideal pose from an initial pose of (0, 0, 0)."""
    forward_velocity, angular_speed, unused_radius = differential_drive_motion(
        v_left, v_right, wheel_separation
    )

    if abs(angular_speed) < 1e-12:
        x_position = forward_velocity * time_seconds
        y_position = 0.0
        heading = 0.0
    else:
        heading = angular_speed * time_seconds
        x_position = (forward_velocity / angular_speed) * math.sin(heading)
        y_position = (forward_velocity / angular_speed) * (1.0 - math.cos(heading))

    return x_position, y_position, heading


def make_path(v_left, v_right, wheel_separation, total_time, samples):
    times = []
    x_values = []
    y_values = []

    for index in range(samples + 1):
        time_seconds = total_time * index / float(samples)
        x_position, y_position, unused_heading = pose_at_time(
            v_left, v_right, wheel_separation, time_seconds
        )
        times.append(time_seconds)
        x_values.append(x_position)
        y_values.append(y_position)

    return times, x_values, y_values


# Verify the worked example.
example_v, example_omega, example_radius = differential_drive_motion(
    0.20, 0.50, 0.30
)

assert abs(example_v - 0.35) < 1e-12
assert abs(example_omega - 1.0) < 1e-12
assert abs(example_radius - 0.35) < 1e-12

print("Worked example verified:")
print("forward velocity =", example_v, "m/s")
print("angular speed =", example_omega, "rad/s")
print("turning radius =", example_radius, "m")

# Verify two important special cases.
straight_v, straight_omega, straight_radius = differential_drive_motion(
    0.30, 0.30, 0.30
)
spin_v, spin_omega, spin_radius = differential_drive_motion(
    -0.20, 0.20, 0.30
)

assert abs(straight_v - 0.30) < 1e-12
assert abs(straight_omega) < 1e-12
assert abs(spin_v) < 1e-12
assert abs(spin_omega - (0.40 / 0.30)) < 1e-12

cases = [
    ("equal speeds", 0.30, 0.30),
    ("faster right wheel", 0.20, 0.50),
    ("spin in place", -0.20, 0.20),
]

plt.figure(figsize=(8, 6))

for label, left_speed, right_speed in cases:
    times, x_values, y_values = make_path(
        left_speed, right_speed, 0.30, 4.0, 200
    )
    plt.plot(x_values, y_values, label=label)

plt.axhline(0.0, color="black", linewidth=0.6)
plt.axvline(0.0, color="black", linewidth=0.6)
plt.xlabel("x position (m)")
plt.ylabel("y position (m)")
plt.title("Ideal differential-drive paths")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.show()
