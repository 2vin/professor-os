position = 0.8
command_speed = 0.4
time_step = 0.5

position = position + command_speed * time_step

print("New position: {:.1f} m".format(position))
