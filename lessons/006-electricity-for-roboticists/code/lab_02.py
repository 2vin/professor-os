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


def interactive_calculation():
    try:
        voltage = float(input("Enter voltage in volts: "))
        resistance = float(input("Enter resistance in ohms: "))

        current = current_from_resistance(voltage, resistance)
        power = resistor_power(voltage, resistance)

        print("Current: {:.6f} A ({:.2f} mA)".format(
            current, current * 1000.0))
        print("Resistor power: {:.6f} W".format(power))

    except EOFError:
        print("No input was provided; run this extension interactively.")
    except ValueError as error:
        print("Input error: {}".format(error))


if __name__ == "__main__":
    interactive_calculation()
