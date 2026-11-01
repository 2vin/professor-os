duration = 8.0
target_history = []

for step in range(int(duration / 0.02)):
    time = step * 0.02
    target_altitude = 2.0 if time < duration / 2.0 else 1.0
    target_history.append(target_altitude)

assert target_history[0] == 2.0
assert target_history[-1] == 1.0
