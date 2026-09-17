"""Deterministic headline formatting for Professor OS LinkedIn posts.

LinkedIn does not support Markdown bold in ordinary post commentary. Professor OS
therefore uses Unicode Mathematical Sans-Serif Bold characters for the visible
first line of every automatic class post.

Example:
    𝗖𝗹𝗮𝘀𝘀 𝟮𝟱 · 𝗖𝗼𝗺𝗽𝘂𝘁𝗲𝗿 𝗩𝗶𝘀𝗶𝗼𝗻: 𝗣𝗶𝘅𝗲𝗹𝘀 𝗮𝘀 𝗡𝘂𝗺𝗯𝗲𝗿𝘀
"""

import re
import unicodedata


_BOLD_UPPER = 0x1D5D4
_BOLD_LOWER = 0x1D5EE
_BOLD_DIGIT = 0x1D7EC


def unicode_bold_sans(value):
    """Convert ASCII letters/digits to Mathematical Sans-Serif Bold."""
    output = []
    for char in str(value or ''):
        if 'A' <= char <= 'Z':
            output.append(
                chr(_BOLD_UPPER + ord(char) - ord('A'))
            )
        elif 'a' <= char <= 'z':
            output.append(
                chr(_BOLD_LOWER + ord(char) - ord('a'))
            )
        elif '0' <= char <= '9':
            output.append(
                chr(_BOLD_DIGIT + ord(char) - ord('0'))
            )
        else:
            # Keep punctuation, arrows, mathematical symbols and spaces exactly
            # as authored in curriculum.json.
            output.append(char)
    return ''.join(output)


def format_linkedin_headline(lesson):
    """Return the canonical visible headline for one Professor OS class."""
    class_no = int(lesson.get('class_no') or 0)
    title = str(lesson.get('title') or '').strip()
    plain = 'Class {0} · {1}'.format(class_no, title)
    return unicode_bold_sans(plain)


def _strip_existing_class_heading(commentary, class_no):
    """Avoid duplicate AI/fallback class headings before adding our canonical one."""
    text = str(commentary or '').strip()
    if not text:
        return ''

    lines = text.splitlines()
    if not lines:
        return text

    first = unicodedata.normalize(
        'NFKC',
        lines[0]
    ).strip()

    pattern = (
        r'^(?:Professor\s+OS\s+)?'
        r'(?:Robotics\s+)?'
        r'Class\s+0*{0}'
        r'(?:\s*[:·\-–—]\s*|\s*$)'
    ).format(int(class_no or 0))

    if re.match(pattern, first, flags=re.I):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]

    return '\n'.join(lines).strip()


def _apply_headline(package, lesson):
    headline = format_linkedin_headline(lesson)
    body = _strip_existing_class_heading(
        package.get('commentary', ''),
        lesson.get('class_no')
    )

    package['title'] = headline
    package['commentary'] = (
        headline + '\n\n' + body
        if body
        else headline
    )
    package['headline'] = headline
    package['headline_style'] = 'unicode_math_sans_serif_bold'
    return package


def install_runtime_hook():
    """Patch the current LinkedIn package builder before pipeline imports it."""
    from . import linkedin_preflight

    current = linkedin_preflight.build_linkedin_package

    if getattr(
            current,
            '_professor_os_headline_wrapped',
            False):
        return

    def build_with_canonical_headline(
            lesson,
            ai_review,
            lesson_url):
        package = current(
            lesson,
            ai_review,
            lesson_url
        )
        return _apply_headline(
            package,
            lesson
        )

    build_with_canonical_headline._professor_os_headline_wrapped = True
    linkedin_preflight.build_linkedin_package = (
        build_with_canonical_headline
    )
