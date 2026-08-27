# Python 3.7-compatible example
# Class 1: Same hardware, different decision authority

import math


def run_rover(commands, speed_m_per_s, command_time_s):
    """Return the rover's final position after a list of commands."""
    position_m = 0.0

    for command in commands:
        # Keep the command within the actuator's allowed range.
        if command > 1:
            command = 1
        elif command < -1:
            command = -1

        position_m += command * speed_m_per_s * command_time_s

    return position_m


def choose_autonomous_commands(marker_distance_m):
    """Choose task-level commands from a simulated marker measurement."""
    if marker_distance_m > 1.5:
        # The marker is far ahead: approach it for three command intervals.
        return [1, 1, 1, 0]
    elif marker_distance_m > 0.5:
        # The marker is nearer: approach it for two command intervals.
        return [1, 1, 0, 0]
    else:
        # The marker is already near: remain stopped.
        return [0, 0, 0, 0]


speed_m_per_s = 0.60
command_time_s = 2.0

# A human operator chooses these immediate commands.
teleoperated_commands = [1, 1, 0, -1]

# A stored program contains the same commands.
preprogrammed_commands = [1, 1, 0, -1]

# A simulated sensor reports that the visible marker is 2.0 m away.
# Task-level software uses that measurement to choose the commands.
marker_distance_m = 2.0
autonomous_commands = choose_autonomous_commands(marker_distance_m)

teleoperated_position = run_rover(
    teleoperated_commands, speed_m_per_s, command_time_s
)
preprogrammed_position = run_rover(
    preprogrammed_commands, speed_m_per_s, command_time_s
)
autonomous_position = run_rover(
    autonomous_commands, speed_m_per_s, command_time_s
)

print("Teleoperated final position: {:.1f} m".format(teleoperated_position))
print("Preprogrammed final position: {:.1f} m".format(preprogrammed_position))
print("Autonomous commands: {}".format(autonomous_commands))
print("Autonomous final position: {:.1f} m".format(autonomous_position))

# Floating-point arithmetic can represent 3.6 approximately, so compare
# with a small tolerance rather than requiring exact binary equality.
assert math.isclose(teleoperated_position, 1.2, rel_tol=0.0, abs_tol=1e-9)
assert math.isclose(preprogrammed_position, 1.2, rel_tol=0.0, abs_tol=1e-9)
assert autonomous_commands == [1, 1, 1, 0]
assert math.isclose(autonomous_position, 3.6, rel_tol=0.0, abs_tol=1e-9)
assert math.isclose(
    teleoperated_position,
    preprogrammed_position,
    rel_tol=0.0,
    abs_tol=1e-9,
)
