import unicodedata

from teacher_agent.linkedin_headline import (
    format_linkedin_headline,
    unicode_bold_sans,
)
from teacher_agent.linkedin_preflight import build_linkedin_package


def _review(commentary):
    return {
        'linkedin': {
            'title': 'AI should not control this title',
            'description': (
                'A premium Professor OS robotics class.'
            ),
            'commentary': commentary,
            'thumbnail_alt_text': (
                'Professor OS class thumbnail'
            ),
        }
    }


def test_class_25_headline_matches_required_format_exactly():
    lesson = {
        'class_no': 25,
        'title': 'Computer Vision: Pixels as Numbers',
    }

    headline = format_linkedin_headline(lesson)

    assert headline == (
        '𝗖𝗹𝗮𝘀𝘀 𝟮𝟱 · '
        '𝗖𝗼𝗺𝗽𝘂𝘁𝗲𝗿 𝗩𝗶𝘀𝗶𝗼𝗻: '
        '𝗣𝗶𝘅𝗲𝗹𝘀 𝗮𝘀 𝗡𝘂𝗺𝗯𝗲𝗿𝘀'
    )


def test_every_package_uses_headline_as_first_visible_line():
    lesson = {
        'class_no': 25,
        'title': 'Computer Vision: Pixels as Numbers',
    }

    package = build_linkedin_package(
        lesson,
        _review(
            'Pixels become useful when we treat them as numerical data.\n\n'
            'This lesson turns an image into something a robot can compute '
            'with.\n\n'
            '#Robotics #ComputerVision'
        ),
        'https://professor-os.onrender.com/lessons/025/'
    )

    expected = format_linkedin_headline(lesson)

    assert package['title'] == expected
    assert package['headline'] == expected
    assert package['commentary'].splitlines()[0] == expected


def test_existing_plain_class_heading_is_not_duplicated():
    lesson = {
        'class_no': 3,
        'title': 'Your First Robot Brain in Python',
    }

    package = build_linkedin_package(
        lesson,
        _review(
            'Robotics Class 3: Your First Robot Brain in Python\n\n'
            'Today we turn decisions into executable logic.\n\n'
            '#Robotics #Python'
        ),
        'https://professor-os.onrender.com/lessons/003/'
    )

    plain = 'Class 3 · Your First Robot Brain in Python'

    assert unicodedata.normalize(
        'NFKC',
        package['commentary'].splitlines()[0]
    ) == plain

    # Only the canonical styled heading should remain at the top.
    assert 'Robotics Class 3:' not in package['commentary']


def test_arrow_and_punctuation_are_preserved():
    lesson = {
        'class_no': 2,
        'title': 'Sense → Think → Act',
    }

    headline = format_linkedin_headline(lesson)

    assert '→' in headline
    assert '·' in headline
    assert unicodedata.normalize(
        'NFKC',
        headline
    ) == 'Class 2 · Sense → Think → Act'


def test_unicode_bold_helper_keeps_symbols_unchanged():
    assert unicode_bold_sans('A1: x-y → z') == '𝗔𝟭: 𝘅-𝘆 → 𝘇'
