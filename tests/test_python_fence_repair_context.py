from teacher_agent.prompts import SYSTEM_PROMPT
from teacher_agent.validator import (
    validate_python_blocks,
    validation_error_report,
)
from teacher_agent.lesson_writer import LessonWriter


def test_syntax_error_reports_exact_bad_source_line():
    markdown = (
        "## Python Lab\n\n"
        "```python\nprint('ok')\n```\n\n"
        "```python\nEstimated pose: x=1.0, y=2.0\n```\n"
    )

    errors = validate_python_blocks(markdown)

    assert errors
    assert 'Block 2' in errors[0]
    assert 'syntax error at line 1' in errors[0]
    assert 'Estimated pose:' in errors[0]

    report = validation_error_report(markdown, errors)
    assert 'Current fenced python Block 2 source:' in report
    assert '01: Estimated pose: x=1.0, y=2.0' in report


def test_generation_prompt_reserves_python_fences_for_real_python():
    assert 'ONLY for runnable Python 3.7 code' in SYSTEM_PROMPT
    assert 'expected console output' in SYSTEM_PROMPT
    assert '```text' in SYSTEM_PROMPT


def test_repair_prompt_can_retag_output_but_not_hide_real_code():
    writer = LessonWriter.__new__(LessonWriter)
    captured = {}

    def fake_call(instructions, user_input, text_format=None):
        captured['instructions'] = instructions
        captured['user_input'] = user_input
        return '# repaired lesson'

    writer._call_openai = fake_call

    result = writer.repair_code(
        '# lesson\n\n```python\nEstimated pose: x=1\n```',
        (
            'Block 1: syntax error at line 1: invalid syntax\n\n'
            'Current fenced python Block 1 source:\n'
            '01: Estimated pose: x=1'
        )
    )

    assert result == '# repaired lesson'
    assert 'FENCE CLASSIFICATION RULE' in captured['instructions']
    assert 'expected console output' in captured['instructions']
    assert 'NEVER hide a genuine Python teaching example' in captured['instructions']
    assert 'numbered source excerpt' in captured['instructions']
