class Topic:
    def __init__(self, name):
        self.name = name
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish(self, message):
        # Simplified conceptual delivery: callbacks run immediately.
        for callback in self.subscribers:
            callback(message)


class Service:
    def __init__(self, name, handler, available=True, response_delay_s=0.0):
        self.name = name
        self.handler = handler
        self.available = available
        self.response_delay_s = response_delay_s

    def call(self, request, timeout_s):
        if not self.available:
            return {
                "accepted": False,
                "reason": "SERVICE_UNAVAILABLE"
            }

        if self.response_delay_s > timeout_s:
            return {
                "accepted": False,
                "reason": "SERVICE_TIMEOUT"
            }

        return self.handler(request)


class Action:
    def __init__(self, name, available=True):
        self.name = name
        self.available = available

    def start(self, goal):
        # This return value models the action goal response:
        # acceptance or rejection of the goal, not final completion.
        if not self.available:
            return {
                "accepted": False,
                "reason": "ACTION_UNAVAILABLE"
            }

        return {
            "accepted": True,
            "status": "RUNNING",
            "goal": goal
        }


class BatteryNode:
    def __init__(self, battery_topic):
        self.battery_topic = battery_topic
        self.voltage = 11.8

    def publish_measurement(self, now_s):
        message = {
            "voltage_v": self.voltage,
            "stamp_s": now_s,
            "source": "battery_node"
        }
        self.battery_topic.publish(message)


class BehaviorTreeNode:
    def __init__(
        self,
        battery_topic,
        docking_service,
        docking_action,
        max_battery_age_s=1.0,
        service_timeout_s=0.5
    ):
        self.latest_battery = None
        self.docking_service = docking_service
        self.docking_action = docking_action
        self.max_battery_age_s = max_battery_age_s
        self.service_timeout_s = service_timeout_s
        battery_topic.subscribe(self.receive_battery)

    def receive_battery(self, message):
        self.latest_battery = message

    def tick(self, now_s):
        if self.latest_battery is None:
            return "WAITING_FOR_BATTERY"

        age_s = now_s - self.latest_battery["stamp_s"]
        if age_s < 0.0 or age_s > self.max_battery_age_s:
            return "STALE_BATTERY"

        voltage = self.latest_battery["voltage_v"]

        if voltage < 11.5:
            # Optional, application-specific readiness/admission check.
            # ROS 2 actions do not require a preceding service.
            response = self.docking_service.call(
                {
                    "reason": "low_battery"
                },
                timeout_s=self.service_timeout_s
            )

            if not response["accepted"]:
                return response["reason"]

            # This models the action's own goal-acceptance response.
            # It is not the final result of docking.
            action_response = self.docking_action.start({
                "reason": "low_battery"
            })

            if action_response["accepted"]:
                return "DOCKING_ACTION_STARTED"

            return action_response["reason"]

        return "CONTINUE_MISSION"


def docking_request_handler(request):
    if request["reason"] == "low_battery":
        return {
            "accepted": True,
            "message": "Docking goal may be started"
        }

    return {
        "accepted": False,
        "reason": "REQUEST_REJECTED"
    }


def main():
    battery_topic = Topic("battery_state")

    # This optional application-specific service models a bounded
    # admission/readiness check before sending the action goal.
    docking_service = Service(
        "request_docking",
        docking_request_handler,
        available=True,
        response_delay_s=0.1
    )

    # The action models the actual long-running docking operation.
    # start() models only the goal response, not final completion.
    docking_action = Action("dock", available=True)

    battery_node = BatteryNode(battery_topic)
    behavior_node = BehaviorTreeNode(
        battery_topic,
        docking_service,
        docking_action,
        max_battery_age_s=1.0,
        service_timeout_s=0.5
    )

    battery_node.publish_measurement(now_s=0.0)
    first_decision = behavior_node.tick(now_s=0.2)
    assert first_decision == "CONTINUE_MISSION"

    battery_node.voltage = 11.2
    battery_node.publish_measurement(now_s=0.5)
    second_decision = behavior_node.tick(now_s=0.6)
    assert second_decision == "DOCKING_ACTION_STARTED"

    stale_decision = behavior_node.tick(now_s=1.7)
    assert stale_decision == "STALE_BATTERY"

    docking_service.available = False
    battery_node.publish_measurement(now_s=2.0)
    unavailable_decision = behavior_node.tick(now_s=2.1)
    assert unavailable_decision == "SERVICE_UNAVAILABLE"

    print("First decision:", first_decision)
    print("Second decision:", second_decision)
    print("Stale-data decision:", stale_decision)
    print("Unavailable-service decision:", unavailable_decision)
    print("Verified: fresh low voltage started a docking action.")
    print("Verified: stale data and service unavailability were detected.")


if __name__ == "__main__":
    main()
