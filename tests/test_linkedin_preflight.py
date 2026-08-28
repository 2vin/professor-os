import teacher_agent.diagram as diagram_module

from teacher_agent.diagram import make_linkedin_cover
from teacher_agent.linkedin_preflight import (
    LINKEDIN_PUBLIC_URL,
    build_linkedin_package,
    preflight_linkedin_package,
)


def _disable_live_gemini(monkeypatch):
    monkeypatch.setattr(
        diagram_module.settings,
        'use_gemini_images',
        False
    )
    monkeypatch.setattr(
        diagram_module.settings,
        'gemini_api_key',
        ''
    )


def _review():
    return {
        'linkedin': {
            'title': 'What Is a Robot?',
            'description': (
                'A beginner-friendly robotics lesson about robot identity.'
            ),
            'commentary': (
                'What actually makes a machine a robot?\n\n'
                'Professor OS Class 1 builds the foundation through '
                'RoboRover, examples, and a tested Python activity.\n\n'
                'Students compare teleoperation, programmed behavior, '
                'feedback, and autonomy while keeping the physical robot '
                'conceptually consistent. The goal is not memorizing a '
                'definition; it is learning how robotics engineers reason '
                'about systems and boundaries.\n\n'
                'Try the lesson, make a prediction before running the lab, '
                'and then explain what changed.\n\n'
                '#Robotics #Python #Engineering'
            ),
            'thumbnail_alt_text': (
                'Professor OS Class 1 robotics thumbnail'
            ),
        }
    }


def test_package_replaces_render_url_with_connect_vin():
    package = build_linkedin_package(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
        },
        _review(),
        (
            'https://professor-os.onrender.com/'
            'lessons/001-what-is-a-robot/'
        )
    )

    assert package['source'] == LINKEDIN_PUBLIC_URL
    assert package['post_type'] == 'image'
    assert LINKEDIN_PUBLIC_URL in package['commentary']
    assert 'onrender.com' not in package['commentary'].lower()


def test_preflight_accepts_connect_vin_image_post(
        tmp_path,
        monkeypatch):
    _disable_live_gemini(monkeypatch)

    hero = tmp_path / 'hero.png'
    make_linkedin_cover(
        1,
        'What Is a Robot?',
        'robot, autonomy, sensors',
        hero
    )

    package = build_linkedin_package(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
        },
        _review(),
        'https://professor-os.onrender.com/lessons/001/'
    )

    report = preflight_linkedin_package(
        package,
        hero
    )

    assert report['passed'], report['errors']
    assert report['post_type'] == 'image'
    assert report['public_source'] == LINKEDIN_PUBLIC_URL
    assert report['thumbnail_width'] == 1200
    assert report['thumbnail_height'] == 675


def test_preflight_rejects_render_url(
        tmp_path,
        monkeypatch):
    _disable_live_gemini(monkeypatch)

    hero = tmp_path / 'hero.png'
    make_linkedin_cover(
        1,
        'What Is a Robot?',
        'robot',
        hero
    )

    package = build_linkedin_package(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
        },
        _review(),
        'https://professor-os.onrender.com/lessons/001/'
    )
    package['source'] = (
        'https://professor-os.onrender.com/lessons/001/'
    )

    report = preflight_linkedin_package(
        package,
        hero
    )

    assert not report['passed']
    assert any(
        'connect.vin' in error
        for error in report['errors']
    )
