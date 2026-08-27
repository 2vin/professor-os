# Python 3.7 compatible
# Class 1: same RoboRover hardware, different decision authority

TRACK_LENGTH_M = 5.0
STEP_DISTANCE_M = 1.0
NUMBER_OF_STEPS = 5


def move_rover(commands):
    """Apply forward (+1) or stop (0) commands and return the final position."""
    position_m = 0.0

    for command in commands:
        if command == 1:
            position_m += STEP_DISTANCE_M
        elif command == 0:
            pass
        else:
            raise ValueError("Commands must be 1 for forward or 0 for stop.")

        # The rover cannot move beyond the end of the track.
        if position_m > TRACK_LENGTH_M:
            position_m = TRACK_LENGTH_M

    return position_m


def get_commands(mode):
    """Return commands selected by a human, a program, or autonomous software."""
    if mode == "human":
        commands = []
        print("Enter one command when each prompt appears: 1 for forward, 0 for stop.")
        for step in range(NUMBER_OF_STEPS):
            try:
                value = int(input("Command {}: ".format(step + 1)))
            except EOFError:
                raise ValueError(
                    "Human mode requires five commands; input ended unexpectedly."
                )
            if value not in (0, 1):
                raise ValueError("Please enter only 0 or 1.")
            commands.append(value)
        return commands

    if mode == "programmed":
        # These commands were written before the run begins.
        return [1, 1, 1, 1, 1]

    if mode == "autonomous":
        # The software uses an idealized internal simulated state.
        # This is not a simulated sensor measurement.
        commands = []
        position_m = 0.0

        for step in range(NUMBER_OF_STEPS):
            if position_m < TRACK_LENGTH_M:
                command = 1
            else:
                command = 0

            commands.append(command)

            if command == 1:
                position_m += STEP_DISTANCE_M

        return commands

    raise ValueError("Mode must be human, programmed, or autonomous.")


def main():
    print("RoboRover same-hardware activity")
    print("Choose: human, programmed, or autonomous")
    try:
        mode = input("Mode: ").strip().lower()
    except EOFError:
        # Noninteractive execution uses a deterministic automatic demonstration.
        mode = "programmed"
        print("No input received; running programmed mode.")

    commands = get_commands(mode)
    final_position_m = move_rover(commands)

    print("Commands:", commands)
    print("Final position: {:.1f} m".format(final_position_m))

    # These assertions verify the exact result for the two automatic modes.
    if mode in ("programmed", "autonomous"):
        assert commands == [1, 1, 1, 1, 1]
        assert final_position_m == 5.0

    # This verifies the physical model for any valid command list.
    assert 0.0 <= final_position_m <= TRACK_LENGTH_M


if __name__ == "__main__":
    main()
