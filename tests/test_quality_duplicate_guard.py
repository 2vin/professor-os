from teacher_agent.quality import deterministic_quality_checks


BASE_LESSON = """# Class 2: Sense → Think → Act

## Where We Are in the Robotics Journey
We are building a clear mental model of sensing, decisions, and physical action.

## Today We Will Learn
We will connect sensing, control decisions, and movement through a small feedback example.

## The Big Idea
A useful control loop measures the world, chooses an action, acts, and measures again.

## Python Lab
```python
def choose_command(measured_distance_cm, target_distance_cm):
    error_cm = measured_distance_cm - target_distance_cm
    move_cm = 0.4 * error_cm
    return max(-8.0, min(8.0, move_cm))

for measured_distance_cm in (80.0, 70.0, 60.0):
    command_cm = choose_command(measured_distance_cm, 50.0)
    assert command_cm <= 8.0
```

## Mini Simulation or Game
The second fenced block intentionally contains a very similar control loop. The regression test verifies that repeated-looking Python does not count as duplicated teaching prose.

```python
def choose_command_again(measured_distance_cm, target_distance_cm):
    error_cm = measured_distance_cm - target_distance_cm
    move_cm = 0.4 * error_cm
    return max(-8.0, min(8.0, move_cm))

for measured_distance_cm in (80.0, 70.0, 60.0):
    command_cm = choose_command_again(measured_distance_cm, 50.0)
    assert command_cm <= 8.0
```

## What Should Happen?
The rover should request progressively smaller moves as it approaches the target distance.

## Common Mistakes
Do not confuse measured distance with error, and do not treat a motor command as a perfect physical displacement.

## Quick Quiz
What quantity tells the controller how far the current measurement is from the target?

## Answers
The signed error is the measured value minus the target value.

## Real Robot Connection
A real rover also has timing delays, wheel slip, motor dynamics, and sensor noise.

## Vocabulary
Sensor: a device that measures something about the robot or environment.
Controller: logic that maps measurements and goals to actions.
Actuator: hardware that produces physical action.

## Next Class
Next we will make robot decision logic explicit in Python.
"""


def _long_enough_lesson(text):
    """Pad the fixture to the production word-count range in bounded time.

    The previous helper used ``while len(text.split()) < 1700`` but never
    changed ``text`` inside the loop. That was an infinite loop which grew an
    in-memory list until GitHub Actions killed pytest with exit code 137.
    """
    current_words = len(text.split())
    needed = max(0, 1700 - current_words)
    if not needed:
        return text

    padding = ' '.join(
        'fixtureword{0}'.format(index)
        for index in range(needed)
    )
    return text + '\n\n' + padding


def test_similar_code_loops_do_not_count_as_repeated_teaching_paragraphs():
    report = deterministic_quality_checks(_long_enough_lesson(BASE_LESSON))

    assert not any(
        error.startswith('Repeated teaching paragraph(s) detected:')
        for error in report['errors']
    )


def test_genuine_repeated_prose_is_still_blocked():
    repeated = (
        'This teaching paragraph deliberately repeats exactly so the quality '
        'gate can still catch duplicated explanatory prose for students. '
        'It is intentionally long enough to qualify for repetition detection.'
    )

    lesson = _long_enough_lesson(
        BASE_LESSON
        + '\n\n'
        + repeated
        + '\n\n'
        + repeated
    )
    report = deterministic_quality_checks(lesson)

    assert any(
        error.startswith('Repeated teaching paragraph(s) detected:')
        for error in report['errors']
    )
