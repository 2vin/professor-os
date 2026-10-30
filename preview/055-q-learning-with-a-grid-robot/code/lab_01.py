import random

ROWS = 4
COLS = 4
START = (3, 0)
GOAL = (0, 3)
OBSTACLE = (1, 1)

ACTIONS = ["U", "R", "D", "L"]
MOVES = {
    "U": (-1, 0),
    "R": (0, 1),
    "D": (1, 0),
    "L": (0, -1),
}

ALPHA = 0.5
GAMMA = 0.9
EPISODES = 2000
MAX_STEPS = 100

rng = random.Random(7)

q_table = {}
for row in range(ROWS):
    for col in range(COLS):
        if (row, col) != OBSTACLE:
            q_table[(row, col)] = {}
            for action in ACTIONS:
                q_table[(row, col)][action] = 0.0


def step(state, action):
    """Return next_state, reward, and whether the episode is finished."""
    row, col = state
    d_row, d_col = MOVES[action]
    next_state = (row + d_row, col + d_col)

    outside = (
        next_state[0] < 0 or next_state[0] >= ROWS or
        next_state[1] < 0 or next_state[1] >= COLS
    )

    if outside or next_state == OBSTACLE:
        return state, -3.0, False

    if next_state == GOAL:
        return next_state, 10.0, True

    return next_state, -1.0, False


def choose_action(state, epsilon):
    """Choose randomly with probability epsilon; otherwise choose greedily."""
    if rng.random() < epsilon:
        return rng.choice(ACTIONS)

    best_value = max(q_table[state].values())
    best_actions = [
        action for action in ACTIONS
        if q_table[state][action] == best_value
    ]
    return rng.choice(best_actions)


for episode in range(EPISODES):
    state = START
    epsilon = max(0.05, 1.0 - episode / 1500.0)

    for step_number in range(MAX_STEPS):
        action = choose_action(state, epsilon)
        next_state, reward, finished = step(state, action)

        if finished:
            future_value = 0.0
        else:
            future_value = max(q_table[next_state].values())

        old_value = q_table[state][action]
        target = reward + GAMMA * future_value
        q_table[state][action] = old_value + ALPHA * (target - old_value)

        state = next_state

        if finished:
            break


def greedy_path():
    """Follow learned greedy actions from START."""
    state = START
    path = [state]

    for unused in range(MAX_STEPS):
        if state == GOAL:
            return path

        best_value = max(q_table[state].values())
        best_actions = [
            action for action in ACTIONS
            if q_table[state][action] == best_value
        ]
        action = best_actions[0]
        state, reward, finished = step(state, action)
        path.append(state)

        if finished:
            return path

    return path


path = greedy_path()

print("Greedy path:", path)
print("Number of moves:", len(path) - 1)
print("Start Q values:", q_table[START])

assert path[0] == START
assert path[-1] == GOAL
assert len(path) - 1 <= 8
print("Verification passed: the learned greedy policy reaches the goal.")
