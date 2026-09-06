THRESHOLD = 500


def detects_line(reading):
    return reading < THRESHOLD


assert detects_line(310) is True
assert detects_line(720) is False
