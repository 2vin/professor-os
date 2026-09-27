from teacher_agent import validator
from teacher_agent.lesson_writer import LessonWriter
from teacher_agent.prompts import SYSTEM_PROMPT


def test_python_fence_guard_is_installed():
    assert hasattr(validator, 'validation_error_report')
    assert 'PYTHON FENCE CLASSIFICATION RULE:' in SYSTEM_PROMPT


def test_validation_report_numbers_referenced_block():
    markdown = (
        "```python\n"
        "print('ok')\n"
        "```\n\n"
        "```python\n"
        "Estimated pose: x=1.0\n"
        "```\n"
    )
    errors = validator.validate_python_blocks(markdown)
    report = validator.validation_error_report(markdown, errors)

    assert 'Block 2' in report
    assert '02:' not in report
    assert '01: Estimated pose: x=1.0' in report


def test_repair_method_mentions_text_fence_and_preservation():
    writer = LessonWriter.__new__(LessonWriter)
    captured = {}

    def fake_call(instructions, user_input, text_format=None):
        captured['instructions'] = instructions
        captured['user_input'] = user_input
        return '# repaired'

    writer._call_openai = fake_call
    result = writer.repair_code(
        "```python\nEstimated pose: x=1\n```",
        'Block 1: syntax error at line 1: invalid syntax'
    )

    assert result == '# repaired'
    assert '```text' in captured['instructions']
    assert 'NEVER hide a genuine Python teaching example' in captured['instructions']
    assert 'Current fenced python Block 1 source:' in captured['user_input']
