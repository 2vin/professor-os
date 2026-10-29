# Python 3.7
# RoboRover stationary stochastic two-armed bandit demonstration

import random

random.seed(54)

routes = {
    "wide_route": {
        "success_probability": 0.95,
        "success_reward": 4,
        "failure_reward": -1
    },
    "shortcut": {
        "success_probability": 0.70,
        "success_reward": 8,
        "failure_reward": -10
    }
}

totals = {
    "wide_route": 0,
    "shortcut": 0
}

counts = {
    "wide_route": 0,
    "shortcut": 0
}

choices = []
rewards = []


def average_reward(route_name):
    if counts[route_name] == 0:
        return 0.0
    return float(totals[route_name]) / counts[route_name]


def sample_reward(route_name):
    route = routes[route_name]
    if random.random() < route["success_probability"]:
        return route["success_reward"]
    return route["failure_reward"]


for episode in range(8):
    # Force one early test of each action.
    if episode == 0:
        chosen_route = "wide_route"
    elif episode == 1:
        chosen_route = "shortcut"
    else:
        wide_average = average_reward("wide_route")
        shortcut_average = average_reward("shortcut")

        if wide_average >= shortcut_average:
            chosen_route = "wide_route"
        else:
            chosen_route = "shortcut"

    # Each selection is an independent draw from the route's
    # stationary reward distribution.
    reward = sample_reward(chosen_route)

    counts[chosen_route] += 1
    totals[chosen_route] += reward

    choices.append(chosen_route)
    rewards.append(reward)

    print(
        "Episode {0}: action={1}, reward={2}, average={3:.2f}".format(
            episode + 1,
            chosen_route,
            reward,
            average_reward(chosen_route)
        )
    )

print("Choices:", choices)
print("Rewards:", rewards)
print(
    "Final averages:",
    round(average_reward("wide_route"), 2),
    round(average_reward("shortcut"), 2)
)

# Verify the stationary model's theoretical expected rewards.
wide_expected = (
    0.95 * 4.0 +
    0.05 * (-1.0)
)
shortcut_expected = (
    0.70 * 8.0 +
    0.30 * (-10.0)
)

assert round(wide_expected, 2) == 3.75
assert round(shortcut_expected, 2) == 2.60

# Verify bookkeeping and the reward support of each route.
assert len(choices) == 8
assert len(rewards) == 8
assert counts["wide_route"] + counts["shortcut"] == 8
assert totals["wide_route"] + totals["shortcut"] == sum(rewards)

assert all(
    reward in (4, -1)
    for route, reward in zip(choices, rewards)
    if route == "wide_route"
)
assert all(
    reward in (8, -10)
    for route, reward in zip(choices, rewards)
    if route == "shortcut"
)

# The first two episodes deliberately test both available actions.
assert choices[0] == "wide_route"
assert choices[1] == "shortcut"

print("Verification passed.")
