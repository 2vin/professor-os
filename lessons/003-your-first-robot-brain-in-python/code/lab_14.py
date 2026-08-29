battery_points = 30.0
battery_points = battery_points - 4.0

assert round(battery_points, 1) == 26.0
print("Battery update passed:", battery_points)
