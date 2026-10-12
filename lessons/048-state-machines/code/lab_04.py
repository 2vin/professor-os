transitions = {
    ("DRIVE", "obstacle_detected"): "STOP",
    ("STOP", "path_clear"): "DRIVE",
}

state = "DRIVE"
event = "obstacle_detected"

# This small standalone example uses the same transition idea.
if (state, event) == ("DRIVE", "obstacle_detected"):
    next_state = "STOP"
elif (state, event) == ("STOP", "path_clear"):
    next_state = "DRIVE"
else:
    next_state = state

assert next_state == "STOP"
print(next_state)
