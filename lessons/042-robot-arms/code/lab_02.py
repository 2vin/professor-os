import math


def arm_points(link1, link2, joint1_deg, joint2_deg):
    """Return base, elbow, and hand coordinates for a planar 2-link arm."""
    joint1_rad = math.radians(joint1_deg)
    joint2_rad = math.radians(joint2_deg)

    elbow_x = link1 * math.cos(joint1_rad)
    elbow_y = link1 * math.sin(joint1_rad)

    hand_angle_rad = joint1_rad + joint2_rad
    hand_x = elbow_x + link2 * math.cos(hand_angle_rad)
    hand_y = elbow_y + link2 * math.sin(hand_angle_rad)

    return (0.0, 0.0), (elbow_x, elbow_y), (hand_x, hand_y)


link1 = 0.30
link2 = 0.20
target_x = 0.26
target_y = 0.35

# Calculate the hand position from the same model used by the plot.
_, _, hand = arm_points(link1, link2, 30.0, 60.0)

error = math.sqrt(
    (hand[0] - target_x) ** 2 +
    (hand[1] - target_y) ** 2
)

print("distance from target = {:.3f} m".format(error))
