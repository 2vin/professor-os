from teacher_agent.heading_integrity import (
    restore_required_sections,
)
from teacher_agent.lesson_writer import LessonWriter
from teacher_agent.validator import REQUIRED_HEADINGS


def _minimal_required_lesson():
    parts = ['# Class 17: PI and PID Intuition']
    for heading in REQUIRED_HEADINGS:
        parts.append(
            '{0}\n\nContent for {1}.'.format(
                heading,
                heading[3:]
            )
        )
    parts.append(
        '## Visual Generation Plan\n\n'
        '```json\n{"hero": {"source": "gemini"}}\n```'
    )
    return '\n\n'.join(parts)


def test_restores_missing_middle_required_section_in_order():
    before = _minimal_required_lesson()

    removed = (
        '## Mini Simulation or Game\n\n'
        'Content for Mini Simulation or Game.'
    )
    after = before.replace(removed + '\n\n', '')

    repaired, restored, normalized = restore_required_sections(
        before,
        after
    )

    assert '## Mini Simulation or Game' in repaired
    assert 'Content for Mini Simulation or Game.' in repaired
    assert restored == ['## Mini Simulation or Game']
    assert normalized == []

    assert repaired.index('## Python Lab') < repaired.index(
        '## Mini Simulation or Game'
    )
    assert repaired.index('## Mini Simulation or Game') < repaired.index(
        '## What Should Happen?'
    )


def test_normalizes_equivalent_heading_without_duplicating_section():
    before = _minimal_required_lesson()
    after = before.replace(
        '## Mini Simulation or Game',
        '## Mini Simulation / Game',
        1
    )

    repaired, restored, normalized = restore_required_sections(
        before,
        after
    )

    assert repaired.count('## Mini Simulation or Game') == 1
    assert '## Mini Simulation / Game' not in repaired
    assert restored == []
    assert normalized == ['## Mini Simulation or Game']


def test_does_not_invent_section_missing_from_reference_too():
    before = _minimal_required_lesson().replace(
        '## Mini Simulation or Game\n\n'
        'Content for Mini Simulation or Game.\n\n',
        ''
    )
    after = before

    repaired, restored, normalized = restore_required_sections(
        before,
        after
    )

    assert '## Mini Simulation or Game' not in repaired
    assert restored == []
    assert normalized == []


def test_all_complete_lesson_rewrite_methods_are_guarded():
    for method_name in (
        'repair_code',
        'repair_technical_quality',
        'polish_post_media_quality',
        'polish_premium_quality',
        'converge_premium_quality',
        'surgical_premium_quality',
    ):
        method = getattr(LessonWriter, method_name)
        assert getattr(
            method,
            '_professor_os_heading_integrity_wrapped',
            False
        ) is True
