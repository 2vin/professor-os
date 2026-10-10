mass_kg = 15.0
duration_s = 2.0
dt_s = 0.01
switch_time_s = 1.0
times = [0.0]
position_m = 0.0
velocity_m_s = 0.0
positions_m = [position_m]
velocities_m_s = [velocity_m_s]

while times[-1] < duration_s:
    current_time_s = times[-1]
    step_duration_s = min(dt_s, duration_s - current_time_s)

    # Split a step if it would cross the force-switch boundary.
    time_to_switch_s = switch_time_s - current_time_s
    if current_time_s < switch_time_s and time_to_switch_s < step_duration_s:
        step_duration_s = time_to_switch_s

    if current_time_s < switch_time_s:
        current_force_n = 15.0
    else:
        current_force_n = -10.0

    current_acceleration_m_s2 = current_force_n / mass_kg
    velocity_m_s += current_acceleration_m_s2 * step_duration_s
    position_m += velocity_m_s * step_duration_s

    times.append(current_time_s + step_duration_s)
    positions_m.append(position_m)
    velocities_m_s.append(velocity_m_s)

assert abs(times[-1] - duration_s) <= 1e-12
assert velocities_m_s[100] > 0.0
assert velocities_m_s[-1] < velocities_m_s[100]

print("Final time: {:.2f} s".format(times[-1]))
print("Final position: {:.3f} m".format(position_m))
print("Final velocity: {:.3f} m/s".format(velocity_m_s))
print("Braking simulation checks passed.")
