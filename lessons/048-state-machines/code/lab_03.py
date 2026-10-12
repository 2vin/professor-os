# Python 3.7-compatible finite-state machine for RoboRover

def step(state, event):
    transitions = {
        ("IDLE", "start"): "SEARCH",
        ("SEARCH", "marker_seen"): "ALIGN",
        ("ALIGN", "marker_centered"): "DRIVE",
        ("DRIVE", "obstacle_detected"): "STOP",
        ("STOP", "path_clear"): "DRIVE",
        ("DRIVE", "dock_reached"): "DOCKED",
        ("DOCKED", "charger_connected"): "CHARGING",
        ("CHARGING", "battery_full"): "IDLE",
    }

    key = (state, event)

    if key in transitions:
        return transitions[key]

    # In this teaching example, unexpected events in motion- or
    # charging-related states cause an explicit safe hold.
    if state in ("DRIVE", "DOCKED", "CHARGING"):
        return "SAFE_HOLD"

    # For less critical states, an unrecognized event leaves the
    # current state unchanged.
    return state


def describe_action(state):
    actions = {
        "IDLE": "wait for a mission",
        "SEARCH": "rotate and look for the blue marker",
        "ALIGN": "turn until the marker is centered",
        "DRIVE": "follow the approach trajectory",
        "STOP": "hold position and wait safely",
        "DOCKED": "stop approach and perform or monitor the docking connection",
        "CHARGING": "keep drive motors disabled while charging is confirmed",
        "SAFE_HOLD": (
            "stop drive motion, request safe inhibition of docking or charging, "
            "and report an unexpected event"
        ),
    }
    return actions[state]


def main():
    events = [
        "start",
        "marker_seen",
        "marker_centered",
        "obstacle_detected",
        "path_clear",
        "dock_reached",
        "charger_connected",
        "battery_full",
    ]

    state = "IDLE"
    trace = [state]

    print("Initial state:", state)
    print("Action:", describe_action(state))

    for event in events:
        old_state = state
        state = step(state, event)
        trace.append(state)

        print("Event: {0} | {1} -> {2}".format(
            event, old_state, state
        ))
        print("Action:", describe_action(state))

    expected_trace = [
        "IDLE",
        "SEARCH",
        "ALIGN",
        "DRIVE",
        "STOP",
        "DRIVE",
        "DOCKED",
        "CHARGING",
        "IDLE",
    ]

    assert state == "IDLE"
    assert len(events) == 8
    assert trace == expected_trace
    assert trace[3] == "DRIVE"
    assert trace[4] == "STOP"
    assert trace[5] == "DRIVE"

    # Unexpected events in motion- or charging-related states
    # enter an explicit safe hold.
    assert step("DRIVE", "unexpected_event") == "SAFE_HOLD"
    assert step("DOCKED", "unexpected_event") == "SAFE_HOLD"
    assert step("CHARGING", "unexpected_event") == "SAFE_HOLD"

    # SAFE_HOLD persists for an unrecognized event in this model.
    assert step("SAFE_HOLD", "unexpected_event") == "SAFE_HOLD"

    # Unexpected events in less critical states are ignored by
    # remaining in the current state.
    ignored_event_cases = [
        ("IDLE", "unexpected_event"),
        ("SEARCH", "unexpected_event"),
        ("ALIGN", "unexpected_event"),
        ("STOP", "unexpected_event"),
    ]

    for source_state, event in ignored_event_cases:
        assert step(source_state, event) == source_state

    # Invalid transitions from every major mission state do not
    # bypass the state-machine policy.
    invalid_transition_cases = [
        ("IDLE", "battery_full", "IDLE"),
        ("SEARCH", "charger_connected", "SEARCH"),
        ("ALIGN", "battery_full", "ALIGN"),
        ("DRIVE", "battery_full", "SAFE_HOLD"),
        ("STOP", "battery_full", "STOP"),
        ("DOCKED", "battery_full", "SAFE_HOLD"),
        ("CHARGING", "dock_reached", "SAFE_HOLD"),
    ]

    for source_state, event, expected_state in invalid_transition_cases:
        assert step(source_state, event) == expected_state

    print("Verified final state: IDLE")
    print("Verified normal trace:", trace)
    print("Verified transition count:", len(events))
    print("Verified unexpected-event safety responses: SAFE_HOLD")
    print("Verified ignored-event and invalid-transition cases")


if __name__ == "__main__":
    main()
