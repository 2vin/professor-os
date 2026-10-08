import math
import matplotlib.pyplot as plt


BOUNDARY_TOLERANCE = 1e-9


def classify_workspace(distance, link_1, link_2,
                       tolerance=BOUNDARY_TOLERANCE):
    """Describe whether a target is interior or on a radial boundary."""
    outer_radius = link_1 + link_2
    inner_radius = abs(link_1 - link_2)

    at_outer = abs(distance - outer_radius) <= tolerance
    at_inner = abs(distance - inner_radius) <= tolerance

    if at_outer:
        return "outer boundary: fully stretched"

    if at_inner and link_1 == link_2:
        return (
            "equal-link inner boundary at the shoulder: "
            "orientation-degenerate family"
        )

    if at_inner:
        return "inner boundary: fully folded"

    return "interior"


def inverse_kinematics(x, y, link_1, link_2):
    """Return distinct representative planar IK solutions in radians."""
    if link_1 <= 0.0 or link_2 <= 0.0:
        raise ValueError("Link lengths must be positive.")

    distance_squared = x * x + y * y
    distance = math.sqrt(distance_squared)
    inner_radius = abs(link_1 - link_2)
    outer_radius = link_1 + link_2

    if distance > outer_radius + BOUNDARY_TOLERANCE:
        raise ValueError("Target is outside the arm's maximum reach.")

    if distance < inner_radius - BOUNDARY_TOLERANCE:
        raise ValueError("Target is inside the arm's unreachable inner region.")

    workspace_status = classify_workspace(
        distance, link_1, link_2
    )

    if workspace_status != "interior":
        print("Workspace status: {}".format(workspace_status))

    cosine_elbow = (
        distance_squared - link_1 * link_1 - link_2 * link_2
    ) / (2.0 * link_1 * link_2)

    # Floating-point rounding can produce a value such as 1.0000000002.
    cosine_elbow = max(-1.0, min(1.0, cosine_elbow))

    elbow_magnitude = math.acos(cosine_elbow)
    candidates = []

    for elbow_angle in (elbow_magnitude, -elbow_magnitude):
        shoulder_angle = (
            math.atan2(y, x)
            - math.atan2(
                link_2 * math.sin(elbow_angle),
                link_1 + link_2 * math.cos(elbow_angle)
            )
        )
        candidates.append((shoulder_angle, elbow_angle))

    # At the outer boundary and at an unequal-link inner boundary,
    # the two candidates describe the same geometric arm. Keep one
    # representative solution. For equal links at the shoulder,
    # this representative suppresses an infinite orientation family;
    # it is not a unique physical solution.
    solutions = []
    for candidate in candidates:
        candidate_points = forward_kinematics(
            candidate[0], candidate[1], link_1, link_2
        )
        duplicate = False

        for existing in solutions:
            existing_points = forward_kinematics(
                existing[0], existing[1], link_1, link_2
            )
            elbow_error = math.hypot(
                candidate_points[0][0] - existing_points[0][0],
                candidate_points[0][1] - existing_points[0][1]
            )
            tip_error = math.hypot(
                candidate_points[1][0] - existing_points[1][0],
                candidate_points[1][1] - existing_points[1][1]
            )

            if elbow_error < BOUNDARY_TOLERANCE and \
                    tip_error < BOUNDARY_TOLERANCE:
                duplicate = True
                break

        if not duplicate:
            solutions.append(candidate)

    return solutions


def forward_kinematics(shoulder_angle, elbow_angle, link_1, link_2):
    """Return the elbow and tip coordinates in metres."""
    elbow_x = link_1 * math.cos(shoulder_angle)
    elbow_y = link_1 * math.sin(shoulder_angle)

    tip_x = (
        elbow_x
        + link_2 * math.cos(shoulder_angle + elbow_angle)
    )
    tip_y = (
        elbow_y
        + link_2 * math.sin(shoulder_angle + elbow_angle)
    )

    return (elbow_x, elbow_y), (tip_x, tip_y)


def degrees(angle_radians):
    return angle_radians * 180.0 / math.pi


def classify_branch(elbow, target):
    """Classify the elbow relative to the shoulder-target line."""
    signed_cross_product = (
        target[0] * elbow[1] - target[1] * elbow[0]
    )

    if signed_cross_product > BOUNDARY_TOLERANCE:
        return "elbow-up"
    if signed_cross_product < -BOUNDARY_TOLERANCE:
        return "elbow-down"
    return "boundary configuration"


def plot_solution(solution, link_1, link_2, target, number):
    shoulder_angle, elbow_angle = solution
    elbow, tip = forward_kinematics(
        shoulder_angle, elbow_angle, link_1, link_2
    )
    branch = classify_branch(elbow, target)

    x_values = [0.0, elbow[0], tip[0]]
    y_values = [0.0, elbow[1], tip[1]]

    # Line style and labels communicate branch identity in addition
    # to color, which improves accessibility.
    line_styles = ["-", "--"]
    line_style = line_styles[(number - 1) % len(line_styles)]

    plt.plot(
        x_values,
        y_values,
        marker="o",
        linestyle=line_style,
        linewidth=3,
        label="Solution {} ({})".format(number, branch)
    )

    print(
        "Solution {} ({}): shoulder={:.2f} degrees, "
        "elbow={:.2f} degrees".format(
            number,
            branch,
            degrees(shoulder_angle),
            degrees(elbow_angle)
        )
    )
    print(
        "  elbow: ({:.3f} m, {:.3f} m)".format(
            elbow[0], elbow[1]
        )
    )
    print(
        "  calculated tip: ({:.3f} m, {:.3f} m)".format(
            tip[0], tip[1]
        )
    )

    # Verification: the calculated tip must be very close to the target.
    error = math.sqrt(
        (tip[0] - target[0]) ** 2
        + (tip[1] - target[1]) ** 2
    )
    assert error < 1e-9


def main():
    link_1 = 0.60
    link_2 = 0.40
    target = (0.70, 0.30)

    solutions = inverse_kinematics(
        target[0], target[1], link_1, link_2
    )

    # This verifies that the chosen interior target has two distinct
    # mathematical configurations.
    assert len(solutions) == 2

    # Verify the numerical values used in the worked example.
    angle_pairs_degrees = [
        (degrees(solution[0]), degrees(solution[1]))
        for solution in solutions
    ]
    rounded_pairs = [
        (round(pair[0], 1), round(pair[1], 1))
        for pair in angle_pairs_degrees
    ]
    assert (-8.2, 82.8) in rounded_pairs
    assert (54.6, -82.8) in rounded_pairs

    # Explicitly verify Target B from the activity.
    target_b = (0.20, 0.90)
    target_b_distance = math.hypot(target_b[0], target_b[1])
    assert abs(target_b_distance - math.sqrt(0.85)) < 1e-12
    assert abs(target_b_distance - 0.9219544457) < 1e-10

    target_b_solutions = inverse_kinematics(
        target_b[0], target_b[1], link_1, link_2
    )
    assert len(target_b_solutions) == 2
    print(
        "Target B distance: {:.3f} m; distinct solutions: {}".format(
            target_b_distance, len(target_b_solutions)
        )
    )

    plt.figure(figsize=(8, 6))

    for index, solution in enumerate(solutions, start=1):
        plot_solution(solution, link_1, link_2, target, index)

    reach = link_1 + link_2
    inner_radius = abs(link_1 - link_2)
    circle_angles = [
        2.0 * math.pi * i / 200.0 for i in range(201)
    ]

    outer_circle_x = [
        reach * math.cos(angle) for angle in circle_angles
    ]
    outer_circle_y = [
        reach * math.sin(angle) for angle in circle_angles
    ]

    plt.plot(
        outer_circle_x,
        outer_circle_y,
        linestyle="--",
        color="gray",
        label="Maximum reach"
    )

    if inner_radius > 0.0:
        inner_circle_x = [
            inner_radius * math.cos(angle) for angle in circle_angles
        ]
        inner_circle_y = [
            inner_radius * math.sin(angle) for angle in circle_angles
        ]
        plt.plot(
            inner_circle_x,
            inner_circle_y,
            linestyle=":",
            color="gray",
            label="Inner exclusion boundary"
        )

    plt.scatter(
        [target[0]],
        [target[1]],
        color="red",
        s=80,
        zorder=5,
        label="Target"
    )

    plt.axhline(0.0, color="black", linewidth=0.5)
    plt.axvline(0.0, color="black", linewidth=0.5)
    plt.xlabel("x position (m)")
    plt.ylabel("y position (m)")
    plt.title("RoboRover: two inverse-kinematics solutions")
    plt.axis("equal")
    plt.grid(True)
    plt.legend()
    plt.show()


if __name__ == "__main__":
    main()
