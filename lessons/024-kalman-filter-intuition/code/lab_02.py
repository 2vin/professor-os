import random
import math
import matplotlib.pyplot as plt


def kalman_update(estimate, variance, motion, process_variance,
                  measurement, measurement_variance):
    """Perform one prediction-and-correction cycle."""
    predicted_estimate = estimate + motion
    predicted_variance = variance + process_variance

    gain = predicted_variance / (
        predicted_variance + measurement_variance
    )

    innovation = measurement - predicted_estimate
    corrected_estimate = predicted_estimate + gain * innovation
    corrected_variance = (1.0 - gain) * predicted_variance

    return corrected_estimate, corrected_variance, gain


def main():
    random_generator = random.Random(24)

    steps = 30
    true_position = 0.0
    estimate = 0.0
    variance = 1.0

    true_positions = []
    measurements = []
    estimates = []
    gains = []

    commanded_motion = 0.8
    process_variance = 0.12
    measurement_variance = 1.44
    measurement_standard_deviation = math.sqrt(measurement_variance)

    for step in range(steps):
        # The simulated world moves by a mostly steady amount.
        true_position += commanded_motion

        # The sensor reports the true position plus random measurement noise.
        noise = random_generator.gauss(
            0.0, measurement_standard_deviation
        )
        measurement = true_position + noise

        # The filter predicts from motion, then corrects with the measurement.
        estimate, variance, gain = kalman_update(
            estimate,
            variance,
            commanded_motion,
            process_variance,
            measurement,
            measurement_variance
        )

        true_positions.append(true_position)
        measurements.append(measurement)
        estimates.append(estimate)
        gains.append(gain)

    assert len(true_positions) == steps
    assert len(measurements) == steps
    assert len(estimates) == steps
    assert len(gains) == steps
    assert all(0.0 < gain < 1.0 for gain in gains)
    assert variance > 0.0

    time_steps = list(range(1, steps + 1))

    plt.figure(figsize=(10, 5))
    plt.plot(
        time_steps,
        true_positions,
        label="Hidden true position",
        linewidth=2
    )
    plt.scatter(
        time_steps,
        measurements,
        label="Noisy sensor measurements",
        color="tab:red",
        alpha=0.65
    )
    plt.plot(
        time_steps,
        estimates,
        label="Kalman estimate",
        color="tab:green",
        linewidth=2
    )
    plt.xlabel("Update number")
    plt.ylabel("Position (m)")
    plt.title("RoboRover: prediction plus correction")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

    print("The program completed", steps, "filter updates.")
    print("Last Kalman gain:", gains[-1])
    print("Last estimated position (m):", estimates[-1])


if __name__ == "__main__":
    main()
