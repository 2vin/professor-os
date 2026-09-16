x_old = 10.0
p_old = 4.0
velocity = 1.2
dt = 2.0
process_variance = 1.0
measurement = 11.0
measurement_variance = 4.0

x_pred = x_old + velocity * dt
p_pred = p_old + process_variance
gain = p_pred / (p_pred + measurement_variance)
innovation = measurement - x_pred
x_new = x_pred + gain * innovation
p_new = (1.0 - gain) * p_pred

assert abs(x_pred - 12.4) < 1e-12
assert abs(p_pred - 5.0) < 1e-12
assert abs(gain - (5.0 / 9.0)) < 1e-12
assert abs(innovation - (-1.4)) < 1e-12
assert abs(x_new - (104.6 / 9.0)) < 1e-12
assert abs(p_new - (20.0 / 9.0)) < 1e-12

print("Predicted position:", x_pred, "m")
print("Corrected position:", x_new, "m")
print("Corrected variance:", p_new, "m^2")
