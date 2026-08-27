from teacher_agent.prompts import (
    lesson_prompt,
    surgical_quality_repair_prompt,
)


def test_class1_prompt_avoids_ambiguous_robot_boundary_case():
    prompt = lesson_prompt(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
            'concepts': 'robot, autonomy, machine, environment',
        },
        None,
        'Sense -> Think -> Act'
    )

    assert 'no single universally accepted binary boundary' in prompt
    assert 'do NOT use an automatic door as a scored robot/not-robot example' in prompt
    assert 'thermostat = feedback control but not normally a robot' in prompt
    assert 'teleoperated rover = robot without task-level autonomy' in prompt
    assert 'threshold/hysteresis feedback still counts' in prompt


def test_surgical_prompt_contains_foundation_repair_rules():
    prompt = surgical_quality_repair_prompt(
        '# Class 1: What Is a Robot?',
        '{"overall_score":84,"blocking_issues":["automatic door ambiguity"]}',
        '{"passed":true,"word_count":2780}',
        None
    )

    assert 'MINIMUM coherent edits' in prompt
    assert 'Do NOT use an automatic door as a scored yes/no robot-classification item' in prompt
    assert 'thermostat' in prompt
    assert 'Feedback can use thresholds or hysteresis' in prompt
    assert 'Keep feedback control and task-level autonomy as independent axes' in prompt
