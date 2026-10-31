WIDTH = 7
HEIGHT = 5
START_TOP = (0, 2)
START_BOTTOM = (0, 4)
GOAL = (6, 2)

OBSTACLES = {
    (3, 1),
    (3, 2),
    (3, 3),
}

TOP_DEMO = [
    (0, 2), (0, 1), (0, 0),
    (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0),
    (6, 1), (6, 2)
]

BOTTOM_DEMO = [
    (0, 4),
    (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4),
    (6, 3), (6, 2)
]

DIRECTION_NAMES = {
    (0, -1): "UP",
    (0, 1): "DOWN",
    (1, 0): "RIGHT",
    (-1, 0): "LEFT",
}


def actions_between(path):
    """Convert a sequence of positions into action labels."""
    actions = []

    for index in range(len(path) - 1):
        x1, y1 = path[index]
        x2, y2 = path[index + 1]
        delta = (x2 - x1, y2 - y1)

        if delta not in DIRECTION_NAMES:
            raise ValueError("Demonstration contains a non-adjacent move.")

        actions.append(DIRECTION_NAMES[delta])

    return actions


def learn_policy(demonstrations):
    """Count demonstrated actions and choose the most common one."""
    counts = {}

    for path in demonstrations:
        actions = actions_between(path)

        for index in range(len(actions)):
            observation = path[index]
            action = actions[index]

            if observation not in counts:
                counts[observation] = {}

            if action not in counts[observation]:
                counts[observation][action] = 0

            counts[observation][action] += 1

    policy = {}

    for observation in counts:
        action_counts = counts[observation]
        best_action = None
        best_count = -1

        for action in action_counts:
            if action_counts[action] > best_count:
                best_action = action
                best_count = action_counts[action]

        policy[observation] = best_action

    return policy, counts


def next_position(position, action):
    x, y = position

    if action == "UP":
        return (x, y - 1)
    if action == "DOWN":
        return (x, y + 1)
    if action == "RIGHT":
        return (x + 1, y)
    if action == "LEFT":
        return (x - 1, y)

    raise ValueError("Unknown action.")


def legal(position):
    x, y = position
    inside = 0 <= x < WIDTH and 0 <= y < HEIGHT
    return inside and position not in OBSTACLES


def run_episode(policy, start, goal, maximum_steps=30):
    position = start
    trace = [position]

    for step in range(maximum_steps):
        if position == goal:
            return trace

        if position not in policy:
            raise RuntimeError("The learned policy has no action for this observation.")

        action = policy[position]
        candidate = next_position(position, action)

        if not legal(candidate):
            raise RuntimeError("The learned action drives into a wall or outside the floor.")

        position = candidate
        trace.append(position)

    raise RuntimeError("The robot did not reach the goal in time.")


def print_floor(trace):
    trace_set = set(trace)

    for y in range(HEIGHT):
        row = []

        for x in range(WIDTH):
            position = (x, y)

            if position in OBSTACLES:
                symbol = "#"
            elif position == GOAL:
                symbol = "G"
            elif position == trace[0]:
                symbol = "S"
            elif position in trace_set:
                symbol = "*"
            else:
                symbol = "."

            row.append(symbol)

        print(" ".join(row))


def main():
    demonstrations = [TOP_DEMO, BOTTOM_DEMO]
    policy, counts = learn_policy(demonstrations)

    top_trace = run_episode(policy, START_TOP, GOAL)
    bottom_trace = run_episode(policy, START_BOTTOM, GOAL)

    # These checks verify the exact route lengths used by this lesson.
    assert len(actions_between(TOP_DEMO)) == 10
    assert len(actions_between(BOTTOM_DEMO)) == 8
    assert len(top_trace) - 1 == 10
    assert len(bottom_trace) - 1 == 8
    assert top_trace[-1] == GOAL
    assert bottom_trace[-1] == GOAL
    assert policy[START_TOP] == "UP"
    assert policy[START_BOTTOM] == "RIGHT"

    # This position was not included in either demonstration.
    assert (1, 3) not in policy

    print("Learned action at top start:", policy[START_TOP])
    print("Top route moves:", len(top_trace) - 1)
    print("Bottom route moves:", len(bottom_trace) - 1)
    print("An unseen observation has a learned action:",
          (1, 3) in policy)

    print("\nTop demonstration replay:")
    print_floor(top_trace)

    print("\nBottom demonstration replay:")
    print_floor(bottom_trace)


if __name__ == "__main__":
    main()
