# Python 3.7
# Self-contained modified stationary bandit:
# shortcut failures are -20.

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
        "failure_reward": -20
    }
}

totals = {"wide_route": 0, "shortcut": 0}
counts = {"wide_route": 0, "shortcut": 0}
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
    if episode == 0:
        chosen_route = "wide_route"
    elif episode == 1:
        chosen_route = "shortcut"
    elif average_reward("wide_route") >= average_reward("shortcut"):
        chosen_route = "wide_route"
    else:
        chosen_route = "shortcut"

    reward = sample_reward(chosen_route)

    counts[chosen_route] += 1
    totals[chosen_route] += reward
    choices.append(chosen_route)
    rewards.append(reward)

wide_expected = 0.95 * 4.0 + 0.05 * (-1.0)
shortcut_expected = 0.70 * 8.0 + 0.30 * (-20.0)

assert round(wide_expected, 2) == 3.75
assert round(shortcut_expected, 2) == -0.40

assert len(choices) == 8
assert len(rewards) == 8
assert counts["wide_route"] + counts["shortcut"] == 8
assert totals["wide_route"] + totals["shortcut"] == sum(rewards)
assert counts["shortcut"] >= 1

assert all(
    reward in (4, -1)
    for route, reward in zip(choices, rewards)
    if route == "wide_route"
)
assert all(
    reward in (8, -20)
    for route, reward in zip(choices, rewards)
    if route == "shortcut"
)

print("Modified experiment verification passed.")
