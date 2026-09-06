robot_x = 0.040
SENSOR_OFFSET = 0.045

left_sensor_x = robot_x - SENSOR_OFFSET
center_sensor_x = robot_x
right_sensor_x = robot_x + SENSOR_OFFSET

assert left_sensor_x < center_sensor_x < right_sensor_x
