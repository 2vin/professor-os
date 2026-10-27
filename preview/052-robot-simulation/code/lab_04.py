def simulate(sensor_bias):
    wall_position = 2.0
    time_step = 0.5
    forward_speed = 0.4
    stop_distance = 0.7
    position = 0.0

    while True:
        true_distance = wall_position - position
        measured_distance = max(0.0, true_distance + sensor_bias)

        if measured_distance > stop_distance:
            command_speed = forward_speed
        else:
            command_speed = 0.0

        position = position + command_speed * time_step

        if command_speed == 0.0:
            return position


biased_run = simulate(sensor_bias=0.1)
print("Final position with positive sensor bias: {:.2f} m".format(biased_run))
