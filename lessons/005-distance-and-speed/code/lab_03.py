starting_position_m = 0.0
target_position_m = 5.0
speed_m_per_s = 1.25
time_step_s = 0.25

assert speed_m_per_s > 0
assert time_step_s > 0
assert target_position_m >= starting_position_m

predicted_time_s = (
    target_position_m - starting_position_m
) / speed_m_per_s
number_of_steps = int(round(predicted_time_s / time_step_s))

assert abs(
    predicted_time_s / time_step_s - number_of_steps
) < 1e-9

times_s = []
positions_m = []

for step in range(number_of_steps + 1):
    time_s = step * time_step_s
    position_m = starting_position_m + speed_m_per_s * time_s
    times_s.append(time_s)
    positions_m.append(position_m)

assert round(predicted_time_s, 10) == 4.0
assert round(positions_m[-1], 10) == round(target_position_m, 10)
