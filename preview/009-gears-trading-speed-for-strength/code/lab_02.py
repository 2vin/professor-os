# Python 3.7-compatible gear-selection game

MOTOR_SPEED_RPM = 180.0
MOTOR_TORQUE_NM = 0.08
EFFICIENCY = 0.85
WHEEL_RADIUS_M = 0.03
REQUIRED_FORCE_N = 5.0

GEARS = {
    "1": ("1:1 gear pair", 24, 24),
    "2": ("Moderate reduction", 18, 36),
    "3": ("Strong reduction", 12, 36),
}

def result_for(driver_teeth, driven_teeth):
    ratio = float(driven_teeth) / float(driver_teeth)
    speed_rpm = MOTOR_SPEED_RPM / ratio
    torque_nm = EFFICIENCY * ratio * MOTOR_TORQUE_NM
    force_n = torque_nm / WHEEL_RADIUS_M
    return ratio, speed_rpm, torque_nm, force_n

print("RoboRover's Ramp Challenge")
print("Required simplified wheel-rim force: {:.1f} N".format(
    REQUIRED_FORCE_N
))
print()

qualifying_choices = []

for key in sorted(GEARS.keys()):
    name, driver, driven = GEARS[key]
    ratio, speed, torque, force = result_for(driver, driven)
    qualifies = force >= REQUIRED_FORCE_N

    if qualifies:
        qualifying_choices.append(key)

    print("{}: {:20s} | ratio {:.1f}:1 | speed {:6.1f} rpm | "
          "force {:4.2f} N | qualifies: {}".format(
              key, name, ratio, speed, force, qualifies
          ))

try:
    choice = input("\nChoose gear 1, 2, or 3: ").strip()
except EOFError:
    choice = "2"
    print("\nNo interactive input was available; demonstrating choice 2.")

if choice not in GEARS:
    print("Please run the program again and choose 1, 2, or 3.")
else:
    name, driver, driven = GEARS[choice]
    ratio, speed, torque, force = result_for(driver, driven)

    if force >= REQUIRED_FORCE_N:
        print("RoboRover meets the simplified force requirement.")
        print("Its predicted speed is {:.1f} rpm.".format(speed))
    else:
        print("RoboRover does not meet the simplified force requirement.")
        print("Its predicted wheel-rim force is {:.2f} N.".format(force))

# Check the calculations and the selection conclusion.
assert abs(result_for(24, 24)[3] - 2.2666666667) < 1e-9
assert abs(result_for(18, 36)[0] - 2.0) < 1e-9
assert abs(result_for(18, 36)[3] - 4.5333333333) < 1e-9
assert abs(result_for(12, 36)[0] - 3.0) < 1e-9
assert abs(result_for(12, 36)[1] - 60.0) < 1e-9
assert abs(result_for(12, 36)[2] - 0.204) < 1e-9
assert abs(result_for(12, 36)[3] - 6.8) < 1e-9

# Only choice 3 reaches 5.0 N in this simplified model.
assert qualifying_choices == ["3"]
assert result_for(12, 36)[1] > 0.0
