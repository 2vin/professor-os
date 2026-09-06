STEPS = 6
sensor_states = [
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (0, 1, 0),
    (0, 0, 0),
    (0, 1, 0),
]

state_names = []
steering_commands = []
previous_steering = -1

for left, center, right in sensor_states:
    if center or (left and right):
        state = "straight"
        steering = 0
    elif left:
        state = "left"
        steering = -1
    elif right:
        state = "right"
        steering = 1
    else:
        state = "lost_line"
        steering = previous_steering

    state_names.append(state)
    steering_commands.append(steering)
    previous_steering = steering

left_count = state_names.count("left")
straight_count = state_names.count("straight")
right_count = state_names.count("right")
lost_line_count = state_names.count("lost_line")

assert len(state_names) == STEPS
assert left_count + straight_count + right_count + lost_line_count == STEPS
assert lost_line_count == 1

print("Left:", left_count)
print("Straight:", straight_count)
print("Right:", right_count)
print("Lost line:", lost_line_count)
