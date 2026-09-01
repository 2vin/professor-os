import math
import matplotlib.pyplot as plt


def pwm_average_voltage(supply_voltage, duty_cycle):
    """Return the ideal average of a 0-to-supply PWM waveform."""
    if supply_voltage < 0:
        raise ValueError("supply_voltage must not be negative")
    if duty_cycle < 0 or duty_cycle > 1:
        raise ValueError("duty_cycle must be between 0 and 1")
    return supply_voltage * duty_cycle


def make_pwm_waveform(supply_voltage, duty_cycle, frequency, duration,
                      sample_count):
    """Create samples for an idealized power-stage voltage waveform."""
    if frequency <= 0:
        raise ValueError("frequency must be positive")
    if duration <= 0:
        raise ValueError("duration must be positive")
    if sample_count <= 1:
        raise ValueError("sample_count must be greater than 1")
    if supply_voltage < 0:
        raise ValueError("supply_voltage must not be negative")
    if duty_cycle < 0 or duty_cycle > 1:
        raise ValueError("duty_cycle must be between 0 and 1")

    times = []
    voltages = []
    period = 1.0 / frequency

    for index in range(sample_count):
        time = duration * index / (sample_count - 1)
        phase = time % period
        voltage = (supply_voltage
                   if phase < duty_cycle * period else 0.0)
        times.append(time)
        voltages.append(voltage)

    return times, voltages


def simulate_motor_speed(duty_cycle, duration, dt, maximum_speed,
                         time_constant):
    """Simulate a stable first-order illustrative response."""
    if duty_cycle < 0 or duty_cycle > 1:
        raise ValueError("duty_cycle must be between 0 and 1")
    if duration <= 0 or dt <= 0:
        raise ValueError("duration and dt must be positive")
    if maximum_speed < 0:
        raise ValueError("maximum_speed must not be negative")
    if time_constant <= 0:
        raise ValueError("time_constant must be positive")
    if dt > time_constant:
        raise ValueError("dt must be no greater than time_constant")

    times = []
    speeds = []
    speed = 0.0
    target_speed = duty_cycle * maximum_speed
    steps = int(round(duration / dt))

    for step in range(steps + 1):
        time = step * dt
        times.append(time)
        speeds.append(speed)
        speed += (target_speed - speed) * dt / time_constant

    return times, speeds


def main():
    print("RoboRover PWM experiment")
    print("Enter a duty cycle from 0 to 100 percent.")

    try:
        user_text = input("Duty cycle: ")
    except EOFError:
        user_text = "40"
        print("No input received; using 40 percent.")

    duty_percent = float(user_text)
    if duty_percent < 0 or duty_percent > 100:
        raise ValueError("Enter a percentage from 0 to 100.")

    duty_cycle = duty_percent / 100.0
    supply_voltage = 9.0
    frequency = 50.0
    duration = 1.0
    dt = 0.01
    maximum_speed = 3000.0
    time_constant = 0.20

    average_voltage = pwm_average_voltage(supply_voltage, duty_cycle)

    assert math.isclose(
        pwm_average_voltage(9.0, 0.40), 3.6,
        rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        0.40 * (1.0 / 50.0), 0.008,
        rel_tol=0.0, abs_tol=1e-12
    )

    check_times, check_speeds = simulate_motor_speed(
        1.0, time_constant, dt, 1.0, time_constant
    )
    one_tau_fraction = check_speeds[-1]
    assert 0.63 < one_tau_fraction < 0.65

    pwm_times, pwm_voltages = make_pwm_waveform(
        supply_voltage, duty_cycle, frequency, 0.20, 1000
    )
    speed_times, speeds = simulate_motor_speed(
        duty_cycle, duration, dt, maximum_speed, time_constant
    )

    target_speed = duty_cycle * maximum_speed
    print("Ideal average power-stage voltage representation: {:.2f} V".format(
        average_voltage
    ))
    print("Model target speed: {:.0f} rpm".format(target_speed))
    print("At one time constant, the normalized model response is {:.1%}."
          .format(one_tau_fraction))
    print("The graph shows speed approaching the target gradually.")

    figure, axes = plt.subplots(2, 1, figsize=(9, 6), sharex=False)

    axes[0].plot(pwm_times, pwm_voltages, color="darkorange")
    axes[0].set_title("Idealized power-stage PWM voltage representation")
    axes[0].set_ylabel("Voltage representation (V)")
    axes[0].set_xlabel("Time (s)")
    axes[0].grid(True)

    axes[1].plot(speed_times, speeds, color="navy")
    axes[1].axhline(
        target_speed, color="gray", linestyle="--", label="model target"
    )
    axes[1].set_title("Illustrative command-response model")
    axes[1].set_ylabel("Model speed (rpm)")
    axes[1].set_xlabel("Time (s)")
    axes[1].legend()
    axes[1].grid(True)

    figure.tight_layout()

    try:
        plt.show()
    except Exception as error:
        figure.savefig("pwm_motor_response.png", dpi=150)
        print("Graphical display unavailable: {}".format(error))
        print("Saved the figure as pwm_motor_response.png")


if __name__ == "__main__":
    main()
