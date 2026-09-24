import math
import matplotlib.pyplot as plt


def move(x, y, heading_degrees, distance):
    """Return the new x and y after moving a measured distance."""
    heading_radians = math.radians(heading_degrees)
    new_x = x + distance * math.cos(heading_radians)
    new_y = y + distance * math.sin(heading_radians)
    return new_x, new_y


def make_path(distances):
    """Build a square-like path using east, north, west, south headings."""
    headings = [0.0, 90.0, 180.0, 270.0]
    x = 0.0
    y = 0.0
    path = [(x, y)]

    for heading, distance in zip(headings, distances):
        x, y = move(x, y, heading, distance)
        path.append((x, y))

    return path


true_distances = [1.00, 1.00, 1.00, 1.00]
odometry_distances = [1.02, 0.97, 1.04, 0.96]

true_path = make_path(true_distances)
odometry_path = make_path(odometry_distances)

true_final = true_path[-1]
odometry_final = odometry_path[-1]

# Verification of the final positions for this floating-point model.
assert math.isclose(true_final[0], 0.0, abs_tol=1e-12)
assert math.isclose(true_final[1], 0.0, abs_tol=1e-12)
assert math.isclose(odometry_final[0], -0.02, abs_tol=1e-12)
assert math.isclose(odometry_final[1], 0.01, abs_tol=1e-12)

error_x = odometry_final[0] - true_final[0]
error_y = odometry_final[1] - true_final[1]
error_distance = math.hypot(error_x, error_y)

print("True final position: ({:.2f}, {:.2f}) m".format(
    true_final[0], true_final[1]
))
print("Odometry final position: ({:.2f}, {:.2f}) m".format(
    odometry_final[0], odometry_final[1]
))
print("Odometry error: ({:.2f}, {:.2f}) m".format(error_x, error_y))
print("Error distance: {:.5f} m".format(error_distance))

true_x = [point[0] for point in true_path]
true_y = [point[1] for point in true_path]
odom_x = [point[0] for point in odometry_path]
odom_y = [point[1] for point in odometry_path]

plt.figure(figsize=(7, 7))
plt.plot(true_x, true_y, "o-", label="True path")
plt.plot(odom_x, odom_y, "s--", label="Odometry estimate")
plt.scatter([0.0], [0.0], marker="*", s=150, label="Start")

plt.xlabel("x position (m)")
plt.ylabel("y position (m)")
plt.title("RoboRover: true path and odometry estimate")
plt.axis("equal")
plt.grid(True)
plt.legend()
plt.show()
