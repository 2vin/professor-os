"""Fix false repeated-paragraph failures caused by fenced Python code.

Professor OS' deterministic quality checker is intended to detect duplicated
TEACHING PROSE. The original implementation split the raw Markdown on blank
lines, so similar indented fragments inside two separate fenced Python blocks
could be mistaken for duplicate teaching paragraphs.

This compatibility guard preserves the existing quality checker, then
recomputes only the repeated-prose verdict using Markdown with fenced code
removed first.
"""

import re


_ERROR_PREFIX = 'Repeated teaching paragraph(s) detected:'


def _prose_duplicate_count(markdown, body_without_code):
    prose = body_without_code(markdown)
    paragraphs = [
        re.sub(r'\s+', ' ', item.strip()).lower()
        for item in re.split(r'\n\s*\n', prose)
    ]
    paragraphs = [
        item for item in paragraphs
        if len(item) > 80
    ]

    seen = set()
    duplicates = 0
    for paragraph in paragraphs:
        key = paragraph[:180]
        if key in seen:
            duplicates += 1
        seen.add(key)
    return duplicates


def install_runtime_hook():
    from . import quality

    current = quality.deterministic_quality_checks
    if getattr(current, '_professor_os_prose_duplicate_fixed', False):
        return

    original = current

    def deterministic_quality_checks_without_code_false_positive(markdown):
        report = original(markdown)

        errors = [
            error
            for error in (report.get('errors') or [])
            if not str(error).startswith(_ERROR_PREFIX)
        ]

        duplicate_count = _prose_duplicate_count(
            markdown,
            quality._body_without_code
        )
        if duplicate_count:
            errors.append(
                'Repeated teaching paragraph(s) detected: {0}.'.format(
                    duplicate_count
                )
            )

        report['errors'] = errors
        report['passed'] = len(errors) == 0
        return report

    deterministic_quality_checks_without_code_false_positive._professor_os_prose_duplicate_fixed = True
    quality.deterministic_quality_checks = (
        deterministic_quality_checks_without_code_false_positive
    )
