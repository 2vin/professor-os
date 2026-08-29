battery_points = 8.0
distance_cm = 72.0

if battery_points < 10.0:
    action = "stop and recharge"
elif distance_cm >= 50.0:
    action = "drive"
elif distance_cm >= 20.0:
    action = "slow"
else:
    action = "clean"

print(action)
