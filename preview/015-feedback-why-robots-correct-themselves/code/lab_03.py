# Python 3.7
measurement_a = 5.8
measurement_b = 6.2
average_measurement = (measurement_a + measurement_b) / 2.0

assert abs(average_measurement - 6.0) < 1e-9
print("Average measurement: {:.1f} cm".format(average_measurement))
