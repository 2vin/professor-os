# Educational velocity estimate from successive altitude measurements.
dt = 0.02
measured_altitudes = [0.00, 0.04, 0.09, 0.13, 0.16, 0.18, 0.19]

alpha = 0.2
estimated_velocity = 0.0
previous_measurement = measured_altitudes[0]
estimated_velocities = [estimated_velocity]

for measurement in measured_altitudes[1:]:
    raw_velocity = (measurement - previous_measurement) / dt
    estimated_velocity = (
        alpha * raw_velocity
        + (1.0 - alpha) * estimated_velocity
    )
    estimated_velocities.append(estimated_velocity)
    previous_measurement = measurement

assert len(estimated_velocities) == len(measured_altitudes)
print("Estimated velocity samples:", len(estimated_velocities))
