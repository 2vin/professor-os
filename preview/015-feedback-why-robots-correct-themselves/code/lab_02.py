# Python 3.7
def run_experiment(threshold, noise_values, correct=True):
    actual = 6.0
    actions = []

    for noise in noise_values:
        measured = actual + noise

        if not correct:
            command, action = 0, "straight"
        elif measured > threshold:
            command, action = -1, "left"
        elif measured < -threshold:
            command, action = 1, "right"
        else:
            command, action = 0, "straight"

        actions.append(action)
        actual += 0.8 * command

    return actual, actions


original_noise = [0.4, -0.4, -0.4, -0.4, -0.4,
                  -0.4, -0.4, -0.4, -0.4, -0.4]

position_a, actions_a = run_experiment(2.0, original_noise, False)
position_b, actions_b = run_experiment(5.0, original_noise)

disturbed_noise = original_noise[:]
disturbed_noise[7] = 5.0
position_c, actions_c = run_experiment(2.0, disturbed_noise)

assert abs(position_a - 6.0) < 1e-9
assert abs(position_b - 5.2) < 1e-9
assert abs(position_c - 1.2) < 1e-9
assert actions_c.count("left") == 6

print("A final: {:.2f} cm".format(position_a))
print("B final: {:.2f} cm".format(position_b))
print("C final: {:.2f} cm; left commands: {}".format(
    position_c, actions_c.count("left")
))
