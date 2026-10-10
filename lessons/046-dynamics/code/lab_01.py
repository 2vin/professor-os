import math
import matplotlib.pyplot as plt


def simulate(mass_kg, net_force_n, duration_s, dt_s):
    """Simulate constant-force motion from rest using semi-implicit Euler."""
    if mass_kg <= 0.0:
        raise ValueError("mass_kg must be positive")
    if duration_s < 0.0:
        raise ValueError("duration_s must be nonnegative")
    if dt_s <= 0.0:
        raise ValueError("dt_s must be positive")

    times = [0.0]
    positions = [0.0]
    velocities = [0.0]

    position_m = 0.0
    velocity_m_s = 0.0
    acceleration_m_s2 = net_force_n / mass_kg

    full_steps = int(math.floor(duration_s / dt_s + 1e-12))
    remainder_s = duration_s - full_steps * dt_s
    tolerance_s = 1e-12 * max(1.0, duration_s, dt_s)

    step_durations = [dt_s] * full_steps
    if remainder_s > tolerance_s:
        step_durations.append(remainder_s)

    for step_duration_s in step_durations:
        velocity_m_s += acceleration_m_s2 * step_duration_s
        position_m += velocity_m_s * step_duration_s

        next_time_s = times[-1] + step_duration_s
        if abs(next_time_s - duration_s) <= tolerance_s:
            next_time_s = duration_s

        times.append(next_time_s)
        positions.append(position_m)
        velocities.append(velocity_m_s)

    return times, positions, velocities, acceleration_m_s2


def analytic_position(acceleration_m_s2, time_s):
    """Position from rest under constant acceleration."""
    return 0.5 * acceleration_m_s2 * time_s ** 2


def semi_implicit_position_from_rest(acceleration_m_s2, duration_s, dt_s):
    """Expected semi-implicit position, including a possible final partial step."""
    full_steps = int(math.floor(duration_s / dt_s + 1e-12))
    remainder_s = duration_s - full_steps * dt_s

    full_step_position = (
        0.5
        * acceleration_m_s2
        * dt_s ** 2
        * full_steps
        * (full_steps + 1)
    )

    # After the full steps, velocity is a * full_steps * dt_s.
    # Semi-implicit Euler updates velocity for the remainder first,
    # then uses that updated velocity for the position update.
    partial_step_position = (
        acceleration_m_s2
        * full_steps
        * dt_s
        * remainder_s
        + acceleration_m_s2 * remainder_s ** 2
    )

    return full_step_position + partial_step_position


def verify_constant_force_case(
    result,
    mass_kg,
    net_force_n,
    duration_s,
    dt_s
):
    """Verify results using expectations derived from the current parameters."""
    times, positions, velocities, acceleration_m_s2 = result

    expected_acceleration = net_force_n / mass_kg
    expected_velocity = expected_acceleration * duration_s
    expected_analytic_position = analytic_position(
        expected_acceleration, duration_s
    )
    expected_semi_implicit_position = semi_implicit_position_from_rest(
        expected_acceleration, duration_s, dt_s
    )

    assert math.isclose(
        times[-1],
        duration_s,
        rel_tol=0.0,
        abs_tol=1e-12
    )
    assert math.isclose(
        acceleration_m_s2,
        expected_acceleration,
        rel_tol=0.0,
        abs_tol=1e-12
    )
    assert math.isclose(
        velocities[-1],
        expected_velocity,
        rel_tol=0.0,
        abs_tol=1e-12
    )
    assert math.isclose(
        positions[-1],
        expected_semi_implicit_position,
        rel_tol=0.0,
        abs_tol=1e-12
    )
    assert math.isclose(
        analytic_position(acceleration_m_s2, times[-1]),
        expected_analytic_position,
        rel_tol=0.0,
        abs_tol=1e-12
    )


def run_edge_case_tests():
    """Test zero duration and durations shorter than one time step."""
    mass_kg = 15.0
    net_force_n = 24.0
    dt_s = 0.01

    zero_duration = simulate(
        mass_kg, net_force_n, 0.0, dt_s
    )
    verify_constant_force_case(
        zero_duration,
        mass_kg,
        net_force_n,
        0.0,
        dt_s
    )
    assert zero_duration[0] == [0.0]
    assert zero_duration[1] == [0.0]
    assert zero_duration[2] == [0.0]

    short_duration_s = 0.005
    shorter_than_step = simulate(
        mass_kg, net_force_n, short_duration_s, dt_s
    )
    verify_constant_force_case(
        shorter_than_step,
        mass_kg,
        net_force_n,
        short_duration_s,
        dt_s
    )
    assert len(shorter_than_step[0]) == 2
    assert math.isclose(
        shorter_than_step[0][-1],
        short_duration_s,
        rel_tol=0.0,
        abs_tol=1e-12
    )


def main():
    net_force_n = 24.0
    loaded_net_force_n = 24.0
    duration_s = 2.0
    dt_s = 0.01

    light_mass_kg = 12.0
    loaded_mass_kg = 15.0

    light = simulate(
        light_mass_kg, net_force_n, duration_s, dt_s
    )
    loaded = simulate(
        loaded_mass_kg, loaded_net_force_n, duration_s, dt_s
    )

    light_times, light_positions, light_velocities, light_acceleration = light
    loaded_times, loaded_positions, loaded_velocities, loaded_acceleration = loaded

    light_analytic_position = analytic_position(
        light_acceleration, duration_s
    )
    loaded_analytic_position = analytic_position(
        loaded_acceleration, duration_s
    )

    verify_constant_force_case(
        light,
        light_mass_kg,
        net_force_n,
        duration_s,
        dt_s
    )
    verify_constant_force_case(
        loaded,
        loaded_mass_kg,
        loaded_net_force_n,
        duration_s,
        dt_s
    )

    # Verify the exact baseline values reported below.
    assert math.isclose(
        light_acceleration, 2.0, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        loaded_acceleration, 1.6, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        light_velocities[-1], 4.0, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        loaded_velocities[-1], 3.2, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        light_positions[-1], 4.02, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        loaded_positions[-1], 3.216, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        light_analytic_position, 4.0, rel_tol=0.0, abs_tol=1e-12
    )
    assert math.isclose(
        loaded_analytic_position, 3.2, rel_tol=0.0, abs_tol=1e-12
    )

    # Explicitly verify a non-integer duration, zero duration,
    # and a duration shorter than one time step.
    non_integer_duration_s = 2.005
    non_integer_case = simulate(
        loaded_mass_kg,
        loaded_net_force_n,
        non_integer_duration_s,
        dt_s
    )
    verify_constant_force_case(
        non_integer_case,
        loaded_mass_kg,
        loaded_net_force_n,
        non_integer_duration_s,
        dt_s
    )
    run_edge_case_tests()

    print("Light rover acceleration: {:.1f} m/s^2".format(
        light_acceleration
    ))
    print("Loaded rover acceleration: {:.1f} m/s^2".format(
        loaded_acceleration
    ))
    print("Light rover final velocity: {:.1f} m/s".format(
        light_velocities[-1]
    ))
    print("Loaded rover final velocity: {:.1f} m/s".format(
        loaded_velocities[-1]
    ))
    print("Light rover numerical position: {:.3f} m".format(
        light_positions[-1]
    ))
    print("Light rover analytic position: {:.3f} m".format(
        light_analytic_position
    ))
    print("Loaded rover numerical position: {:.3f} m".format(
        loaded_positions[-1]
    ))
    print("Loaded rover analytic position: {:.3f} m".format(
        loaded_analytic_position
    ))
    print("Verified non-integer, zero-duration, and short-duration cases.")
    print("All verification assertions passed.")

    figure, axes = plt.subplots(2, 1, sharex=True)

    axes[0].plot(light_times, light_positions, label="12 kg rover")
    axes[0].plot(
        loaded_times,
        loaded_positions,
        label="15 kg rover with toolbox"
    )
    axes[0].set_ylabel("Position (m)")
    axes[0].set_title("RoboRover: same net force, different mass")
    axes[0].legend()
    axes[0].grid(True)

    axes[1].plot(light_times, light_velocities, label="12 kg rover")
    axes[1].plot(
        loaded_times,
        loaded_velocities,
        label="15 kg rover with toolbox"
    )
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Velocity (m/s)")
    axes[1].legend()
    axes[1].grid(True)

    figure.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
