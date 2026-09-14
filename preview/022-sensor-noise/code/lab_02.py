alpha = 0.25
reading = 101.0
previous = 100.0
new_value = alpha * reading + (1.0 - alpha) * previous

assert abs(new_value - 100.25) < 1e-9
print("Filtered value:", new_value)
