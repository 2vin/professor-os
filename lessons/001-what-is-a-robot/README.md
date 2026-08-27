# Class 1: What Is a Robot?

## Where We Are in the Robotics Journey

Welcome to the robotics course. This is Class 1, so there is no previous robotics class to review. We will begin with a question that sounds simple but has several careful answers:

**What makes a machine a robot?**

Throughout the course, we will follow a fictional machine called **RoboRover**. RoboRover is a small wheeled machine with:

- two powered wheels;
- a battery;
- a simple computer;
- sensors that can measure parts of its surroundings;
- controlled actuators, such as motors, that can create motion.

Today, we will not yet design a navigation algorithm or a feedback controller. Instead, we will learn how to describe RoboRover accurately.

## Today We Will Learn

By the end of this class, you should be able to:

1. use the course’s working description of a robot;
2. distinguish a robot’s identity from who or what chooses its actions;
3. explain the difference between a machine and its environment;
4. describe autonomy as a decision-making relationship, not as a magical robot property;
5. recognize feedback as a preview concept;
6. compare several real systems without forcing every boundary case into a yes/no definition;
7. run a small Python simulation showing the same RoboRover hardware under different decision authorities;
8. classify an unfamiliar example by identifying its machine boundary, decision authority, and feedback status.

**Observation prompt:** When you encounter an unfamiliar machine, identify three things: What physical system is the machine? Who or what selects its immediate action? Does measured state influence a current or future control action?

## 2-Minute Recap

There is no previous class in this course. Begin with this mental picture:

> A robot is a physical machine whose controlled actuators perform a physical task. Its immediate actions may be selected by a human operator, a preprogrammed controller, or autonomous software.

Imagine RoboRover sitting on a laboratory floor. The rover is the **machine**. The floor, walls, objects, light, and people around it are parts of its **environment**. The motors change the rover’s physical state. Sensors can measure parts of the environment or the rover itself.

Keep two questions separate:

1. **Is the physical system commonly called a robot?**
2. **Who or what selects its immediate actions?**

Those questions are related, but they are not the same question.

## The Big Idea


![Three panels show identical RoboRover hardware controlled by a human operator, a stored program, and autonomous software.](inline_01.png)

**Figure:** The rover’s robot identity can stay the same while the source of immediate decisions changes.

For this course, use this working description:

> **For this course, a robot is a physical machine commonly treated as a robot in engineering practice whose controlled actuators perform a physical task. Its immediate actions may be selected by a human operator, a preprogrammed controller, or autonomous software. This is a working description for teaching, not a universal necessary-and-sufficient test.**

This description deliberately allows three kinds of immediate decision authority:

- **Human-directed:** a person selects the rover’s immediate motion command.
- **Preprogrammed:** a controller follows instructions prepared earlier.
- **Autonomous:** software selects task-level actions using its operating rules and available information.

A teleoperated rover can therefore be a robot even though a human chooses its immediate movement. An industrial robot arm can be a robot even when it follows a preprogrammed sequence. An autonomous vacuum can be a robot because software selects task-level actions.

There is no single universally accepted binary boundary for the word **robot**. Engineers, manufacturers, researchers, and ordinary users may use the word differently in some borderline situations. We will not pretend that one test settles every case. Instead, we will use clear engineering examples and the course working description above.

## See It in Your Head

### AI-Generated Engineering Visual · Professor OS

![Professor OS engineering schematic](diagram.png)

**How to read this visual:** Trace the signal or idea from left to right. Match each block to the lesson explanation, then predict what would change if one block produced a wrong value.



Picture an overhead view of a small blue RoboRover on a rectangular laboratory floor.

Draw a dashed outline around the rover. Inside the outline are:

- the wheels;
- motors;
- battery;
- computer;
- sensors;
- chassis.

Outside the outline are:

- a red box;
- a wall;
- a person holding a controller;
- patches of bright and dim light;
- the floor surface.

Now draw arrows:

- **Sensor arrows** point from the environment toward the rover.
- **Actuator arrows** point from the rover toward the wheels and physical surroundings.
- A **human command arrow** may point from the operator to the rover.
- A **program arrow** may point from stored instructions to the rover’s controller.

The boundary matters because a robot is a physical system interacting with something outside itself. A camera mounted on RoboRover is part of the robot. The red box being observed is part of the environment, unless we deliberately define a larger system boundary that includes it.

A system boundary is an engineering choice. For example, when studying a robot arm moving a part, we usually describe the arm as the machine and the part, workbench, and surrounding workspace as its environment.

## Core Concept

### Robot identity and decision authority

Suppose we build three identical RoboRovers with the same motors, wheels, sensors, and battery.

- Rover A is driven by a person using a joystick.
- Rover B repeats a stored sequence: forward, forward, turn, stop.
- Rover C chooses its next task-level action using software.

The hardware is the same. The decision authority changes.

This is the important lesson:

> **Robot identity and control mode are separate questions.**

A system can be:

- a robot without task-level autonomy;
- a robot with preprogrammed task execution;
- a robot with task-level autonomy;
- a non-robot appliance that still uses feedback control.

### A compact comparison

| System | Commonly called a robot? | Immediate decision authority | Feedback in the described behavior? |
|---|---|---|---|
| Timer-controlled traffic signal | Not normally | Preprogrammed timer | No, in the described timing behavior |
| Thermostat | Not normally | Preprogrammed feedback rule | Yes |
| Teleoperated rover | Yes | Human operator | May or may not have local feedback |
| Industrial robot arm | Yes | Often a preprogrammed task sequence | Local feedback is common |
| Autonomous vacuum | Yes | Software selects task-level actions | Feedback is commonly used |

The phrase **fixed automation** can describe a timer-controlled sequence, but it is not a mutually exclusive control category. A system may execute a preprogrammed task while one of its subsystems uses feedback.

### A short feedback preview

Feedback means that a measured state or output influences the current or a future control action in relation to a desired behavior or state.

A compact representation is:

> **measure → compare with desired state → act → measure again**

A thermostat provides a useful example:

1. A person sets a desired temperature, such as \(20\,^\circ\text{C}\).
2. The thermostat measures the room temperature.
3. If the measured temperature is below the rule’s heating threshold, it turns heating on.
4. If the measured temperature reaches the relevant threshold, it turns heating off.

The rule is predetermined, but the action responds to a measurement. That is feedback control. Feedback does not have to be continuous or proportional. A threshold or hysteresis rule can still be feedback.

Textbook terminology can vary with the chosen system boundary. In this course, a threshold measurement-to-action relationship can count as feedback control; we use **sustained feedback regulation** specifically for repeated measurement-and-correction over time.

A sensor-triggered event needs more care. If a sensor detects an object once and starts a fixed timed sequence, but the later actions do not use the measured state again, we will not call that sustained feedback regulation merely because a sensor started the sequence.

Task-level autonomy and feedback are independent. Software may select task-level actions without the example demonstrating feedback, and a non-autonomous device may use feedback to regulate a physical variable.

## Math Without Fear

A simple equation helps us describe a physical task.

If a rover moves at a constant speed, its ideal travel distance is:

\[
d = vt
\]

where:

- \(d\) is distance traveled, measured in meters \((\text{m})\);
- \(v\) is speed, measured in meters per second \((\text{m/s})\);
- \(t\) is elapsed time, measured in seconds \((\text{s})\).

For RoboRover, suppose:

\[
v = 0.60\ \text{m/s}
\]

and

\[
t = 4.0\ \text{s}
\]

Then:

\[
d = (0.60\ \text{m/s})(4.0\ \text{s}) = 2.4\ \text{m}
\]

The seconds cancel:

\[
\frac{\text{m}}{\text{s}}\times\text{s}=\text{m}
\]

So the ideal prediction is that RoboRover travels **2.4 meters**.

This is a model, not a guarantee. It assumes the rover really maintains \(0.60\ \text{m/s}\), starts immediately, travels straight, and does not slip or collide.

## Worked Robotics Example


![A two-wheeled rover moves along a measured track toward a target, with speed, time, and ideal distance represented in a technical overlay.](inline_02.png)

**Figure:** The ideal distance prediction comes from speed multiplied by time, while real motion can differ because of slip, delay, and calibration.

RoboRover is asked to deliver a lightweight sensor package to a marked location **2.4 m** away.

Its motor controller is set for an ideal forward speed of \(0.60\ \text{m/s}\). The stored task says:

> Drive forward for \(4.0\ \text{s}\), then stop.

Using \(d=vt\):

\[
d=(0.60\ \text{m/s})(4.0\ \text{s})=2.4\ \text{m}
\]

### Interpretation

The rover’s controlled actuators—the wheel motors—perform the physical task. The stored controller selects the immediate action. Under our course description, this is a robot performing a preprogrammed task.

However, the calculation is only an ideal prediction. Real results can differ because:

- the battery voltage changes as it discharges;
- the wheels may slip on the floor;
- the motor speed may not exactly match the setting;
- the rover may start after a small command delay;
- one wheel may produce slightly more torque than the other;
- the floor may not be perfectly level.

If the rover stops at \(2.2\ \text{m}\), the equation has not become useless. It has shown us that one or more assumptions were inaccurate. Engineering often means comparing a model with a measurement and investigating the difference.

## Python Lab

This program uses the **same RoboRover hardware** in three modes:

1. human-directed;
2. preprogrammed;
3. autonomous at the task level.

The simulation is intentionally simple. RoboRover moves along a straight one-dimensional track from \(0.0\ \text{m}\) toward a target at \(5.0\ \text{m}\). Each forward command moves it \(1.0\ \text{m}\).

The program does not prove that one mode is “more robotic.” It demonstrates that decision authority can change while the physical machine stays the same.

The autonomous mode is deliberately simplified: its software reads an **idealized internal simulated position variable**, not a simulated sensor measurement. It therefore demonstrates software decision authority, not perception, sensor processing, navigation, planning, or meaningful adaptation to an uncertain environment. The autonomous rule is deterministic and has no feedback sensor model.

```python
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
```

### Important lines

- `commands` represents immediate motion decisions.
- `move_rover(commands)` represents the physical machine responding to actuator commands.
- In `"programmed"` mode, the list is prepared before the run.
- In `"autonomous"` mode, software checks its idealized simulated position before selecting each command.
- The assertions are executable checks. They stop the program with an error if the verified claims are false.

For human mode, enter one value when each prompt appears. For example, enter `1`, then `1`, then `0`, then `1`, then `1`. The person is choosing each immediate action. The program still models the same motors and track.

## Mini Simulation or Game

### RoboRover decision-authority challenge

Run the Python program three times.

Before each run, predict:

1. Will the hardware model change?
2. Who or what selects the immediate commands?
3. Will the final position necessarily be the same?

Try these runs:

- **Human:** when prompted, enter five values separately: `1`, `1`, `1`, `1`, `1`.
- **Programmed:** allow the stored list to run.
- **Autonomous:** allow the deterministic software rule to run.

Now run human mode again and enter these five values separately, one at each prompt:

```text
1
1
0
1
0
```

Predict the final position before running the program. Each `1` means one forward step of \(1.0\ \text{m}\), and each `0` means stop for that step.

This is not a navigation lesson. There is no map, path planner, perception module, or search algorithm here. The purpose is to observe the relationship between the physical machine and decision authority.

## What Should Happen?

For programmed mode:

- the commands are `[1, 1, 1, 1, 1]`;
- RoboRover reaches \(5.0\ \text{m}\).

For autonomous mode:

- the software also selects `[1, 1, 1, 1, 1]`;
- RoboRover reaches \(5.0\ \text{m}\).

The code verifies both exact claims with assertions.

For human mode with commands \(1,1,0,1,0\):

\[
d=(1+1+0+1+0)(1.0\ \text{m})=3.0\ \text{m}
\]

The rover stops at \(3.0\ \text{m}\). Here, the human selected the immediate actions, but the physical system is still a rover commonly treated as a robot.

## Common Mistakes

### Mistake 1: “A robot must be autonomous.”

Not in this course. A teleoperated rover is a robot. Autonomy describes who or what selects task-level actions; it does not alone determine robot identity.

### Mistake 2: “Anything with a sensor is a robot.”

Too broad. Many machines and appliances use sensors. A thermostat uses feedback, but it is not normally called a robot.

### Mistake 3: “Preprogrammed means no feedback.”

Not necessarily. An industrial robot arm may repeat a preprogrammed task while joint controllers use measured position information to regulate motion.

### Mistake 4: “A sensor triggered the action, so the system was closed-loop.”

Not automatically. If a sensor event starts a fixed timed sequence and the measured state is not used to adjust later actions, we do not call that sustained feedback regulation.

### Mistake 5: “The equation predicts exactly what a real robot will do.”

The equation predicts an ideal result under stated assumptions. Real robots have calibration errors, delays, saturation limits, wheel slip, mechanical wear, and changing battery conditions.

### Mistake 6: Confusing the machine with its environment

The floor is not usually part of RoboRover’s hardware, even though the rover interacts with it. A sensor reading may describe the environment, the machine, or both, depending on what the sensor measures.

## Try It Yourself

### Challenge: same hardware, three authorities

Use the Python program and record a table with these columns:

| Mode | Who selects immediate commands? | Commands used | Final position |
|---|---|---|---|
| Human |  |  |  |
| Programmed |  |  |  |
| Autonomous |  |  |  |

For the human run, choose a command sequence that contains at least one stop. Enter the values separately when the prompts appear.

Then answer:

1. Did the physical model change between modes?
2. Did the decision authority change?
3. Does a different decision authority automatically make the machine a different kind of physical system?
4. For the autonomous mode, which part of the example represents decision logic, and which part represents the physical model?
5. What would need to be added for the autonomous mode to use actual simulated sensor measurements?

### Optional extension

Modify the program so the target is \(7.0\ \text{m}\) and the rover can take seven steps. Update the constants and the automatic command list. Add an assertion verifying the new final position.

Then inspect the autonomous stopping condition and explain:

- which changes affect the physical model, such as track length or step distance;
- which changes affect decision logic, such as the target comparison or the number of decisions;
- why changing the target does not by itself add perception, navigation, planning, or meaningful environmental adaptation.

Do not change the lesson’s central idea: the extension is still about the same hardware under different decision authorities.

## Quick Quiz

1. According to the course working description, what makes a physical system a robot?

2. A person drives RoboRover with a joystick. Is RoboRover a robot even though it is not choosing its own immediate motion?

3. A thermostat measures room temperature and turns heating on or off according to a predetermined threshold rule. Is this feedback control? Is the thermostat normally called a robot?

4. A sensor detects an object once and starts a fixed \(10\)-second motor sequence. The later motor actions do not use the measured object distance. Should we call this sustained feedback regulation?

## Answers

1. It is a physical machine commonly treated as a robot in engineering practice whose controlled actuators perform a physical task. Its immediate actions may be selected by a human operator, a preprogrammed controller, or autonomous software. This is a teaching description, not a universal necessary-and-sufficient test.

2. Yes. A teleoperated rover is commonly called a robot. Human decision authority does not remove its robot identity.

3. Yes, it is feedback control because measured temperature influences the heating action. The thermostat is not normally called a robot.

4. No, not under the Class 1 convention. The sensor starts the sequence, but the measured state is not repeatedly used to adjust the current or future action. It is not sustained feedback regulation.

## Real Robot Connection


![A technical comparison diagram separates robot identity, who selects actions, and whether measured state affects control actions across five systems.](inline_03.png)

**Figure:** Robot identity, decision authority, and feedback describe different aspects of a system and should not be collapsed into one test.

In a real robot, the distinction between decision authority and robot identity affects engineering questions.

For a teleoperated rover, the operator may decide “drive forward,” but the rover’s local electronics may still regulate motor speed or protect the battery. The human chooses the immediate motion command; task-level intent may or may not be explicitly represented. Local subsystems may handle lower-level physical behavior.

For an industrial robot arm, a stored task may specify a sequence of poses. Sensors and motor controllers can still correct the motion of individual joints. “Preprogrammed” and “feedback-based” are not opposites.

For an autonomous vacuum, software may choose when to move, stop, or change a task-level action. Its sensors provide information about the machine and environment. If a sensor is dirty, a wheel is slipping, or the battery is weak, the intended behavior may differ from the actual behavior.

A practical engineering caveat is **calibration**. Calibration means relating a sensor’s measurement or actuator command to a physical quantity. If RoboRover’s controller assumes that one motor command produces \(0.60\ \text{m/s}\), but the actual speed is lower because of a weak battery or carpet friction, its distance prediction will be wrong. This is why robotics requires both definitions and measurements.

Next class, we will examine a more detailed cycle:

> **Sense → Think → Act**

That cycle will show how information enters a robot, how a decision is selected, and how actuators change the physical world.

## Vocabulary

**Robot:** For this course, a robot is a physical machine commonly treated as a robot in engineering practice whose controlled actuators perform a physical task. Its immediate actions may be selected by a human operator, a preprogrammed controller, or autonomous software. This is a working description for teaching, not a universal necessary-and-sufficient test.

**Machine:** A physical system made from parts that work together to perform functions or tasks. In this class, RoboRover’s chassis, motors, battery, computer, and sensors are parts of the machine.

**Environment:** The physical surroundings and objects that interact with or can be measured by the machine.

**Actuator:** A device that produces a controlled physical effect, such as a motor producing wheel rotation.

**Sensor:** A device that measures some property of the machine or environment.

**Decision authority:** The person, stored program, or autonomous software that selects an immediate action.

**Teleoperation:** Operation in which a human operator selects the robot’s immediate commands, often through a remote controller.

**Autonomy:** The ability of software or a system to select task-level actions during operation without a human selecting every immediate action.

**Feedback control:** Control in which measured state or output influences the current or a future control action in relation to desired behavior or state. Textbook terminology can vary with the chosen system boundary.

**Sustained feedback regulation:** Repeated measurement-and-correction over time. This is the Class 1 course phrase for distinguishing ongoing regulation from a one-shot trigger that starts a fixed sequence.

## Further Learning

To deepen this class, look for beginner resources under these search-friendly names:

- “robotics system boundary and environment”
- “teleoperation versus autonomy in robotics”
- “introductory feedback control thermostat example”
- “industrial robot joint servo feedback”
- “robot sensors actuators beginner laboratory”

When reading, ask three questions of every example:

1. What physical machine is being discussed?
2. Who or what selects the immediate action?
3. Does measured state influence a current or future control action?

Those questions will remain useful throughout the course.

## Next Class

**Class 2: Sense → Think → Act**

Next, we will open RoboRover’s behavior into three connected stages:

- **Sense:** obtain information from sensors;
- **Think:** interpret information and select an action;
- **Act:** command actuators to change the machine or environment.

We will build this cycle from a very small example before adding more sophisticated robotics concepts.