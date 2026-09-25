import math


def bayes_update(prior, likelihood):
    if len(prior) != len(likelihood) or not prior:
        raise ValueError("Inputs must have the same nonzero length.")

    tolerance = 1e-12
    for value in prior + likelihood:
        if not math.isfinite(value) or value < 0.0 or value > 1.0:
            raise ValueError("Values must be finite and between 0 and 1.")

    if abs(sum(prior) - 1.0) > tolerance:
        raise ValueError("Prior must sum to 1.")

    scores = [p * l for p, l in zip(prior, likelihood)]
    total = sum(scores)
    if total <= 0.0:
        raise ValueError("Observation is impossible under this model.")

    posterior = [score / total for score in scores]
    assert abs(sum(posterior) - 1.0) < tolerance
    return posterior


def print_belief(label, belief):
    print(label)
    print(["{:.6f}".format(value) for value in belief])
    print("total: {:.6f}".format(sum(belief)))


prior = [0.25, 0.25, 0.25, 0.25]
blue = [0.10, 0.80, 0.20, 0.10]
no_blue = [0.90, 0.20, 0.80, 0.90]

after_blue = bayes_update(prior, blue)
after_no_blue = bayes_update(after_blue, no_blue)

assert all(
    abs(actual - expected) < 1e-12
    for actual, expected in zip(
        after_blue, [1.0 / 12.0, 2.0 / 3.0, 1.0 / 6.0, 1.0 / 12.0]
    )
)
assert all(
    abs(actual - expected) < 1e-12
    for actual, expected in zip(
        after_no_blue, [9.0 / 50.0, 8.0 / 25.0,
                        8.0 / 25.0, 9.0 / 50.0]
    )
)

equal_evidence = bayes_update(after_blue, [0.5, 0.5, 0.5, 0.5])
assert all(
    abs(actual - expected) < 1e-12
    for actual, expected in zip(equal_evidence, after_blue)
)

print_belief("After blue:", after_blue)
print_belief("After blue, then no blue:", after_no_blue)
print("All checks passed.")
