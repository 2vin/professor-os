class SensorErrorExample:
    def __init__(self, actual_position_m=0.0, error_m=0.1):
        self.actual_position_m = actual_position_m
        self.error_m = error_m

    def read_position_sensor(self):
        return self.actual_position_m + self.error_m


example = SensorErrorExample(actual_position_m=1.5, error_m=0.1)

print("Actual position:", example.actual_position_m)
print("Measured position:", example.read_position_sensor())

assert example.read_position_sensor() == 1.6
