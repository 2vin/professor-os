# Python 3.7
TARGET = 0.0
THRESHOLD = 2.0
STEP_SIZE = 0.8

sensor_noise = [0.4, -0.4, -0.4, -0.4, -0.4,
                -0.4, -0.4, -0.4, -0.4, -0.4]

actual_position = 6.0
history = []

for step_number, noise in enumerate(sensor_noise):
    measured_position = actual_position + noise
    error = TARGET - measured_position

    if measured_position > THRESHOLD:
        steering_command = -1
        action = "left"
    elif measured_position < -THRESHOLD:
        steering_command = 1
        action = "right"
    else:
        steering_command = 0
        action = "straight"

    history.append({
        "step": step_number,
        "actual": actual_position,
        "measured": measured_position,
        "error": error,
        "action": action
    })

    actual_position += STEP_SIZE * steering_command

print("step | actual | measured | error  | action")
print("-------------------------------------------")
for row in history:
    print("{:>4} | {:>6.2f} | {:>8.2f} | {:>6.2f} | {}".format(
        row["step"], row["actual"], row["measured"],
        row["error"], row["action"]
    ))

print("Final position: {:.2f} cm".format(actual_position))

assert len(history) == 10
assert [row["action"] for row in history] == ["left"] * 5 + ["straight"] * 5
assert abs(actual_position - 2.0) < 1e-9
assert abs(actual_position - TARGET) < abs(6.0 - TARGET)

print("Verified: 10 measurements, 5 left, 5 straight, final = 2.00 cm.")
