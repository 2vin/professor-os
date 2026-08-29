distance_cm = 18.0

if distance_cm >= 50.0:
    action = "drive"
elif distance_cm >= 20.0:
    action = "slow"
else:
    action = "clean"

print(action)
