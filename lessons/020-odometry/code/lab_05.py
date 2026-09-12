import math


def command_to_wheel_travel(forward_distance, turn_degrees, track_width):
    turn_radians = math.radians(turn_degrees)
    left_distance = forward_distance - (
        track_width * turn_radians / 2.0
    )
    right_distance = forward_distance + (
        track_width * turn_radians / 2.0
    )
    return left_distance, right_distance
