import matplotlib.pyplot as plt

mass_kg = 0.35
gravity_m_s2 = 9.81
friction_coefficient = 0.60
safety_factor = 2.0

weight_n = mass_kg * gravity_m_s2
required_force_per_finger_n = (
    safety_factor * weight_n
    / (2.0 * friction_coefficient)
)

def predicted_safe(force_per_finger_n):
    total_friction_n = (
        2.0 * friction_coefficient * force_per_finger_n
    )
    required_load_n = safety_factor * weight_n
    return total_friction_n >= required_load_n

test_forces_n = [5.0, 6.0]
test_results = [predicted_safe(force) for force in test_forces_n]

print("Object weight: {:.4f} N".format(weight_n))
print(
    "Required force per finger: {:.4f} N".format(
        required_force_per_finger_n
    )
)

for force, safe in zip(test_forces_n, test_results):
    print(
        "{:.1f} N per finger -> {}".format(
            force,
            "predicted safe" if safe else "predicted slip"
        )
    )

assert abs(weight_n - 3.4335) < 1e-9
assert abs(required_force_per_finger_n - 5.7225) < 1e-9
assert test_results == [False, True]

forces_n = [force / 10.0 for force in range(0, 101)]
safe_values = [predicted_safe(force) for force in forces_n]

colors = ["tab:green" if safe else "tab:red" for safe in safe_values]

plt.figure(figsize=(8, 4))
plt.scatter(forces_n, safe_values, c=colors, s=18)
plt.axvline(
    required_force_per_finger_n,
    color="black",
    linestyle="--",
    label="calculated threshold"
)
plt.yticks([0, 1], ["predicted slip", "predicted safe"])
plt.xlabel("Normal force per finger (N)")
plt.ylabel("Simplified prediction")
plt.title("RoboRover's two-finger grasp estimate")
plt.grid(True, axis="x", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
