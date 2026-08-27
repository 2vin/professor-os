# Python 3.7-compatible RoboRover feedback simulation

target_distance = 0.30       # metres
distance = 0.60               # metres; true starting distance
time_step = 1.0               # seconds
forward_speed = 0.10          # metres per second
tolerance = 0.02              # metres

# A simple, repeatable sensor-error sequence.
sensor_errors = [0.00, 0.01, -0.01, 0.01, 0.00, -0.01]

move_count = 0
history = []

for step in range(len(sensor_errors)):
    measured_distance = distance + sensor_errors[step]
    error = measured_distance - target_distance

    if error > tolerance:
        command = "FORWARD"
        distance -= forward_speed * time_step
        move_count += 1
    else:
        command = "STOP"

    history.append((step, distance, measured_distance, error, command))

print("step | true_m | measured_m | error_m | command")
for record in history:
    step, true_distance, measured, error, command = record
    print("{:4d} | {:6.2f} | {:10.2f} | {:7.2f} | {}".format(
        step, true_distance, measured, error, command
    ))

print("forward commands:", move_count)
print("final true distance: {:.2f} m".format(distance))

# Executable checks for the claims made by this simulation.
assert move_count == 3
assert abs(distance - 0.30) < 1e-9
assert history[3][4] == "STOP"
assert abs(history[3][2] - 0.31) < 1e-9
