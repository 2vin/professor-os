from pathlib import Path

from teacher_agent.media_inserter import (
    inject_inline_visuals,
    validate_inserted_visuals,
)
from teacher_agent.prompts import lesson_prompt
from teacher_agent.visual_plan import extract_visual_plan, remove_visual_plan


def _asset(filename, heading, caption, alt_text):
    return {
        'filename': filename,
        'path': filename,
        'section_heading': heading,
        'caption': caption,
        'alt_text': alt_text,
        'visual_type': 'diagram',
    }


def test_lesson_prompt_contains_parseable_visual_plan():
    prompt = lesson_prompt(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
            'concepts': 'sense, think, act',
        },
        None,
        'Robot Parts'
    )

    assert '## Visual Generation Plan' in prompt
    assert '```json' in prompt
    assert '\n```\n' in prompt
    assert '"needed": true' in prompt
    assert prompt.count('\"section_heading\"') >= 2


def test_remove_visual_plan_keeps_student_lesson_only():
    markdown = (
        '# Class 1: Intro\n\n'
        '## Next Class\nNext lesson.\n\n'
        '## Visual Generation Plan\n'
        '```json\n'
        '{"hero_image":{"needed":true},"inline_visuals":[{},{}]}\n'
        '```\n'
    )

    cleaned = remove_visual_plan(markdown)
    assert '## Visual Generation Plan' not in cleaned
    assert 'hero_image' not in cleaned
    assert '## Next Class' in cleaned


def test_inline_visuals_are_inserted_and_validated(tmp_path):
    markdown = (
        '# Class 1: Intro\n\n'
        '## The Big Idea\n\nExplain the concept.\n\n'
        '## Worked Robotics Example\n\nRun the example.\n'
    )

    assets = [
        _asset(
            'inline_01.png',
            '## The Big Idea',
            'Trace the robot information flow.',
            'Sense think act robotics diagram.'
        ),
        _asset(
            'inline_02.png',
            '## Worked Robotics Example',
            'Notice how distance changes the action.',
            'Robot measuring an obstacle.'
        ),
    ]

    for asset in assets:
        path = tmp_path / asset['filename']
        path.write_bytes(b'x' * 12000)
        asset['path'] = str(path)

    inserted = inject_inline_visuals(markdown, assets)

    assert '](inline_01.png)' in inserted
    assert '](inline_02.png)' in inserted
    assert '**Figure:** Trace the robot information flow.' in inserted

    errors = validate_inserted_visuals(inserted, assets, tmp_path)
    assert errors == []


def test_inline_visual_validation_fails_when_article_reference_disappears(tmp_path):
    asset = _asset(
        'inline_01.png',
        '## The Big Idea',
        'Trace the robot information flow.',
        'Sense think act robotics diagram.'
    )
    path = tmp_path / 'inline_01.png'
    path.write_bytes(b'x' * 12000)
    asset['path'] = str(path)

    errors = validate_inserted_visuals('# Class 1: Intro', [asset, asset], tmp_path)
    assert any('not inserted' in error for error in errors)
