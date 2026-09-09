import math

noise = 0.005 * math.sin(40.0 * 1.0)
expected_noise = 0.005 * math.sin(40.0)
assert abs(noise - expected_noise) < 1e-15
print("Repeatable measurement disturbance: {:.6f} m".format(noise))
