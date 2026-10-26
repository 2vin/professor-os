class Topic:
    def __init__(self, name):
        self.name = name
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish(self, message):
        for callback in self.subscribers:
            callback(message)


drive_commands = []
drive_status = Topic("/drive_status")
drive_status_messages = []
drive_status.subscribe(drive_status_messages.append)


def record_drive_command(speed_mps):
    drive_commands.append(speed_mps)
    if speed_mps == 0.0:
        drive_status.publish("STOPPED")
    elif speed_mps > 0.0:
        drive_status.publish("MOVING")


safe_speed = Topic("/safe_speed")
safe_speed.subscribe(record_drive_command)

desired_speed = Topic("/desired_speed")
front_distance = Topic("/front_distance")

distance_m = None
desired_speed_mps = 0.0
threshold_m = 0.50


def publish_safe_command():
    if distance_m is None or distance_m < threshold_m:
        safe_speed.publish(0.0)
    else:
        safe_speed.publish(desired_speed_mps)


def receive_desired_speed(speed_mps):
    global desired_speed_mps
    desired_speed_mps = speed_mps
    publish_safe_command()


def receive_distance(distance):
    global distance_m
    distance_m = distance
    publish_safe_command()


desired_speed.subscribe(receive_desired_speed)
front_distance.subscribe(receive_distance)

# Use the modified subscriber before publishing commands.
desired_speed.publish(0.40)
front_distance.publish(0.35)
assert drive_status_messages[-1] == "STOPPED"

front_distance.publish(0.80)
assert drive_status_messages[-1] == "MOVING"
