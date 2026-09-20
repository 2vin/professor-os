import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Camera parameters
focal_length_px = 400.0
vertical_focal_length_px = 400.0
image_width_px = 640.0
image_height_px = 480.0

# Marker parameters
marker_height_m = 0.30
distance_m = 2.0

# Pinhole projection: apparent image height in pixels
projected_height_px = (
    vertical_focal_length_px * marker_height_m / distance_m
)

# Horizontal field of view, using the horizontal image dimension
horizontal_fov_rad = 2.0 * math.atan(
    image_width_px / (2.0 * focal_length_px)
)
horizontal_fov_deg = math.degrees(horizontal_fov_rad)

# Vertical field of view for the side-view drawing
vertical_fov_rad = 2.0 * math.atan(
    image_height_px / (2.0 * vertical_focal_length_px)
)
vertical_fov_deg = math.degrees(vertical_fov_rad)
half_vertical_fov_deg = vertical_fov_deg / 2.0

# Verification statements: these verify the numerical claims in the lesson.
assert abs(projected_height_px - 60.0) < 1e-6
assert abs(horizontal_fov_deg - 77.31961650818018) < 1e-6
assert abs(vertical_fov_deg - 61.92751306414704) < 1e-6
assert abs(
    2.0 * half_vertical_fov_deg - vertical_fov_deg
) < 1e-6

print("Projected marker height: {:.1f} pixels".format(
    projected_height_px
))
print("Horizontal field of view: {:.2f} degrees".format(
    horizontal_fov_deg
))
print("Vertical field of view: {:.2f} degrees".format(
    vertical_fov_deg
))

# Draw a side-view camera wedge and marker.
# The rays use the vertical FOV, not the horizontal FOV.
fig, ax = plt.subplots(figsize=(8, 5))

# Camera position
camera_x = 0.0
camera_y = 0.0

# Draw rays representing the top and bottom of the side-view FOV.
# This is a 2D slice of a 3D camera frustum.
view_distance_m = 3.0
ray_angle_rad = math.radians(half_vertical_fov_deg)
top_x = view_distance_m
top_y = math.tan(ray_angle_rad) * view_distance_m
bottom_x = view_distance_m
bottom_y = -top_y

ax.plot(
    [camera_x, top_x],
    [camera_y, top_y],
    color="steelblue",
    label="vertical FOV boundary"
)
ax.plot(
    [camera_x, bottom_x],
    [camera_y, bottom_y],
    color="steelblue"
)

# Draw the marker as a vertical rectangle at the chosen distance.
marker_bottom_m = -marker_height_m / 2.0
marker = Rectangle(
    (distance_m, marker_bottom_m),
    0.05,
    marker_height_m,
    facecolor="orange",
    edgecolor="black",
    label="orange marker"
)
ax.add_patch(marker)

ax.scatter(
    [camera_x],
    [camera_y],
    color="black",
    s=50,
    label="camera"
)
ax.axhline(0.0, color="gray", linewidth=0.8)

ax.set_xlim(-0.1, view_distance_m + 0.2)
ax.set_ylim(-2.0, 2.0)
ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("Forward distance (m)")
ax.set_ylabel("Vertical position (m)")
ax.set_title("RoboRover camera vertical field of view")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
