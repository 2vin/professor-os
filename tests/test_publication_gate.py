import json
from pathlib import Path

from teacher_agent.publication_gate import final_publication_gate


def _png(path, width=1200, height=675):
    import struct
    # Minimal header sufficient for Professor OS dimension inspection plus size padding.
    data = (
        b'\x89PNG\r\n\x1a\n' +
        b'\x00\x00\x00\x0dIHDR' +
        struct.pack('>II', width, height) +
        b'0' * 12000
    )
    Path(path).write_bytes(data)


def _visual_plan():
    return {
        'hero_image': {
            'needed': True,
            'section': 'top',
            'visual_type': 'premium robotics hero illustration',
            'prompt': 'A realistic classroom robot being examined by students.',
            'caption': 'Observe how sensing, computation, and actuation form one system.',
            'alt_text': 'Students examining a wheeled classroom robot.',
        },
        'inline_visuals': [
            {
                'section_heading': '## The Big Idea',
                'visual_type': 'diagram',
                'prompt': 'A clear sense-think-act robotics diagram.',
                'caption': 'Trace information from sensor to decision to actuator.',
                'alt_text': 'Sense think act flow diagram for a robot.',
            },
            {
                'section_heading': '## Worked Robotics Example',
                'visual_type': 'illustration',
                'prompt': 'A realistic robot approaching an obstacle with distance sensing.',
                'caption': 'Notice how measured distance changes the robot action.',
                'alt_text': 'Robot measuring distance to an obstacle.',
            },
        ],
    }


def _complete_package(tmp_path):
    lesson = {'class_no': 1, 'title': 'What Is a Robot?'}

    readme = (
        '# Class 1: What Is a Robot?\n\n'
        '## The Big Idea\n\n'
        '![Sense think act flow diagram for a robot.](inline_01.png)\n\n'
        '**Figure:** Trace information from sensor to decision to actuator.\n\n'
        '## Worked Robotics Example\n\n'
        '![Robot measuring distance to an obstacle.](inline_02.png)\n\n'
        '**Figure:** Notice how measured distance changes the robot action.\n'
    )
    (tmp_path / 'README.md').write_text(readme, encoding='utf-8')

    article = (
        '<html><head><meta name="viewport" content="width=device-width">'
        '<style>body{font-family:Arial}@media(max-width:700px){}</style></head>'
        '<body><article>Professor OS Built by Connect.Vin What Is a Robot? '
        '<img src="hero.png">'
        '<img src="inline_01.png" alt="Sense think act flow diagram for a robot.">'
        '<img src="inline_02.png" alt="Robot measuring distance to an obstacle.">'
        '</article></body></html>' + ('x' * 5000)
    )
    (tmp_path / 'index.html').write_text(article, encoding='utf-8')

    preview = (
        '<html><head><meta name="viewport" content="width=device-width">'
        '<style>body{font-family:Arial}@media(max-width:700px){}</style></head>'
        '<body>What Is a Robot? <img src="hero.png"></body></html>' +
        ('x' * 5000)
    )
    (tmp_path / 'linkedin_preview.html').write_text(preview, encoding='utf-8')

    _png(tmp_path / 'hero.png', 1200, 675)
    _png(tmp_path / 'diagram.png', 1200, 675)
    _png(tmp_path / 'inline_01.png', 1024, 576)
    _png(tmp_path / 'inline_02.png', 1024, 576)

    (tmp_path / 'VISUAL_PLAN.json').write_text(
        json.dumps(_visual_plan()),
        encoding='utf-8'
    )
    (tmp_path / 'QUALITY_REPORT.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'LINKEDIN_PREFLIGHT.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'MEDIA_CREDITS.md').write_text('# Media Credits', encoding='utf-8')

    code = tmp_path / 'lab.py'
    code.write_text('print(1)', encoding='utf-8')
    return lesson, code


def test_publication_gate_passes_complete_premium_visual_package(tmp_path):
    lesson, code = _complete_package(tmp_path)

    report = final_publication_gate(
        lesson,
        tmp_path,
        {'passed': True},
        {'passed': True, 'title': lesson['title']},
        {'used': False, 'items': []},
        [code]
    )

    assert report['passed'] is True
    assert report['checks']['visual_assets'] is True
    assert report['checks']['inline_visual_count'] is True
    assert report['visuals']['planned_inline_count'] == 2
    assert (tmp_path / 'PUBLICATION_GATE.json').exists()


def test_publication_gate_blocks_missing_artifacts(tmp_path):
    report = final_publication_gate(
        {'class_no': 1, 'title': 'Intro'},
        tmp_path,
        {'passed': True},
        {'passed': True},
        {'used': False, 'items': []},
        []
    )

    assert report['passed'] is False
    assert report['errors']


def test_publication_gate_blocks_missing_inline_visual(tmp_path):
    lesson, code = _complete_package(tmp_path)
    (tmp_path / 'inline_02.png').unlink()

    report = final_publication_gate(
        lesson,
        tmp_path,
        {'passed': True},
        {'passed': True},
        {'used': False, 'items': []},
        [code]
    )

    assert report['passed'] is False
    assert any('inline_02.png' in error for error in report['errors'])


def test_publication_gate_blocks_machine_visual_plan_leak(tmp_path):
    lesson, code = _complete_package(tmp_path)
    readme_path = tmp_path / 'README.md'
    readme_path.write_text(
        readme_path.read_text(encoding='utf-8') + '\n## Visual Generation Plan\n',
        encoding='utf-8'
    )

    report = final_publication_gate(
        lesson,
        tmp_path,
        {'passed': True},
        {'passed': True},
        {'used': False, 'items': []},
        [code]
    )

    assert report['passed'] is False
    assert any('Visual Generation Plan leaked' in error for error in report['errors'])
