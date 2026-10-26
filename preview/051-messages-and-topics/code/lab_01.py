class MessageBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, topic_name, callback):
        if topic_name not in self.subscribers:
            self.subscribers[topic_name] = []
        self.subscribers[topic_name].append(callback)

    def publish(self, topic_name, message):
        callbacks = self.subscribers.get(topic_name, [])
        for callback in callbacks:
            callback(message)


class SafetyNode:
    def __init__(self, bus, stop_distance_m):
        self.bus = bus
        self.stop_distance_m = stop_distance_m
        self.decisions = []

        self.bus.subscribe("/roborover/front_distance",
                           self.distance_callback)

    def distance_callback(self, message):
        if not message["valid"]:
            command = "STOP"
            distance_m = message["distance_m"]
        else:
            distance_m = message["distance_m"]

            if distance_m <= self.stop_distance_m:
                command = "STOP"
            else:
                command = "FORWARD"

        self.decisions.append((distance_m, command))
        self.bus.publish("/roborover/motor_command", command)


class MotorNode:
    def __init__(self, bus):
        self.commands_received = []
        bus.subscribe("/roborover/motor_command",
                      self.command_callback)

    def command_callback(self, command):
        self.commands_received.append(command)


def main():
    bus = MessageBus()
    safety = SafetyNode(bus, stop_distance_m=0.50)
    motors = MotorNode(bus)

    distance_messages = [
        {"distance_m": 0.80, "valid": True},
        {"distance_m": 0.65, "valid": True},
        {"distance_m": 0.48, "valid": True},
        {"distance_m": 0.44, "valid": True},
    ]

    for message in distance_messages:
        bus.publish("/roborover/front_distance", message)

    expected_decisions = [
        (0.80, "FORWARD"),
        (0.65, "FORWARD"),
        (0.48, "STOP"),
        (0.44, "STOP"),
    ]

    assert safety.decisions == expected_decisions
    assert motors.commands_received == [
        "FORWARD",
        "FORWARD",
        "STOP",
        "STOP",
    ]

    # Invalid sensor data is not treated as safe.
    bus.publish(
        "/roborover/front_distance",
        {"distance_m": 0.10, "valid": False},
    )

    assert safety.decisions[-1] == (0.10, "STOP")
    assert motors.commands_received[-1] == "STOP"

    print("Safety decisions:", safety.decisions)
    print("Motor commands:", motors.commands_received)
    print("Verified: valid readings followed the distance rule.")
    print("Verified: an invalid reading produced STOP.")


if __name__ == "__main__":
    main()
