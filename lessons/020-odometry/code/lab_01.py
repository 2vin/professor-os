import math
import matplotlib.pyplot as plt


def apply_wheel_motion(pose, left_distance, right_distance, track_width):
    """Update a pose from measured left- and right-wheel travel."""
    x, y, theta = pose
    forward_distance = (left_distance + right_distance) / 2.0
    heading_change = (right_distance - left_distance) / track_width
    midpoint_heading = theta + heading_change / 2.0

    new_x = x + forward_distance * math.cos(midpoint_heading)
    new_y = y + forward_distance * math.sin(midpoint_heading)
    new_theta = theta + heading_change

    return new_x, new_y, new_theta


def simulate():
    track_width = 0.20
    side_length = 1.0
    true_turn_degrees = 90.0
    estimated_turn_degrees = 91.0
    estimated_distance_scale = 1.02

    true_pose = (0.0, 0.0, 0.0)
    estimated_pose = (0.0, 0.0, math.radians(0.0))

    true_path = [true_pose]
    estimated_path = [estimated_pose]

    # A turn in place through angle alpha requires opposite wheel
    # travels of magnitude track_width * alpha / 2.
    true_turn_travel = (
        track_width * math.radians(true_turn_degrees) / 2.0
    )
    estimated_turn_travel = (
        track_width * math.radians(estimated_turn_degrees) / 2.0
    )

    for step in range(4):
        # True forward wheel travel.
        true_pose = apply_wheel_motion(
            true_pose, side_length, side_length, track_width
        )

        # Estimated encoder-derived forward travel has a scale error.
        estimated_side_length = side_length * estimated_distance_scale
        estimated_pose = apply_wheel_motion(
            estimated_pose,
            estimated_side_length,
            estimated_side_length,
            track_width
        )

        true_path.append(true_pose)
        estimated_path.append(estimated_pose)

        # True 90-degree left turn in place.
        true_pose = apply_wheel_motion(
            true_pose,
            -true_turn_travel,
            true_turn_travel,
            track_width
        )

        # Estimated turn is 91 degrees instead of 90 degrees.
        estimated_pose = apply_wheel_motion(
            estimated_pose,
            -estimated_turn_travel,
            estimated_turn_travel,
            track_width
        )

        true_path.append(true_pose)
        estimated_path.append(estimated_pose)

    true_x = [pose[0] for pose in true_path]
    true_y = [pose[1] for pose in true_path]
    estimated_x = [pose[0] for pose in estimated_path]
    estimated_y = [pose[1] for pose in estimated_path]

    true_final = true_path[-1]
    estimated_final = estimated_path[-1]

    true_distance_from_start = math.hypot(
        true_final[0], true_final[1]
    )
    estimated_distance_from_start = math.hypot(
        estimated_final[0], estimated_final[1]
    )

    # Verification statements for the claims made by this simulation.
    assert len(true_path) == 9
    assert len(estimated_path) == 9
    assert true_distance_from_start < 1e-9
    assert estimated_distance_from_start > 0.04

    print("Modeled true final position: ({:.4f}, {:.4f}) m".format(
        true_final[0], true_final[1]
    ))
    print("Estimated final position: ({:.4f}, {:.4f}) m".format(
        estimated_final[0], estimated_final[1]
    ))
    print("Modeled true distance from start: {:.6f} m".format(
        true_distance_from_start
    ))
    print("Estimated distance from start: {:.6f} m".format(
        estimated_distance_from_start
    ))

    plt.figure(figsize=(7, 7))
    plt.plot(true_x, true_y, "o--", label="Modeled true path")
    plt.plot(estimated_x, estimated_y, "s-", label="Odometry estimate")
    plt.scatter([0], [0], color="black", label="Start", zorder=5)

    plt.axis("equal")
    plt.xlabel("x position (m)")
    plt.ylabel("y position (m)")
    plt.title("RoboRover: modeled path and odometry drift")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    simulate()
