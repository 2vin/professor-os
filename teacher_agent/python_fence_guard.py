"""Python-fence generation and repair guard for Professor OS.

This runtime hook fixes a failure mode where explanatory prose or expected
console output is accidentally emitted inside a ```python fence. The normal
validator then tries to execute that prose as Python.

The hook:
- strengthens the generation system prompt;
- makes syntax diagnostics include the exact offending source line;
- exposes validation_error_report() with numbered fenced-source context;
- upgrades LessonWriter.repair_code() so it can distinguish prose/output from
  genuine Python and repair the fence without deleting real teaching code.

It is installed before the visual/heading integrity guards, so those existing
guards still wrap and protect the corrected repair method.
"""

import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


_FENCE_RULES = r"""

PYTHON FENCE CLASSIFICATION RULE:
- Use fenced ```python blocks ONLY for runnable Python 3.7 code.
- Never put explanatory prose, pseudocode, a trace, a state summary, a formula,
  a table, or expected console output inside a ```python block.
- Put expected console output, logs, traces, and non-executable examples in
  fenced ```text blocks or ordinary Markdown prose.
- A line such as "Estimated pose: x=1.0, y=2.0" is not Python unless it is
  intentionally represented as a quoted string or produced by a print()
  statement.
- Every ```python block must parse as Python 3.7 and must remain independently
  executable under the Professor OS validator.
"""


def _line_excerpt(code, line_number):
    lines = str(code or '').splitlines()
    try:
        index = int(line_number or 0) - 1
    except (TypeError, ValueError):
        index = -1
    if 0 <= index < len(lines):
        return lines[index].rstrip()
    return ''


def _numbered_source(code):
    lines = str(code or '').splitlines()
    width = max(2, len(str(max(1, len(lines)))))
    return '\n'.join(
        ('{0:0' + str(width) + 'd}: {1}').format(index, line)
        for index, line in enumerate(lines, 1)
    )


def _validation_error_report(markdown, errors):
    """Return repair-friendly diagnostics with exact fenced Python sources."""
    from . import validator

    blocks = validator.extract_python(markdown)
    error_text = '\n'.join(str(item) for item in (errors or []))
    parts = [
        'VALIDATION ERRORS:',
        error_text or 'No validator message supplied.',
    ]

    referenced = []
    for match in re.finditer(r'\bBlock\s+(\d+)\b', error_text):
        try:
            number = int(match.group(1))
        except (TypeError, ValueError):
            continue
        if number not in referenced:
            referenced.append(number)

    # If an upstream caller did not name a block, include all blocks. That is
    # more useful than sending the repair model an opaque error string.
    if not referenced:
        referenced = list(range(1, len(blocks) + 1))

    for number in referenced:
        if 1 <= number <= len(blocks):
            parts.extend([
                '',
                'Current fenced python Block {0} source:'.format(number),
                _numbered_source(blocks[number - 1]),
            ])

    return '\n'.join(parts).rstrip()


def _enhanced_validate_python_blocks(markdown, timeout=8):
    """Validate fenced Python and report the exact bad line on syntax errors."""
    from . import validator

    errors = []
    blocks = validator.extract_python(markdown)
    if not blocks:
        return ['No Python code block found.']

    for index, code in enumerate(blocks, 1):
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            line_no = int(getattr(exc, 'lineno', 0) or 0)
            source_line = _line_excerpt(code, line_no)
            message = 'Block {0}: syntax error at line {1}: {2}'.format(
                index,
                line_no or '?',
                getattr(exc, 'msg', str(exc))
            )
            if source_line:
                message += '\nOffending source: ' + source_line
            errors.append(message)
            continue

        if validator._is_reference_only_expression(tree):
            continue

        hardware_imports = (
            'RPi',
            'gpiozero',
            'serial',
            'rclpy',
            'cv2',
            'pybullet',
        )
        if any(name in code for name in hardware_imports):
            continue

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'lesson_block_{0}.py'.format(index)
            path.write_text(code, encoding='utf-8')
            env = os.environ.copy()
            env['MPLBACKEND'] = 'Agg'

            try:
                proc = subprocess.run(
                    [sys.executable, str(path)],
                    cwd=directory,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    timeout=timeout,
                    env=env,
                )
                if proc.returncode != 0:
                    errors.append(
                        'Block {0}: runtime error:\n{1}'.format(
                            index,
                            proc.stderr[-1500:]
                        )
                    )
            except subprocess.TimeoutExpired:
                errors.append(
                    'Block {0}: timed out after {1}s.'.format(
                        index,
                        timeout
                    )
                )
            except Exception as exc:
                errors.append(
                    'Block {0}: validator could not execute code: {1}'.format(
                        index,
                        exc
                    )
                )

    return errors


def _install_prompt_rules():
    from . import prompts

    marker = 'PYTHON FENCE CLASSIFICATION RULE:'
    if marker not in prompts.SYSTEM_PROMPT:
        prompts.SYSTEM_PROMPT += _FENCE_RULES


def _install_validator_rules():
    from . import validator

    validator.validation_error_report = _validation_error_report
    validator.validate_python_blocks = _enhanced_validate_python_blocks


def _install_repair_rules():
    from .lesson_writer import LessonWriter
    from . import validator

    current = LessonWriter.repair_code
    if getattr(
            current,
            '_professor_os_python_fence_guard_wrapped',
            False):
        return

    def repair_code_with_fence_context(
            self,
            lesson_markdown,
            error_report):
        instructions = (
            'You are repairing executable Python examples inside a robotics '
            'teaching lesson. Return the COMPLETE corrected Markdown lesson '
            'only. Preserve all required headings, explanations, diagrams, '
            'media references, and teaching continuity. Change only what is '
            'necessary to correct validation errors.\n\n'

            'FENCE CLASSIFICATION RULE:\n'
            '- A fenced ```python block is ONLY for runnable Python 3.7 code.\n'
            '- Explanatory prose, pseudocode, traces, state summaries, formulas, '
            'and expected console output must NOT remain in a Python fence.\n'
            '- If such content was accidentally fenced as Python, preserve the '
            'teaching content but retag it as ```text or convert it to normal '
            'Markdown prose.\n'
            '- NEVER hide a genuine Python teaching example merely to make the '
            'validator pass. If a block is intended to be code, repair the code '
            'and keep it executable.\n'
            '- Use the numbered source excerpt in the validation report to '
            'identify exactly which fenced line failed.\n\n'

            'CRITICAL VALIDATION RULE: every fenced ```python code block is '
            'executed IN ISOLATION in a fresh Python process. Therefore EVERY '
            'Python code block must be independently executable. A block may '
            'NOT depend on variables, functions, classes, imports, constants, '
            'or setup defined in another code block.\n\n'

            'If a demonstration needs a function, variable, class, import, or '
            'other dependency, define or import it inside that same Python '
            'block.\n\n'

            'ASSERTION FAILURE RULE: if validation reports AssertionError, do '
            'not blindly preserve, delete, or invert the assertion. Re-evaluate '
            'the tested function using the exact input in the assertion and fix '
            'whichever side actually contradicts the lesson semantics.\n\n'

            'If the lesson contains a ## Visual Generation Plan section, '
            'preserve the ENTIRE heading and fenced ```json block exactly as '
            'machine-readable metadata. Preserve existing inline_XX.png and '
            'diagram.png references, captions, and surrounding context.\n\n'

            'All executable code must run on Python 3.7. Do not use syntax '
            'introduced after Python 3.7. Before returning the lesson, mentally '
            'execute every Python block independently.'
        )

        # Always rebuild the report from the actual current Markdown. The
        # pipeline historically passed only a short error string, which left
        # the repair model without the source line that caused the failure.
        report = validator.validation_error_report(
            lesson_markdown,
            [error_report]
        )

        user_input = (
            'LESSON:\n{0}\n\n'
            'VALIDATION REPORT WITH NUMBERED SOURCE EXCERPTS:\n{1}'
        ).format(
            lesson_markdown,
            report
        )

        return self._call_openai(
            instructions,
            user_input
        )

    repair_code_with_fence_context._professor_os_python_fence_guard_wrapped = True
    LessonWriter.repair_code = repair_code_with_fence_context


def install_runtime_hook():
    _install_prompt_rules()
    _install_validator_rules()
    _install_repair_rules()
