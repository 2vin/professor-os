def current_from_resistance(voltage, resistance):
    """Return current in amperes using I = V / R."""
    if voltage < 0:
        raise ValueError("Voltage must be nonnegative.")
    if resistance <= 0:
        raise ValueError("Resistance must be greater than zero.")
    return voltage / resistance


def resistor_power(voltage, resistance):
    """Return resistor power in watts using P = V^2 / R."""
    if voltage < 0:
        raise ValueError("Voltage must be nonnegative.")
    if resistance <= 0:
        raise ValueError("Resistance must be greater than zero.")
    return voltage * voltage / resistance


def compare_with_exercise_limit(current, limit=0.05):
    """Compare current with a classroom exercise threshold."""
    if current > limit:
        return "above the {:.3f} A exercise threshold".format(limit)
    return "at or below the {:.3f} A exercise threshold".format(limit)


def main():
    voltage = 5.0
    exercise_threshold = 0.05
    resistances = [100, 200, 220, 500, 1000, 10000]

    assert abs(current_from_resistance(5.0, 100) - 0.05) < 1e-12
    assert abs(current_from_resistance(5.0, 1000) - 0.005) < 1e-12
    assert abs(resistor_power(5.0, 100) - 0.25) < 1e-12

    try:
        current_from_resistance(-1.0, 100.0)
    except ValueError:
        pass
    else:
        raise AssertionError("Negative voltage must be rejected.")

    print("RoboRover resistor-branch simulation")
    print("Supply voltage: {:.1f} V".format(voltage))
    print("Exercise threshold: {:.3f} A".format(exercise_threshold))
    print()

    for resistance in resistances:
        current = current_from_resistance(voltage, resistance)
        power = resistor_power(voltage, resistance)
        print("{:>5} ohms -> {:.2f} mA, {:.4f} W: {}".format(
            resistance,
            current * 1000.0,
            power,
            compare_with_exercise_limit(current, exercise_threshold)))


if __name__ == "__main__":
    main()
