import math

experiment_rover = (1, -3)
experiment_target = (5, 0)

horizontal_difference = (
    experiment_target[0] - experiment_rover[0]
)
vertical_difference = (
    experiment_target[1] - experiment_rover[1]
)

experiment_distance = math.sqrt(
    horizontal_difference ** 2 + vertical_difference ** 2
)

print("Experiment distance: {:.3f} units".format(
    experiment_distance
))

assert math.isclose(experiment_distance, 5.0)
