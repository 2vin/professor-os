# Python 3.7-compatible RoboRover Class 1 experiment

class RoboRover:
    def __init__(self, speed_m_per_s=0.5):
        self.position_m = 0.0
        self.speed_m_per_s = speed_m_per_s

    def step(self, command, duration_s):
        """Move according to a command for a specified time."""
        if command not in (-1, 0, 1):
            raise ValueError("command must be -1, 0, or 1")

        self.position_m += command * self.speed_m_per_s * duration_s
        return self.position_m

    def read_position_sensor(self):
        """Return an idealized position measurement."""
        return self.position_m


def run_rover(mode, target_m=2.0):
    rover = RoboRover(speed_m_per_s=0.5)
    positions_m = []

    if mode == "teleoperated":
        # Imagine a human pressing buttons during four one-second intervals.
        commands = [1, 0, -1, 0]
        for command in commands:
            positions_m.append(rover.step(command, 1.0))

    elif mode == "preprogrammed":
        # A stored sequence runs without a human choosing each step.
        commands = [1, 1, 1, 0]
        for command in commands:
            positions_m.append(rover.step(command, 1.0))

    elif mode == "autonomous":
        # Software uses the idealized measured position to choose each command.
        for unused_step in range(4):
            measured_position_m = rover.read_position_sensor()
            if measured_position_m < target_m:
                command = 1
            else:
                command = 0
            positions_m.append(rover.step(command, 1.0))

    else:
        raise ValueError("unknown mode")

    return positions_m


def main():
    print("RoboRover Class 1 experiment")
    print("Choose: teleoperated, preprogrammed, or autonomous")

    try:
        selected_mode = input("Mode: ").strip().lower()
    except EOFError:
        selected_mode = "autonomous"

    if selected_mode not in ("teleoperated", "preprogrammed", "autonomous"):
        print("Unknown choice; running autonomous mode.")
        selected_mode = "autonomous"

    selected_positions = run_rover(selected_mode)
    print("Selected mode:", selected_mode)
    print("Positions after each 1-second step:", selected_positions)
    print("Final position: {:.1f} m".format(selected_positions[-1]))

    # Verification checks for the experiment's exact claims.
    teleoperated_positions = run_rover("teleoperated")
    preprogrammed_positions = run_rover("preprogrammed")
    autonomous_positions = run_rover("autonomous")

    assert teleoperated_positions == [0.5, 0.5, 0.0, 0.0]
    assert preprogrammed_positions == [0.5, 1.0, 1.5, 1.5]
    assert autonomous_positions == [0.5, 1.0, 1.5, 2.0]

    assert teleoperated_positions[-1] == 0.0
    assert preprogrammed_positions[-1] == 1.5
    assert autonomous_positions[-1] == 2.0

    print("All verification checks passed.")


if __name__ == "__main__":
    main()
