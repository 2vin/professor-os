def clamp(value, low, high):
    return max(low, min(value, high))


kp = 0.8
error = 0.10
max_speed = 0.60
disturbance_speed = 0.05

requested_speed = kp * error
commanded_speed = clamp(requested_speed, -max_speed, max_speed)
actual_speed = commanded_speed - disturbance_speed

print("Commanded speed:", commanded_speed)
print("Actual speed:", actual_speed)
