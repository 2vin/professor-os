class Topic:
    def __init__(self, name):
        self.name = name
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish(self, message):
        # Simplification: callbacks run synchronously and immediately.
        for callback in self.subscribers:
            callback(message)


class ServiceServer:
    def __init__(self, name, handler):
        self.name = name
        self.handler = handler

    def call(self, request):
        return self.handler(request)


class Node:
    def __init__(self, name):
        self.name = name
        self.services = {}

    def create_service(self, name, handler):
        self.services[name] = ServiceServer(name, handler)

    def call_service(self, server_node, name, request):
        if name not in server_node.services:
            raise KeyError("Service is not available: {}".format(name))
        return server_node.services[name].call(request)


class SafetyNode(Node):
    def __init__(self, name, distance_topic, desired_topic, safe_topic,
                 threshold_m):
        super().__init__(name)
        self.distance_m = None
        self.desired_speed_mps = 0.0
        self.threshold_m = threshold_m
        self.safe_topic = safe_topic

        distance_topic.subscribe(self.receive_distance)
        desired_topic.subscribe(self.receive_desired_speed)

    def receive_distance(self, distance_m):
        self.distance_m = distance_m
        self.publish_safe_command()

    def receive_desired_speed(self, speed_mps):
        self.desired_speed_mps = speed_mps
        self.publish_safe_command()

    def publish_safe_command(self):
        if self.distance_m is None:
            safe_speed = 0.0
        elif self.distance_m < self.threshold_m:
            safe_speed = 0.0
        else:
            safe_speed = self.desired_speed_mps

        self.safe_topic.publish(safe_speed)


def reset_odometry(request):
    if request == "reset":
        return "odometry reset"
    return "unknown request"


front_distance = Topic("/front_distance")
desired_speed = Topic("/desired_speed")
safe_speed = Topic("/safe_speed")

behavior_node = Node("behavior_tree")
drive_node = Node("drive_controller")
odometry_node = Node("odometry_service")

safety_node = SafetyNode(
    "safety_controller",
    front_distance,
    desired_speed,
    safe_speed,
    threshold_m=0.50
)

drive_commands = []
safe_speed.subscribe(drive_commands.append)

odometry_node.create_service("/reset_odometry", reset_odometry)

desired_speed.publish(0.40)
front_distance.publish(0.35)
assert drive_commands[-1] == 0.0

front_distance.publish(0.80)
assert drive_commands[-1] == 0.40

response = behavior_node.call_service(
    odometry_node,
    "/reset_odometry",
    "reset"
)
assert response == "odometry reset"

# The three safe commands are:
# 1. No distance is known yet: stop.
# 2. The measured distance is 0.35 m: stop.
# 3. The measured distance is 0.80 m: allow 0.40 m/s.
assert drive_commands == [0.0, 0.0, 0.40]

print("First safe command: {:.2f} m/s".format(drive_commands[0]))
print("Second safe command: {:.2f} m/s".format(drive_commands[1]))
print("Third safe command: {:.2f} m/s".format(drive_commands[2]))
print("Service response: {}".format(response))
print("All assertions passed.")
