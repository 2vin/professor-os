import math


def line_position(forward_distance):
    if forward_distance < 2.0:
        return 0.0
    return 0.08 * math.sin(0.8 * forward_distance)


assert line_position(1.0) == 0.0
