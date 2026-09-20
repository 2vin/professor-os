vertical_focal_length_px = 400.0
marker_height_m = 0.30
distance_m = 4.0
projected_height_px = (
    vertical_focal_length_px * marker_height_m / distance_m
)

assert abs(projected_height_px - 30.0) < 1e-6
print("Projected marker height: {:.1f} pixels".format(
    projected_height_px
))
