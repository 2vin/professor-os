def run_simulation(true_path, odometry_step, sensor_range):
    """Run the conceptual simulation for forward or backward motion."""
    estimated_x = 0.0
    landmark_map = {}
    history = []
    previous_true_x = None

    for true_x in true_path:
        if previous_true_x is not None:
            direction = 1.0 if true_x > previous_true_x else -1.0
            estimated_x += direction * odometry_step

        for name, relative_x in visible_landmarks(true_x, sensor_range):
            if name not in landmark_map:
                landmark_map[name] = estimated_x + relative_x
            else:
                estimated_x = landmark_map[name] - relative_x

        history.append((true_x, estimated_x))
        previous_true_x = true_x

    return history, landmark_map
