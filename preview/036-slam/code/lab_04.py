import matplotlib.pyplot as plt

TRUE_LANDMARKS = {
    "A": 3.0,
    "B": 7.0,
    "C": 11.0,
}

TRUE_PATH = list(range(13))
ODOMETRY_STEP = 1.1
SENSOR_RANGE = 2.2


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
    return [(name, landmark_x - true_x)]


def run_simulation(true_path, odometry_step, sensor_range):
    estimated_x = 0.0
    landmark_map = {}
    history = []

    for step_number, true_x in enumerate(true_path):
        if step_number > 0:
            estimated_x += odometry_step

        for name, relative_x in visible_landmarks(true_x, sensor_range):
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

steps = list(range(len(history)))
true_positions = [item[0] for item in history]
estimated_positions = [item[1] for item in history]

plt.figure()
plt.plot(
    steps,
    true_positions,
    linestyle="-",
    marker="o",
    label="True position",
)
plt.plot(
    steps,
    estimated_positions,
    linestyle="--",
    marker="x",
    label="Estimated position",
)
plt.xlabel("Step")
plt.ylabel("Position (m)")
plt.title("Position estimate over time")
plt.legend()
plt.tight_layout()

plt.figure()
landmark_names = sorted(landmark_map.keys())
map_positions = [landmark_map[name] for name in landmark_names]
true_positions_for_map = [TRUE_LANDMARKS[name] for name in landmark_names]

plt.plot(
    landmark_names,
    true_positions_for_map,
    linestyle="",
    marker="o",
    label="True landmark position",
)
plt.plot(
    landmark_names,
    map_positions,
    linestyle="",
    marker="x",
    label="Estimated map position",
)
for name, true_position, estimated_position in zip(
    landmark_names,
    true_positions_for_map,
    map_positions,
):
    plt.annotate(
        "true {}".format(true_position),
        (name, true_position),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
    )
    plt.annotate(
        "map {:.1f}".format(estimated_position),
        (name, estimated_position),
        textcoords="offset points",
        xytext=(0, -14),
        ha="center",
    )

plt.xlabel("Landmark")
plt.ylabel("Position along hallway (m)")
plt.title("Landmark positions: physical world and estimated map")
plt.legend()
plt.tight_layout()
plt.show()
