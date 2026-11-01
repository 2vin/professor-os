duration = 8.0
time = 0.0
target_altitude = 2.0 if time < duration / 2.0 else 1.0
assert target_altitude == 2.0
