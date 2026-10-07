import math
import matplotlib.pyplot as plt


def forward_kinematics(length1, length2, angle1_deg, angle2_deg):
    """Return base, elbow, gripper, and gripper orientation."""
    angle1 = math.radians(angle1_deg)
    angle2 = math.radians(angle2_deg)

    elbow_x = length1 * math.cos(angle1)
    elbow_y = length1 * math.sin(angle1)

    link2_direction = angle1 + angle2
    gripper_x = elbow_x + length2 * math.cos(link2_direction)
    gripper_y = elbow_y + length2 * math.sin(link2_direction)

    gripper_orientation_deg = math.degrees(link2_direction)

    return (
        (0.0, 0.0),
        (elbow_x, elbow_y),
        (gripper_x, gripper_y),
        gripper_orientation_deg
    )


def main():
    length1 = 0.30
    length2 = 0.20
    angle1_deg = 40.0
    angle2_deg = -25.0

    base, elbow, gripper, orientation = forward_kinematics(
        length1, length2, angle1_deg, angle2_deg
    )

    expected_x = 0.422998
    expected_y = 0.244600
    expected_orientation = 15.0

    assert abs(gripper[0] - expected_x) < 0.00001
    assert abs(gripper[1] - expected_y) < 0.00001
    assert abs(orientation - expected_orientation) < 0.00001

    print("Forward kinematics check passed.")
    print("Gripper position: x = {:.4f} m, y = {:.4f} m".format(
        gripper[0], gripper[1]
    ))
    print("Gripper orientation: {:.1f} degrees".format(orientation))

    x_values = [base[0], elbow[0], gripper[0]]
    y_values = [base[1], elbow[1], gripper[1]]

    plt.figure(figsize=(7, 6))
    plt.plot(x_values, y_values, "o-", linewidth=4, markersize=9)
    plt.text(base[0], base[1], "  base")
    plt.text(elbow[0], elbow[1], "  elbow")
    plt.text(gripper[0], gripper[1], "  gripper")

    reach = length1 + length2
    plt.xlim(-reach - 0.05, reach + 0.05)
    plt.ylim(-reach - 0.05, reach + 0.05)
    plt.axhline(0.0, color="gray", linewidth=0.8)
    plt.axvline(0.0, color="gray", linewidth=0.8)
    plt.gca().set_aspect("equal", adjustable="box")
    plt.xlabel("x position (m)")
    plt.ylabel("y position (m)")
    plt.title("RoboRover two-link forward kinematics")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    main()
