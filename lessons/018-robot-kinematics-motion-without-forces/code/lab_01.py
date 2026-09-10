import math
import matplotlib.pyplot as plt


def update_pose(x, y, theta, speed, angular_speed, dt):
    """Update a planar pose for constant forward speed and turn rate."""
    if abs(angular_speed) < 1e-12:
        # Straight-line motion when the angular speed is effectively zero.
        new_x = x + speed * math.cos(theta) * dt
        new_y = y + speed * math.sin(theta) * dt
        new_theta = theta
    else:
        # Exact circular-arc update for constant speed and angular speed.
        new_theta = theta + angular_speed * dt
        radius = speed / angular_speed

        new_x = x + radius * (
            math.sin(new_theta) - math.sin(theta)
        )
        new_y = y + radius * (
            math.cos(theta) - math.cos(new_theta)
        )

    return new_x, new_y, new_theta


# Initial pose and constant motion command.
x = 1.0
y = 2.0
theta = 0.0

speed = 0.50          # metres per second
angular_speed = 0.20  # radians per second
total_time = 3.0      # seconds
dt = 0.05             # seconds

times = [0.0]
xs = [x]
ys = [y]
thetas = [theta]

steps = int(round(total_time / dt))

for step in range(steps):
    x, y, theta = update_pose(
        x, y, theta, speed, angular_speed, dt
    )
    times.append((step + 1) * dt)
    xs.append(x)
    ys.append(y)
    thetas.append(theta)

# Independent checks of the worked example.
expected_theta = angular_speed * total_time
expected_x = 1.0 + (speed / angular_speed) * math.sin(expected_theta)
expected_y = 2.0 + (speed / angular_speed) * (
    1.0 - math.cos(expected_theta)
)

assert len(times) == steps + 1
assert abs(times[-1] - total_time) < 1e-12
assert abs(theta - expected_theta) < 1e-12
assert abs(x - expected_x) < 1e-12
assert abs(y - expected_y) < 1e-12

path_length = speed * total_time
assert abs(path_length - 1.5) < 1e-12

print("Final pose:")
print("x = {:.3f} m".format(x))
print("y = {:.3f} m".format(y))
print("theta = {:.3f} rad".format(theta))
print("Commanded path length = {:.3f} m".format(path_length))
print("All worked-example checks passed.")

plt.figure(figsize=(7, 6))
plt.plot(xs, ys, color="darkblue", linewidth=2, label="RoboRover path")
plt.scatter([xs[0]], [ys[0]], color="green", s=70, label="Start")
plt.scatter([xs[-1]], [ys[-1]], color="red", s=70, label="Finish")

# Draw a short arrow showing the final heading.
arrow_length = 0.35
plt.arrow(
    xs[-1],
    ys[-1],
    arrow_length * math.cos(thetas[-1]),
    arrow_length * math.sin(thetas[-1]),
    width=0.015,
    head_width=0.10,
    head_length=0.12,
    color="red",
    length_includes_head=True
)

plt.axis("equal")
plt.xlabel("x position (m)")
plt.ylabel("y position (m)")
plt.title("RoboRover: constant forward speed and turn rate")
plt.grid(True)
plt.legend()
plt.show()
