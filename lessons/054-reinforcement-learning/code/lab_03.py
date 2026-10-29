# Python 3.7
# Standalone demonstration of the exploration-selection block.

import random

random.seed(54)

totals = {
    "wide_route": 4,
    "shortcut": 8
}

counts = {
    "wide_route": 1,
    "shortcut": 1
}


def average_reward(route_name):
    return float(totals[route_name]) / counts[route_name]


if random.random() < 0.25:
    chosen_route = random.choice(["wide_route", "shortcut"])
else:
    wide_average = average_reward("wide_route")
    shortcut_average = average_reward("shortcut")

    if wide_average >= shortcut_average:
        chosen_route = "wide_route"
    else:
        chosen_route = "shortcut"

print("Selected route:", chosen_route)
