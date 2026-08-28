from teacher_agent.quality import deterministic_quality_checks


BASE_LESSON = """# Class 2: Sense → Think → Act

## Where We Are in the Robotics Journey
We are building a clear mental model of how sensing, deciding, and acting connect in a robot.

## Today We Will Learn
We will connect sensing, control decisions, and movement through a small feedback example.

## 2-Minute Recap
A robot is a physical machine whose actions may be selected by a person, a program, or autonomous software.

## The Big Idea
A useful control loop measures the world, compares that measurement with a desired state, acts, and measures again.

## See It in Your Head
Imagine a small rover facing a wall and repeatedly checking its distance before choosing a short motion.

## Core Concept
The sensor produces a measurement, the controller transforms that measurement into a command, and the actuator changes the physical state.

## Math Without Fear
If the target is 50 cm and the rover measures 70 cm, the signed error is 20 cm.

## Worked Robotics Example
With a response factor of 0.4, a 20 cm error requests an 8 cm correction.

## Python Lab
```python
def read_distance(true_distance_cm, sensor_bias_cm):
    return true_distance_cm + sensor_bias_cm

def choose_command(measured_distance_cm, target_distance_cm,
                   response_factor_per_cycle, max_move_cm_per_cycle):
    error_cm = measured_distance_cm - target_distance_cm
    move_cm = response_factor_per_cycle * error_cm
    return max(-max_move_cm_per_cycle,
               min(max_move_cm_per_cycle, move_cm))

def apply_command(true_distance_cm, move_cm):
    return true_distance_cm - move_cm

true_distance_cm = 80.0
commands_cm = []
distances_cm = []

for _ in range(6):
    measured_distance_cm = read_distance(
        true_distance_cm, 0.0
    )
    move_cm = choose_command(
        measured_distance_cm,
        50.0,
        0.4,
        8.0
    )
    true_distance_cm = apply_command(true_distance_cm, move_cm)
    commands_cm.append(move_cm)
    distances_cm.append(true_distance_cm)

assert len(distances_cm) == 6
```

## Mini Simulation or Game
Predict whether the rover will move toward or away from the wall when the measured distance is larger than the target.

```python
def read_distance_again(true_distance_cm, sensor_bias_cm):
    return true_distance_cm + sensor_bias_cm

def choose_command_again(measured_distance_cm, target_distance_cm,
                         response_factor_per_cycle, max_move_cm_per_cycle):
    error_cm = measured_distance_cm - target_distance_cm
    move_cm = response_factor_per_cycle * error_cm
    return max(-max_move_cm_per_cycle,
               min(max_move_cm_per_cycle, move_cm))

true_distance_cm = 80.0
commands_cm = []
distances_cm = []

for _ in range(6):
    measured_distance_cm = read_distance_again(
        true_distance_cm, 0.0
    )
    move_cm = choose_command_again(
        measured_distance_cm,
        50.0,
        0.4,
        8.0
    )
    true_distance_cm -= move_cm
    commands_cm.append(move_cm)
    distances_cm.append(true_distance_cm)

assert distances_cm[-1] < 80.0
```

## What Should Happen?
The rover should reduce its distance while the measured distance remains above the target.

## Common Mistakes
Do not confuse the measured distance with the signed error or assume a motor command is literally a distance.

## Try It Yourself
Change the response factor from 0.4 to 0.2 and predict the trajectory before running the code.

## Quick Quiz
Question 1: What information comes from the sensor?
Question 2: Why can the command saturate?

## Answers
Answer 1: The measured distance.
Answer 2: Because the actuator model limits movement per cycle.

## Real Robot Connection
A real rover would have timing delays, motor dynamics, wheel slip, and sensor noise that this simple model intentionally omits.

## Vocabulary
Sensor: a device that measures something about the robot or environment.
Controller: logic that converts measurements and goals into actions.
Actuator: hardware that produces physical action.

## Further Learning
Compare this ideal loop with a supervised low-speed rover experiment and inspect how noise changes the measurement.

## Next Class
Next we will build the first robot brain in Python and make decision logic explicit.
"""


def _long_enough_lesson(text):
    # The production static checker has a 1,600-word minimum. Extend only with
    # unique prose so this regression test isolates the duplicate detector.
    additions = []
    index = 0
    while len(text.split()) < 1700:
        index += 1
        additions.append(
            "Teaching note {0}: sensing and action remain distinct stages, "
            "and this numbered sentence exists only to keep the regression "
            "fixture above the premium lesson length threshold.".format(index)
        )
    return text + "\n\n" + "\n\n".join(additions)


def test_similar_code_loops_do_not_count_as_repeated_teaching_paragraphs():
    report = deterministic_quality_checks(_long_enough_lesson(BASE_LESSON))

    assert not any(
        error.startswith('Repeated teaching paragraph(s) detected:')
        for error in report['errors']
    )


def test_genuine_repeated_prose_is_still_blocked():
    repeated = (
        "This teaching paragraph deliberately repeats exactly so the quality "
        "gate can still catch duplicated explanatory prose for students. "
        "It is long enough to qualify for the deterministic repetition check."
    )

    lesson = _long_enough_lesson(
        BASE_LESSON
        + "\n\n"
        + repeated
        + "\n\n"
        + repeated
    )
    report = deterministic_quality_checks(lesson)

    assert any(
        error.startswith('Repeated teaching paragraph(s) detected:')
        for error in report['errors']
    )
