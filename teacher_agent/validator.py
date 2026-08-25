import ast
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REQUIRED_HEADINGS = [
    '## Where We Are in the Robotics Journey',
    '## Today We Will Learn',
    '## 2-Minute Recap',
    '## The Big Idea',
    '## See It in Your Head',
    '## Core Concept',
    '## Math Without Fear',
    '## Worked Robotics Example',
    '## Python Lab',
    '## Mini Simulation or Game',
    '## What Should Happen?',
    '## Common Mistakes',
    '## Try It Yourself',
    '## Quick Quiz',
    '## Answers',
    '## Real Robot Connection',
    '## Vocabulary',
    '## Further Learning',
    '## Next Class',
]

BLOCK_RE = re.compile(r'```python\s+(.*?)```', re.S | re.I)


def extract_python(markdown):
    return [x.strip() for x in BLOCK_RE.findall(markdown)]


def validate_structure(markdown):
    return [h for h in REQUIRED_HEADINGS if h not in markdown]


def validate_python_blocks(markdown, timeout=8):
    errors = []
    blocks = extract_python(markdown)
    if not blocks:
        return ['No Python code block found.']

    for index, code in enumerate(blocks, 1):
        try:
            ast.parse(code)
        except SyntaxError as exc:
            errors.append('Block {0}: syntax error: {1}'.format(index, exc))
            continue

        # Hardware/large external frameworks are syntax-checked only in this lightweight validator.
        hardware_imports = ('RPi', 'gpiozero', 'serial', 'rclpy', 'cv2', 'pybullet')
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
                    errors.append('Block {0}: runtime error:\n{1}'.format(
                        index, proc.stderr[-1500:]))
            except subprocess.TimeoutExpired:
                errors.append('Block {0}: timed out after {1}s.'.format(index, timeout))
            except Exception as exc:
                errors.append('Block {0}: validator could not execute code: {1}'.format(index, exc))
    return errors


def validate_lesson(markdown):
    errors = []
    missing = validate_structure(markdown)
    if missing:
        errors.append('Missing headings: ' + ', '.join(missing))
    errors.extend(validate_python_blocks(markdown))
    return errors
