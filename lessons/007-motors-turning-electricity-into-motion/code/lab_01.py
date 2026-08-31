import math
import matplotlib.pyplot as plt


def motor_rpm(load_torque, no_load_rpm, stall_torque):
    """Return a simple linear torque-speed prediction."""
    if load_torque < 0:
        raise ValueError("Load torque cannot be negative.")
    if no_load_rpm < 0 or stall_torque <= 0:
        raise ValueError("Motor parameters are invalid.")

    speed = no_load_rpm * (1.0 - load_torque / stall_torque)

    # A stalled motor cannot have negative rotational speed in this model.
    return max(0.0, speed)


no_load_rpm = 150.0
stall_torque = 0.20
load_torques = [0.00, 0.05, 0.10, 0.15, 0.20]

predicted_rpm = []
for load in load_torques:
    speed = motor_rpm(load, no_load_rpm, stall_torque)
    predicted_rpm.append(speed)
    print("Load: {:.2f} N*m -> Speed: {:.1f} RPM".format(load, speed))

# Verify the hand calculation and another endpoint before displaying the graph.
assert math.isclose(predicted_rpm[2], 75.0, rel_tol=1e-9)
assert math.isclose(predicted_rpm[1], 112.5, rel_tol=1e-9)
assert math.isclose(predicted_rpm[-1], 0.0, rel_tol=1e-9)
print("Verified: 0.10 N*m gives 75.0 RPM.")
print("Verified: 0.05 N*m gives 112.5 RPM.")
print("Verified: 0.20 N*m gives 0.0 RPM.")

plt.plot(load_torques, predicted_rpm, "o-", color="darkblue")
plt.xlabel("Load torque (N*m)")
plt.ylabel("Predicted motor speed (RPM)")
plt.title("RoboRover motor: simplified torque-speed model")
plt.grid(True)
plt.tight_layout()
plt.show()
