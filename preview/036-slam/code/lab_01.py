import math

TRUE_LANDMARKS = {
    "A": 3.0,
    "B": 7.0,
    "C": 11.0,
}

TRUE_PATH = list(range(13))
ODOMETRY_STEP = 1.1
SENSOR_RANGE = 2.2

# Keep this True for the supplied baseline settings.
# Set it to False before changing ODOMETRY_STEP, SENSOR_RANGE, or TRUE_PATH.
RUN_BASELINE_TESTS = True


def visible_landmarks(true_x, sensor_range):
    """Return the closest visible landmark, with deterministic tie-breaking."""
    candidates = []

    for name, landmark_x in TRUE_LANDMARKS.items():
        distance = abs(landmark_x - true_x)
        if distance <= sensor_range:
            candidates.append((distance, -landmark_x, name, landmark_x))

    if not candidates:
        return []

    _, _, name, landmark_x = min(candidates)
    relative_x = landmark_x - true_x
    return [(name, relative_x)]


def run_simulation(true_path, odometry_step, sensor_range):
    """Run the conceptual landmark-localization simulation."""
    estimated_x = 0.0
    landmark_map = {}
    history = []

    for step_number, true_x in enumerate(true_path):
        if step_number > 0:
            estimated_x += odometry_step

        observations = visible_landmarks(true_x, sensor_range)

        for name, relative_x in observations:
            if name not in landmark_map:
                landmark_map[name] = estimated_x + relative_x
            else:
                estimated_x = landmark_map[name] - relative_x

        history.append((true_x, estimated_x))

    return history, landmark_map


history, landmark_map = run_simulation(
    TRUE_PATH,
    ODOMETRY_STEP,
    SENSOR_RANGE,
)

final_true_x, final_estimated_x = history[-1]
final_error = abs(final_estimated_x - final_true_x)

print("Mapped landmark names:", sorted(landmark_map.keys()))
print("Mapped landmark positions: {}".format(
    {name: round(landmark_map[name], 1)
     for name in sorted(landmark_map)}
))
print("Final true position: {:.1f} m".format(final_true_x))
print("Final estimated position: {:.1f} m".format(final_estimated_x))
print("Final absolute error: {:.1f} m".format(final_error))

# These checks always verify structural invariants and therefore remain
# useful when students change the parameters.
assert set(landmark_map).issubset(set(TRUE_LANDMARKS))
assert len(history) == len(TRUE_PATH)
assert final_error >= 0.0

# These checks apply only to the documented baseline configuration.
if RUN_BASELINE_TESTS:
    assert sorted(landmark_map.keys()) == ["A", "B", "C"]
    assert math.isclose(landmark_map["A"], 3.1, abs_tol=1e-9)
    assert math.isclose(landmark_map["B"], 7.2, abs_tol=1e-9)
    assert math.isclose(landmark_map["C"], 11.3, abs_tol=1e-9)
    assert final_true_x == 12
    assert math.isclose(final_estimated_x, 12.3, abs_tol=1e-9)
    assert math.isclose(final_error, 0.3, abs_tol=1e-9)
    print("Verification: all baseline values passed.")
