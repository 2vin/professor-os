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
        previous_running_child = self.running_child

        for child in self.children:
            result = child.tick(robot)

            if result != Status.FAILURE:
                if (
                    previous_running_child is not None
                    and previous_running_child is not child
                ):
                    previous_running_child.halt(robot)

                self.running_child = (
                    child if result == Status.RUNNING else None
                )
                return result

        if previous_running_child is not None:
            previous_running_child.halt(robot)

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


def run_permanently_running_timeout_test():
    robot = {"delivered": False, "failure_reason": None}
    tree = UntilDelivered(
        Action(lambda state: Status.RUNNING),
        max_ticks=20
    )

    result = None
    for evaluation in range(20):
        result = tree.tick(robot)
        if evaluation < 19:
            assert result == Status.RUNNING

    assert result == Status.FAILURE
    assert tree.ticks_used == 20
    assert robot["failure_reason"] == "mission timeout"


def run_success_without_delivery_timeout_test():
    robot = {"delivered": False, "failure_reason": None}
    tree = UntilDelivered(
        Action(lambda state: Status.SUCCESS),
        max_ticks=3
    )

    result = None
    for evaluation in range(3):
        result = tree.tick(robot)
        if evaluation < 2:
            assert result == Status.RUNNING

    assert result == Status.FAILURE
    assert tree.ticks_used == 3
    assert robot["failure_reason"] == "mission timeout"
    assert robot["delivered"] is False


def main():
    robot = {
        "battery": 15,
        "distance": 0.0,
        "goal_distance": 2.0,
        "obstacle": True,
        "delivered": False,
        "failure_reason": None,
        "drive_command_active": False
    }

    tree = build_tree()
    ticks = 0

    while True:
        ticks += 1
        result = tree.tick(robot)
        print(
            "tick={0}, result={1}, distance={2:.2f} m, "
            "battery={3}, obstacle={4}, delivered={5}".format(
                ticks,
                result.name,
                robot["distance"],
                robot["battery"],
                robot["obstacle"],
                robot["delivered"]
            )
        )

        if result != Status.RUNNING:
            break

    assert result == Status.SUCCESS
    assert robot["delivered"] is True
    assert ticks == 6
    assert robot["distance"] == 2.0
    assert robot["battery"] == 15
    assert robot["obstacle"] is False
    assert robot["failure_reason"] is None
    assert robot["drive_command_active"] is False

    run_permanently_running_timeout_test()
    run_success_without_delivery_timeout_test()

    print("Verified: delivery completed in 6 ticks.")
    print("Verified: final distance is 2.0 m.")
    print("Verified: final battery is 15 energy units.")
    print("Verified: permanent RUNNING tree timed out on evaluation 20.")
    print("Verified: undelivered SUCCESS also timed out on evaluation 3.")


if __name__ == "__main__":
    main()
