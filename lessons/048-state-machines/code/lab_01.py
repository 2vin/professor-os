def dock_reached(distance):
    return distance <= 0.30


assert dock_reached(0.25)
assert not dock_reached(0.45)
