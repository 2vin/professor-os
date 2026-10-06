import math
import matplotlib.pyplot as plt


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


def close_enough(actual, expected, tolerance=1e-3):
    return abs(actual - expected) <= tolerance


link1 = 0.30
link2 = 0.20

# Verify the numerical example from the lesson against rounded reference values.
base, elbow, hand = arm_points(link1, link2, 30.0, 60.0)

expected_elbow = (0.260, 0.150)
expected_hand = (0.260, 0.350)

assert close_enough(elbow[0], expected_elbow[0])
assert close_enough(elbow[1], expected_elbow[1])
assert close_enough(hand[0], expected_hand[0])
assert close_enough(hand[1], expected_hand[1])

print("Verified worked example:")
print("elbow = ({:.3f}, {:.3f}) m".format(elbow[0], elbow[1]))
print("hand  = ({:.3f}, {:.3f}) m".format(hand[0], hand[1]))

poses = [
    ("stretched", 0.0, 0.0),
    ("raised elbow", 30.0, 60.0),
    ("folded", 90.0, 120.0),
]

line_styles = ["-", "--", ":"]
markers = ["o", "s", "^"]

figure, axis = plt.subplots()

for (name, joint1, joint2), line_style, marker in zip(
    poses, line_styles, markers
):
    base, elbow, hand = arm_points(link1, link2, joint1, joint2)

    xs = [base[0], elbow[0], hand[0]]
    ys = [base[1], elbow[1], hand[1]]

    axis.plot(
        xs,
        ys,
        linestyle=line_style,
        marker=marker,
        linewidth=4,
        label=name,
    )

axis.set_aspect("equal", adjustable="box")
axis.set_xlim(-0.55, 0.55)
axis.set_ylim(-0.10, 0.55)
axis.set_xlabel("horizontal position (m)")
axis.set_ylabel("vertical position (m)")
axis.set_title("RoboRover's two-link planar arm")
axis.grid(True)
axis.legend()
plt.show()
