from enum import Enum


class Status(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3


class Node(object):
    def tick(self, robot):
        raise NotImplementedError

    def halt(self, robot):
        pass


class Condition(Node):
    def __init__(self, test):
        self.test = test

    def tick(self, robot):
        return Status.SUCCESS if self.test(robot) else Status.FAILURE


class Action(Node):
    def __init__(self, function, halt_function=None):
        self.function = function
        self.halt_function = halt_function

    def tick(self, robot):
        return self.function(robot)

    def halt(self, robot):
        if self.halt_function is not None:
            self.halt_function(robot)


class Sequence(Node):
    def __init__(self, children):
        self.children = children
        self.running_index = 0

    def tick(self, robot):
        index = self.running_index

        while index < len(self.children):
            result = self.children[index].tick(robot)

            if result == Status.RUNNING:
                self.running_index = index
                return Status.RUNNING

            if result == Status.FAILURE:
                self.running_index = 0
                return Status.FAILURE

            index += 1

        self.running_index = 0
        return Status.SUCCESS

    def halt(self, robot):
        if self.running_index < len(self.children):
            self.children[self.running_index].halt(robot)
        self.running_index = 0


class Selector(Node):
    def __init__(self, children):
        self.children = children
        self.running_child = None

    def tick(self, robot):
        previous = self.running_child

        for child in self.children:
            result = child.tick(robot)

            if result != Status.FAILURE:
                if previous is not None and previous is not child:
                    previous.halt(robot)

                self.running_child = (
                    child if result == Status.RUNNING else None
                )
                return result

        if previous is not None:
            previous.halt(robot)

        self.running_child = None
        return Status.FAILURE

    def halt(self, robot):
        if self.running_child is not None:
            self.running_child.halt(robot)
        self.running_child = None


class UntilDelivered(Node):
    def __init__(self, child, max_ticks):
        self.child = child
        self.max_ticks = max_ticks
        self.ticks_used = 0

    def tick(self, robot):
        if robot.get("delivered", False):
            return Status.SUCCESS

        if self.ticks_used >= self.max_ticks:
            robot["failure_reason"] = "mission timeout"
            self.child.halt(robot)
            return Status.FAILURE

        self.ticks_used += 1
        result = self.child.tick(robot)

        if robot.get("delivered", False):
            return Status.SUCCESS

        if result == Status.FAILURE:
            robot["failure_reason"] = "all available branches failed"
            return Status.FAILURE

        if self.ticks_used >= self.max_ticks:
            robot["failure_reason"] = "mission timeout"
            self.child.halt(robot)
            return Status.FAILURE

        return Status.RUNNING

    def halt(self, robot):
        self.child.halt(robot)


def battery_is_low(robot):
    return robot["battery"] < 20


def obstacle_is_present(robot):
    return robot["obstacle"]


def recharge_if_needed(robot):
    if robot["battery"] < 20:
        robot["battery"] += 20
        return Status.SUCCESS
    return Status.FAILURE


def avoid_obstacle(robot):
    if robot["obstacle"]:
        robot["obstacle"] = False
        return Status.SUCCESS
    return Status.FAILURE


def drive_to_station(robot):
    if robot["distance"] >= robot["goal_distance"]:
        robot["drive_command_active"] = False
        return Status.SUCCESS

    robot["drive_command_active"] = True
    robot["distance"] += 0.50
    robot["battery"] -= 5

    if robot["distance"] >= robot["goal_distance"]:
        robot["drive_command_active"] = False
        return Status.SUCCESS

    return Status.RUNNING


def halt_drive(robot):
    robot["drive_command_active"] = False


def release_package(robot):
    robot["delivered"] = True
    return Status.SUCCESS


def build_tree():
    recharge_branch = Sequence([
        Condition(battery_is_low),
        Action(recharge_if_needed)
    ])

    avoid_branch = Sequence([
        Condition(obstacle_is_present),
        Action(avoid_obstacle)
    ])

    delivery_branch = Sequence([
        Action(drive_to_station, halt_function=halt_drive),
        Action(release_package)
    ])

    return UntilDelivered(
        Selector([
            recharge_branch,
            avoid_branch,
            delivery_branch
        ]),
        max_ticks=20
    )


class StopIfBlocked(Node):
    def __init__(self):
        self.stop_ticks = 0

    def tick(self, robot):
        if not robot["blocked"]:
            self.stop_ticks = 0
            robot["drive_command_active"] = False
            return Status.SUCCESS

        self.stop_ticks += 1
        robot["drive_command_active"] = False

        if self.stop_ticks >= 3:
            robot["failure_reason"] = "blocked for three ticks"
            return Status.FAILURE

        return Status.RUNNING

    def halt(self, robot):
        robot["drive_command_active"] = False


class SafetyGuard(Node):
    def __init__(self, normal_mission):
        self.stop_if_blocked = StopIfBlocked()
        self.normal_mission = normal_mission
        self.terminal_failure = False

    def tick(self, robot):
        if self.terminal_failure:
            return Status.FAILURE

        if robot["blocked"] or self.stop_if_blocked.stop_ticks > 0:
            self.normal_mission.halt(robot)

            result = self.stop_if_blocked.tick(robot)

            if result == Status.FAILURE:
                self.terminal_failure = True
                return Status.FAILURE

            if result == Status.RUNNING:
                return Status.RUNNING

            return self.normal_mission.tick(robot)

        return self.normal_mission.tick(robot)

    def halt(self, robot):
        self.stop_if_blocked.halt(robot)
        self.normal_mission.halt(robot)


def build_safety_tree():
    return SafetyGuard(build_tree())


def run_block_clears_test():
    robot = {
        "battery": 25,
        "distance": 0.0,
        "goal_distance": 2.0,
        "obstacle": False,
        "blocked": True,
        "delivered": False,
        "failure_reason": None,
        "drive_command_active": False
    }

    tree = build_safety_tree()

    first = tree.tick(robot)
    assert first == Status.RUNNING
    assert robot["distance"] == 0.0
    assert robot["drive_command_active"] is False

    robot["blocked"] = False
    second = tree.tick(robot)

    assert second == Status.RUNNING
    assert robot["distance"] == 0.50
    assert robot["failure_reason"] is None


def run_persistent_block_test():
    robot = {
        "battery": 25,
        "distance": 0.0,
        "goal_distance": 2.0,
        "obstacle": False,
        "blocked": True,
        "delivered": False,
        "failure_reason": None,
        "drive_command_active": False
    }

    tree = build_safety_tree()

    first = tree.tick(robot)
    second = tree.tick(robot)
    third = tree.tick(robot)

    assert first == Status.RUNNING
    assert second == Status.RUNNING
    assert third == Status.FAILURE
    assert robot["failure_reason"] == "blocked for three ticks"
    assert robot["distance"] == 0.0
    assert robot["delivered"] is False
    assert robot["drive_command_active"] is False
    assert tree.tick(robot) == Status.FAILURE


def run_safety_tests():
    run_block_clears_test()
    run_persistent_block_test()
    print("Verified: a cleared block permits the normal mission.")
    print("Verified: a persistent block fails on the third blocked tick.")


if __name__ == "__main__":
    run_safety_tests()
