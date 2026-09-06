THRESHOLD = 100
dark_reading = 200


def detects_line(reading):
    return reading < THRESHOLD


assert detects_line(dark_reading) is False
print("The dark reading was not detected because the threshold is too low.")
