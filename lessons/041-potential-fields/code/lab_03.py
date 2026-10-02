import numpy as np

force = np.array([3.0, 4.0])
position = np.array([1.0, 1.0])
step_size = 0.08

direction = force / np.linalg.norm(force)
position = position + step_size * direction

assert abs(np.linalg.norm(direction) - 1.0) < 1e-12
assert abs(np.linalg.norm(position - np.array([1.0, 1.0]))
           - step_size) < 1e-12

print("Direction:", direction)
print("Updated position:", position)
print("Verified movement distance:", step_size)
