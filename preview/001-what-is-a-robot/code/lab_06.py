commands = [1, 1, 0, -1]
speed_m_per_s = 0.60
command_time_s = 2.0
total_distance_m = 0.0

for command in commands:
    total_distance_m += abs(command) * speed_m_per_s * command_time_s

print("Total distance traveled: {:.1f} m".format(total_distance_m))
assert abs(total_distance_m - 3.6) < 1e-9
