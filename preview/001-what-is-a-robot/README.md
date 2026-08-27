# Class 1: What Is a Robot?

## Where We Are in the Robotics Journey

Welcome to the robotics course. This is Class 1, so we begin with a question that sounds simple but has surprising depth:

**What makes a machine a robot?**

You will meet our course companion, **RoboRover**. RoboRover is a small wheeled machine with motors, a battery, sensors, and a computer. Today, we will not build advanced navigation or control systems. Instead, we will learn how to describe RoboRover accurately.

There is no single universally accepted binary boundary for the word **robot**. Engineers, industries, museums, and textbooks may use the word slightly differently. Therefore, this course uses a clear teaching convention:

**For this course, a robot is a physical machine commonly treated as a robot in engineering practice whose controlled actuators perform a physical task. Its immediate actions may be selected by a human operator, a preprogrammed controller, or autonomous software. This is a working description for teaching, not a universal necessary-and-sufficient test.**

A robot does not need to be fully autonomous. Robot identity and decision authority are separate questions.

## Today We Will Learn

By the end of this class, you should be able to:

- describe a robot using the course working description;
- distinguish a **machine** from a robot;
- identify the physical boundary between a robot and its **environment**;
- distinguish robot identity from **decision authority**;
- compare teleoperation, preprogrammed action, and task-level autonomy;
- preview how **feedback control** uses measurements;
- run a small Python experiment using the same RoboRover hardware in different control modes.

## 2-Minute Recap

There is no previous class. This is the foundation of the course.

Before reading further, make a quick prediction:

> A human uses a handheld controller to drive RoboRover across a room. Is RoboRover a robot?

The answer is **yes, under this course convention**. A human selects the immediate motion, but RoboRover is still a physical machine whose controlled actuators perform a physical task.

Now make a second prediction:

> A thermostat measures room temperature and switches a heater on or off. Is it normally called a robot?

The answer is **no, not normally**, although it uses feedback control.

These examples establish two separate questions:

1. Is the physical system commonly treated as a robot whose controlled actuators perform a physical task?
2. Who or what selects the immediate action, and does measured state influence that action?

## The Big Idea


![A labeled rover diagram shows motors, sensors, battery, and computer inside a machine boundary, with a floor, wall, box, and operator outside.](inline_01.png)

**Figure:** The machine boundary separates RoboRover’s physical components from the environment while allowing commands, measurements, energy, and forces to cross.

Use three layers to analyze a robotic system:

1. **The machine**  
   The physical object: chassis, wheels, motors, battery, sensors, and computer.

2. **The decision authority**  
   The person, stored controller, or software that selects what the machine should do next.

3. **The environment**  
   Relevant parts of the world outside the machine that can affect it or be affected by it: floors, walls, objects, light, people, temperature, and air.

Inspect the figure by tracing what crosses the bold boundary:

- energy travels from the battery to the motors;
- measurements travel from the environment through the sensors;
- forces and motion travel from the motors and wheels into the environment;
- commands may arrive from a human or another computer.

The machine boundary is a **modeling boundary**, not necessarily a visible physical line. It tells us which components we are analyzing as the robot and which outside conditions are part of the environment.

A **component boundary** answers a different question: which physical parts belong to the machine itself. A camera mounted on RoboRover is a robot component. A remote operator is outside the robot, even though the operator’s commands influence it. Wireless communication may cross the modeling boundary without making the transmitter part of the rover. Similarly, wireless power can cross the boundary while the power source remains outside it. Environmental forces, such as friction from the floor or contact with a wall, also cross the boundary without becoming robot components.

A machine is commonly treated as a robot under this course convention when its controlled actuators perform a physical task. An **actuator** is a device that creates physical action, such as a motor turning a wheel or a gripper closing.

A calculator performs computation, but it does not usually perform a physical task through controlled actuators. A motorized robotic arm does.

## See It in Your Head

### AI-Generated Engineering Visual · Professor OS

![Professor OS engineering schematic](diagram.png)

**How to read this visual:** Trace the signal or idea from left to right. Match each block to the lesson explanation, then predict what would change if one block produced a wrong value.

Use the visual to locate four elements:

- **machine components:** actuators, sensors, battery, and computer;
- **decision authority:** the source that selects commands;
- **environment:** objects and surfaces outside the machine;
- **cross-boundary flows:** commands, measurements, energy, and physical forces.

Picture RoboRover beside a red storage box:

- RoboRover’s left and right wheels are actuators.
- A distance sensor measures how far the box is away.
- A small computer receives commands.
- The box and floor belong to the environment.
- The robot may be driven by a person, follow a stored sequence, or choose actions using software.

Now freeze the hardware and change only the decision authority:

- **Teleoperated RoboRover:** a human presses forward, left, or stop.
- **Preprogrammed RoboRover:** a stored sequence selects the actions.
- **Autonomous RoboRover:** software selects task-level actions from available information.

The physical machine remains the same. The control mode changes, but RoboRover’s robot identity does not automatically disappear.

> Keep the chassis, motors, battery, and sensors unchanged. Change only who chooses the next command. Describe what changed—and what did not.

What changed is the **decision authority**. What did not change is the physical machine performing the task.

## Core Concept


![Three panels show identical rover hardware controlled respectively by a human, a stored program, and onboard autonomous software.](inline_02.png)

**Figure:** The same physical rover can be teleoperated, preprogrammed, or autonomous depending on who or what selects its immediate actions.

### Machine

A **machine** is a physical system designed to transform energy and information into useful action. A washing machine, electric drill, elevator, and robot arm are all machines.

Not every machine is commonly called a robot. Under this course convention, robot identity focuses on a physical machine, controlled physical action, and a physical task. Sensing, computation, and command selection may be present in different forms; they do not by themselves determine the classification.

Real engineering language contains boundary cases, so this description is a teaching convention rather than a universal test.

### Environment

A robot’s environment is the relevant world outside the machine boundary. For RoboRover, it might include:

- the floor that supports its wheels;
- a box that it must approach;
- a wall that can block motion;
- lighting that affects a camera;
- a person who operates it.

Ask:

> What crosses the machine boundary, and which side contains the component being analyzed?

Information can cross through sensors and communication. Energy can cross through contact or wireless power. Forces can cross through wheels, arms, tools, or collisions. These flows do not automatically change which physical components belong to the machine.

### Autonomy

In ordinary robotics usage, **autonomy** means that software selects task-level actions without a human choosing every immediate motion.

Autonomy is not the same as intelligence, consciousness, or independence from all humans. An autonomous vacuum may still have a human-set schedule and charging station. Its autonomy concerns how it selects task-level actions during operation.

A teleoperated robot can be a robot without task-level autonomy. An autonomous system can also be limited: it may operate only in a mapped room, at a restricted speed, or under a human emergency-stop system.

### Feedback: an introductory preview

**Feedback control** broadly means that a measured state or output influences the current or a future control action in relation to a desired behavior or state.

A thermostat provides a simple example:

- desired room temperature: the setpoint;
- measured room temperature: the sensor reading;
- action: switch heating on or off.

If the measured temperature is below the setpoint, the heater may turn on. If it is above the setpoint, the heater may turn off. The rule is predetermined, but the action responds to a measurement.

Threshold and hysteresis controllers can therefore be feedback controllers. Feedback does not have to be continuous or proportional.

In this course, we will use **sustained feedback regulation** when we specifically mean repeated measurement-and-correction over time.

A one-shot sensor event is different. If a sensor detects an object once and starts a fixed five-second motor sequence, but later measurements do not alter that sequence, the event is not sustained feedback regulation merely because a sensor started it.

### One compact comparison

| System | Commonly called a robot? | Immediate decision authority | Feedback in the described behavior? |
|---|---|---|---|
| Timer-controlled traffic signal | Not normally | Preprogrammed timer | No; timing follows the stored schedule |
| Thermostat | Not normally | Preprogrammed feedback rule | Yes; measured temperature affects heating |
| Teleoperated rover | Yes | Human operator | Local feedback may or may not exist |
| Industrial robot arm | Yes | Often a preprogrammed task sequence | Local feedback is common |
| Autonomous vacuum | Yes | Software selects task-level actions | Feedback is commonly used |

A preprogrammed task can include feedback in a subsystem. For example, an industrial arm may follow a stored sequence while its joint controllers use motor-position measurements. “Preprogrammed” and “feedback” are not mutually exclusive categories.

Automatic doors are a boundary case. They share sensing, computation, and actuation with some robots, but terminology varies by context. We will not use them as a scored yes-or-no classification test.

## Math Without Fear

A physical task involves quantities such as distance, time, and speed.

Suppose RoboRover travels at a constant speed of:

\[
v = 0.20\ \text{m/s}
\]

where:

- \(v\) is speed, measured in metres per second;
- \(t\) is time, measured in seconds;
- \(d\) is distance, measured in metres.

For constant speed:

\[
d = vt
\]

If RoboRover travels for:

\[
t = 15\ \text{s}
\]

then:

\[
d = (0.20\ \text{m/s})(15\ \text{s}) = 3.0\ \text{m}
\]

The seconds cancel:

\[
\frac{\text{m}}{\text{s}}\times \text{s}=\text{m}
\]

**Interpretation:** RoboRover’s controlled actuators have produced physical motion through a 3.0-metre distance. This is a physical task, even if a human selected every movement.

Real robots rarely move at exactly constant speed. Floors, battery voltage, wheel slip, motor variation, and load can change the actual distance. The equation is a model: useful, but not perfect.

## Worked Robotics Example


![A wheeled rover with an inspection camera travels from a start line to a work area 3 metres away in a laboratory test scene.](inline_03.png)

**Figure:** At a simplified constant speed of 0.20 m/s for 15 s, the modeled travel distance is 3.0 m; real robots may differ because of slip, battery changes, and calibration errors.

RoboRover must move a lightweight inspection camera from a starting mark to a work area 3.0 metres away.

Its wheel motors are commanded to produce an approximate speed of \(0.20\ \text{m/s}\). If the command remains active for \(15\ \text{s}\):

\[
d = vt
\]

\[
d = (0.20\ \text{m/s})(15\ \text{s}) = 3.0\ \text{m}
\]

The controlled actuators perform a physical task: they move the machine and its camera.

Now compare three ways of selecting the command:

1. A person holds the forward button for 15 seconds.  
   RoboRover is teleoperated.

2. A controller stores “drive forward for 15 seconds.”  
   RoboRover performs a preprogrammed task.

3. Software measures position and decides when to stop near 3.0 metres.  
   RoboRover uses task-level autonomy.

The numerical motion model is similar, but the decision authority differs.

### Engineering caveat: calibration and drift

The command “0.20 m/s” may not produce exactly \(0.20\ \text{m/s}\). One wheel may be slightly faster than the other. The floor may be slippery. The battery voltage may fall during operation. If the wheels slip, the motors can turn without producing the expected movement.

This is why real robots need measurements, testing, and calibration. A controller that assumes perfect motion may stop too early, too late, or at an angle.

## Python Lab


![A horizontal track compares three simulated rover position traces for teleoperated, preprogrammed, and autonomous command selection.](inline_04.png)

**Figure:** The simulation keeps hardware and speed constant while changing only the source of the motion commands.

This Python 3.7 program uses one simple RoboRover model in three modes:

- `teleoperated`: a human’s command list represents immediate choices;
- `preprogrammed`: a stored command sequence runs;
- `autonomous`: software chooses forward or stop using a measured simulated position.

The sensor in this first model is **idealized**: it reports the rover’s internal simulated position exactly. It is included to preview the structure of feedback without modeling noise or delay.

The command values mean:

- `1`: drive forward;
- `0`: stop;
- `-1`: drive backward.

### Predict before running

Complete the final-position cells before running the program:

| Mode | Command sequence or rule | Predicted final position (m) |
|---|---|---:|
| Teleoperated | `[1, 0, -1, 0]` | |
| Preprogrammed | `[1, 1, 1, 0]` | |
| Autonomous | Move forward while measured position is below \(2.0\ \text{m}\) | |

The program is deliberately small. It does not model a real motor, battery, or noisy sensor. It is a learning model for separating hardware from decision authority.

```python
# Python 3.7-compatible RoboRover Class 1 experiment

class RoboRover:
    def __init__(self, speed_m_per_s=0.5):
        self.position_m = 0.0
        self.speed_m_per_s = speed_m_per_s

    def step(self, command, duration_s):
        """Move according to a command for a specified time."""
        if command not in (-1, 0, 1):
            raise ValueError("command must be -1, 0, or 1")

        self.position_m += command * self.speed_m_per_s * duration_s
        return self.position_m

    def read_position_sensor(self):
        """Return an idealized position measurement."""
        return self.position_m


def run_rover(mode, target_m=2.0):
    rover = RoboRover(speed_m_per_s=0.5)
    positions_m = []

    if mode == "teleoperated":
        # Imagine a human pressing buttons during four one-second intervals.
        commands = [1, 0, -1, 0]
        for command in commands:
            positions_m.append(rover.step(command, 1.0))

    elif mode == "preprogrammed":
        # A stored sequence runs without a human choosing each step.
        commands = [1, 1, 1, 0]
        for command in commands:
            positions_m.append(rover.step(command, 1.0))

    elif mode == "autonomous":
        # Software uses the idealized measured position to choose each command.
        for unused_step in range(4):
            measured_position_m = rover.read_position_sensor()
            if measured_position_m < target_m:
                command = 1
            else:
                command = 0
            positions_m.append(rover.step(command, 1.0))

    else:
        raise ValueError("unknown mode")

    return positions_m


def main():
    print("RoboRover Class 1 experiment")
    print("Choose: teleoperated, preprogrammed, or autonomous")

    try:
        selected_mode = input("Mode: ").strip().lower()
    except EOFError:
        selected_mode = "autonomous"

    if selected_mode not in ("teleoperated", "preprogrammed", "autonomous"):
        print("Unknown choice; running autonomous mode.")
        selected_mode = "autonomous"

    selected_positions = run_rover(selected_mode)
    print("Selected mode:", selected_mode)
    print("Positions after each 1-second step:", selected_positions)
    print("Final position: {:.1f} m".format(selected_positions[-1]))

    # Verification checks for the experiment's exact claims.
    teleoperated_positions = run_rover("teleoperated")
    preprogrammed_positions = run_rover("preprogrammed")
    autonomous_positions = run_rover("autonomous")

    assert teleoperated_positions == [0.5, 0.5, 0.0, 0.0]
    assert preprogrammed_positions == [0.5, 1.0, 1.5, 1.5]
    assert autonomous_positions == [0.5, 1.0, 1.5, 2.0]

    assert teleoperated_positions[-1] == 0.0
    assert preprogrammed_positions[-1] == 1.5
    assert autonomous_positions[-1] == 2.0

    print("All verification checks passed.")


if __name__ == "__main__":
    main()
```

Important lines:

- `self.position_m` represents RoboRover’s simulated position in metres.
- `self.speed_m_per_s` represents the simplified forward speed.
- `step()` models an actuator command changing the physical position.
- `read_position_sensor()` represents a separate, idealized measurement.
- The teleoperated list represents a human’s immediate choices.
- The preprogrammed list is selected before the run.
- The autonomous mode reads the measured position before choosing forward or stop.
- The `assert` statements automatically test the exact traces and final positions.

The autonomous model is intentionally modest. It does not understand the whole world. It simply selects a task-level action using an idealized position measurement.

## Mini Simulation or Game

Play “control-room operator” with the code.

1. Complete the prediction table.
2. Run the program once in each mode.
3. Compare the printed position lists with your predictions.
4. Change the teleoperated command list.
5. Predict how the final position will change before running again.
6. Change `target_m=2.0` to `1.0` in the autonomous call and update the assertions only after reasoning about the result.

The same simulated chassis, sensor model, and speed are used in every mode. Only the source of the commands changes.

This is a useful robotics habit:

> When comparing two robot systems, identify which physical components changed and which decision process changed.

## What Should Happen?

The verification checks show:

- teleoperated RoboRover ends at \(0.0\ \text{m}\);
- preprogrammed RoboRover ends at \(1.5\ \text{m}\);
- autonomous RoboRover ends at \(2.0\ \text{m}\).

These values follow directly from the commands and the speed of \(0.5\ \text{m/s}\):

- forward for one second changes position by \(+0.5\ \text{m}\);
- stopped for one second changes position by \(0\ \text{m}\);
- backward for one second changes position by \(-0.5\ \text{m}\).

The important lesson is not that autonomy always gives the “best” result. It is that **decision authority can change while robot identity and hardware remain the same**.

## Common Mistakes

### Mistake 1: “A robot must be autonomous.”

Not under this course convention. A teleoperated rover is still a robot.

### Mistake 2: “Anything with a sensor is a robot.”

Sensors are common in many machines and appliances. A sensor alone does not settle robot identity.

### Mistake 3: “Preprogrammed means no feedback.”

A preprogrammed task can include feedback in a subsystem. An industrial robot arm may follow a stored sequence while its joint controllers use position measurements.

### Mistake 4: “A sensor trigger always means closed-loop feedback.”

A one-shot sensor event that starts a fixed timed sequence is not sustained feedback regulation merely because a sensor was involved. Ask whether later measured state affects the current or a future action.

### Mistake 5: “The mathematical model is reality.”

The Python model assumes constant speed and an idealized position measurement. Real robots experience noise, delay, wheel slip, limited motor torque, calibration errors, and mechanical stops.

## Try It Yourself

### Challenge

Modify the program so RoboRover has a fourth mode called `manual_reverse`.

In this mode, use four commands:

```python
[1, 1, -1, 0]
```

Predict the position after each one-second step, then add an assertion that verifies your prediction.

Explain in one sentence:

> Is `manual_reverse` a different robot, or the same robot with a different sequence of immediate commands?

### Optional extension

Keep the original `RoboRover` class unchanged and create a separate miniature example of sensor error:

```python
class SensorErrorExample:
    def __init__(self, actual_position_m=0.0, error_m=0.1):
        self.actual_position_m = actual_position_m
        self.error_m = error_m

    def read_position_sensor(self):
        return self.actual_position_m + self.error_m


example = SensorErrorExample(actual_position_m=1.5, error_m=0.1)

print("Actual position:", example.actual_position_m)
print("Measured position:", example.read_position_sensor())

assert example.read_position_sensor() == 1.6
```

This example separates the actual position from the measured position. A real autonomous controller would use the measurement, not direct access to the actual value.

Discuss how a measurement error could cause software to stop too early or continue too long. This is only a preview; later classes will address more realistic sensor models.

## Quick Quiz

1. Under the course working description, can a teleoperated rover be a robot?

2. What is the environment for RoboRover?

3. Which system is normally not called a robot but clearly uses feedback: a timer-controlled traffic signal or a thermostat?

4. What is the difference between robot identity and decision authority?

## Answers

1. **Yes.** RoboRover is a physical machine whose controlled actuators perform a physical task. A human selects the immediate motion, but that does not remove its robot identity.

2. The environment includes relevant things outside the machine boundary, such as the floor, walls, boxes, lighting, people, and other objects. The exact boundary is a modeling choice for analyzing the system; it does not imply that every communication, power, or force source is part of the robot.

3. **The thermostat.** Its measured temperature affects whether heating turns on or off. The timer-controlled traffic signal follows its timing schedule in the behavior described.

4. Robot identity describes the physical machine and its controlled physical task. Decision authority describes who or what selects the immediate action: a human operator, a preprogrammed controller, or autonomous software.

## Real Robot Connection

In a real RoboRover, the command “drive forward” might pass through several layers:

1. a human, stored task, or autonomous program selects a desired action;
2. a motor controller sends electrical power to the wheel motors;
3. the wheels produce force against the floor;
4. sensors may measure wheel rotation, position, distance, or obstacles;
5. later commands may be adjusted using those measurements.

The exact system boundary depends on the engineering question. For example, the rover’s onboard computer and sensors may be included as robot components, while a remote operator, communication link, or external power source may be modeled as outside the robot. Commands, measurements, energy, and environmental forces can still cross that boundary.

Even this simple chain has failure modes:

- a motor may not start at low power;
- left and right wheels may rotate at different speeds;
- a sensor may report noisy or delayed measurements;
- a battery may provide less voltage as it discharges;
- a wheel may slip on a smooth floor;
- a physical bumper may limit motion.

Robotics engineering is the practice of making useful physical behavior despite these imperfections.

Before moving on, retrieve the three questions from this class:

- What physical machine and task are we analyzing?
- What is inside the machine boundary, and what is in the environment?
- Who or what selects the next action, and what measurements can influence it?

## Vocabulary

**Robot:** For this course, a robot is a physical machine commonly treated as a robot in engineering practice whose controlled actuators perform a physical task. Its immediate actions may be selected by a human operator, a preprogrammed controller, or autonomous software. This is a working description for teaching, not a universal necessary-and-sufficient test.

**Machine:** A physical system designed to transform energy and information into useful action.

**Environment:** The relevant world outside the robot’s machine boundary that can affect the robot or be affected by it.

**Actuator:** A device that creates physical action, such as a motor, wheel drive, or gripper mechanism.

**Decision authority:** The person, stored controller, or software that selects the robot’s immediate action.

**Teleoperation:** Operation in which a human selects immediate commands for a robot, usually through a remote controller or interface.

**Preprogrammed task execution:** Operation in which a stored sequence or rule selects actions according to instructions prepared in advance.

**Autonomy:** The ability of software to select task-level actions without a human choosing every immediate motion.

**Feedback control:** Control in which a measured state or output influences a current or future control action in relation to a desired behavior or state.

**Sustained feedback regulation:** Repeated measurement-and-correction over time.

**Sensor:** A device that measures some aspect of the robot or environment.

## Further Learning

To deepen this class, investigate these topics in this order:

1. Read an introductory explanation of **robot sensors, actuators, and controllers**.
2. Look for engineering demonstrations of **teleoperated mobile robots**.
3. Compare a **thermostat feedback loop** with a timer-controlled device.
4. Sketch the machine boundary around RoboRover and label every signal, force, and energy flow you can identify.

As you study, keep asking:

> What is the physical task, and who or what chooses the next action?

Those questions will remain useful throughout the course.

## Next Class

In Class 2, **Sense → Think → Act**, we will examine the basic cycle inside many robotic systems:

- **Sense:** gather information with sensors;
- **Think:** interpret information and choose an action;
- **Act:** use actuators to affect the environment.

This cycle will build directly on today’s machine–environment boundary and decision-authority ideas. We will begin examining how information moves through a robot, without yet needing advanced algorithms.