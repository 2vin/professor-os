from teacher_agent.lesson_writer import LessonWriter
from teacher_agent.visual_integrity import (
    restore_generated_visuals,
)


def _lesson_with_visuals():
    return (
        '# Class 6: Electricity for Roboticists\n\n'
        '## The Big Idea\n\n'
        '![Circuit diagram](inline_01.png)\n\n'
        '**Figure:** Voltage, current, and resistance.\n\n'
        'The circuit is a complete loop.\n\n'
        '## See It in Your Head\n\n'
        '![Meter placement](inline_02.png)\n\n'
        '**Figure:** Voltmeter across; ammeter in series.\n\n'
        'A voltmeter compares two points.\n\n'
        '## Worked Robotics Example\n\n'
        '![Rover resistor example](inline_03.png)\n\n'
        '**Figure:** A low-voltage resistor branch.\n'
    )


def test_missing_generated_visual_is_restored_to_original_section():
    before = _lesson_with_visuals()

    after = before.replace(
        '![Meter placement](inline_02.png)\n\n',
        ''
    )

    repaired, restored = restore_generated_visuals(
        before,
        after
    )

    assert restored == ['inline_02.png']
    assert '](inline_02.png)' in repaired
    assert repaired.count('](inline_02.png)') == 1

    heading_at = repaired.index('## See It in Your Head')
    image_at = repaired.index('](inline_02.png)')
    next_heading_at = repaired.index(
        '## Worked Robotics Example'
    )
    assert heading_at < image_at < next_heading_at


def test_orphan_caption_is_not_duplicated_when_image_is_restored():
    before = _lesson_with_visuals()

    after = before.replace(
        '![Meter placement](inline_02.png)\n\n',
        ''
    )

    repaired, restored = restore_generated_visuals(
        before,
        after
    )

    assert restored == ['inline_02.png']
    assert repaired.count(
        '**Figure:** Voltmeter across; ammeter in series.'
    ) == 1


def test_existing_visuals_are_not_duplicated():
    before = _lesson_with_visuals()

    repaired, restored = restore_generated_visuals(
        before,
        before
    )

    assert restored == []
    assert repaired.count('](inline_01.png)') == 1
    assert repaired.count('](inline_02.png)') == 1
    assert repaired.count('](inline_03.png)') == 1


def test_small_heading_drift_can_still_restore_visual():
    before = _lesson_with_visuals()

    after = before.replace(
        '## See It in Your Head',
        '## See It in Your Head — Circuit Measurement'
    ).replace(
        '![Meter placement](inline_02.png)\n\n',
        ''
    )

    repaired, restored = restore_generated_visuals(
        before,
        after
    )

    assert restored == ['inline_02.png']
    assert '](inline_02.png)' in repaired


def test_all_full_lesson_rewrite_methods_are_protected():
    for name in (
        'repair_code',
        'repair_technical_quality',
        'polish_post_media_quality',
        'polish_premium_quality',
        'converge_premium_quality',
        'surgical_premium_quality',
    ):
        method = getattr(LessonWriter, name)
        assert getattr(
            method,
            '_professor_os_visual_integrity_wrapped',
            False
        ) is True
