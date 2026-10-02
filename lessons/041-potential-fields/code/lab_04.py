import numpy as np


def point_to_segment_distance(point, segment_start, segment_end):
    segment = segment_end - segment_start
    segment_length_squared = np.dot(segment, segment)

    if segment_length_squared == 0.0:
        return np.linalg.norm(point - segment_start)

    projection = np.dot(point - segment_start, segment)
    parameter = projection / segment_length_squared
    parameter = min(1.0, max(0.0, parameter))

    closest_point = segment_start + parameter * segment
    return np.linalg.norm(point - closest_point)
