# Python 3.7-compatible gear comparison for RoboRover

MOTOR_SPEED_RPM = 180.0
MOTOR_TORQUE_NM = 0.08
EFFICIENCY = 0.85
WHEEL_RADIUS_M = 0.03

GEAR_CHOICES = [
    ("1:1 gear pair", 24, 24),
    ("Moderate reduction", 18, 36),
    ("Strong reduction", 12, 36),
]

def calculate_gear_result(driver_teeth, driven_teeth):
    """Return ratio, output speed, output torque, and wheel-rim force."""
    ratio = float(driven_teeth) / float(driver_teeth)
    output_speed_rpm = MOTOR_SPEED_RPM / ratio
    output_torque_nm = EFFICIENCY * ratio * MOTOR_TORQUE_NM
    wheel_force_n = output_torque_nm / WHEEL_RADIUS_M

    return ratio, output_speed_rpm, output_torque_nm, wheel_force_n


print("RoboRover gear comparison")
print("-" * 72)
print("{:<20s} {:>8s} {:>12s} {:>16s} {:>16s}".format(
    "Choice", "Ratio", "Speed (rpm)", "Torque (N m)", "Wheel-rim force (N)"
))

results = {}

for name, driver_teeth, driven_teeth in GEAR_CHOICES:
    ratio, speed, torque, force = calculate_gear_result(
        driver_teeth, driven_teeth
    )
    results[name] = (ratio, speed, torque, force)

    print("{:<20s} {:>8.2f} {:>12.2f} {:>16.3f} {:>16.2f}".format(
        name, ratio, speed, torque, force
    ))

# Verification checks for the numerical relationships used in this lesson.
assert abs(results["1:1 gear pair"][0] - 1.0) < 1e-9
assert abs(results["Moderate reduction"][0] - 2.0) < 1e-9
assert abs(results["Strong reduction"][0] - 3.0) < 1e-9

assert abs(results["1:1 gear pair"][3] - 2.2666666667) < 1e-9
assert abs(results["Moderate reduction"][3] - 4.5333333333) < 1e-9
assert abs(results["Strong reduction"][1] - 60.0) < 1e-9
assert abs(results["Strong reduction"][2] - 0.204) < 1e-9
assert abs(results["Strong reduction"][3] - 6.8) < 1e-9

print("-" * 72)
print("Verification passed: the 3:1 choice gives 60 rpm,")
print("0.204 N m output torque, and 6.8 N simplified wheel-rim force.")
