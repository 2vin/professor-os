# Class 12: simplified infrared proximity simulation
# Compatible with Python 3.7

def infrared_signal(distance_cm, reflectivity, scale):
    """Return a simplified reflected-IR signal."""
    return scale * reflectivity / (distance_cm ** 2)


def main():
    scale = 100.0
    reflectivity = 0.80
    threshold = 2.0

    distance_cm = 12.0
    step_cm = 1.0
    first_close_distance = None
    steps_taken = 0

    print("distance_cm  signal  decision")

    while distance_cm >= 1.0:
        signal = infrared_signal(distance_cm, reflectivity, scale)

        if signal >= threshold:
            decision = "CLOSE"
            if first_close_distance is None:
                first_close_distance = distance_cm
        else:
            decision = "clear"

        print("{:10.1f}  {:6.2f}  {}".format(
            distance_cm, signal, decision
        ))

        if first_close_distance is not None:
            break

        distance_cm -= step_cm
        steps_taken += 1

    print()
    print("First CLOSE distance: {:.1f} cm".format(first_close_distance))
    print("Steps taken: {}".format(steps_taken))

    # Executable checks for the exact claims made by this simulation.
    assert first_close_distance == 6.0
    assert steps_taken == 6
    assert round(infrared_signal(8.0, reflectivity, scale), 2) == 1.25
    assert round(infrared_signal(6.0, reflectivity, scale), 2) == 2.22


if __name__ == "__main__":
    main()
