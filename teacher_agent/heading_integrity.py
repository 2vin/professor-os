"""Deterministic protection for required Professor OS lesson sections.

Full-lesson AI editorial rewrites can occasionally omit or rename a required H2
heading even when the source lesson was structurally valid. That should never
burn more repair rounds or block publication if the original valid section is
available.

This module wraps every LessonWriter method that rewrites a complete lesson.
After each rewrite it:

1. normalizes harmless heading punctuation/wording drift back to the exact
   required Professor OS heading;
2. restores any required section that disappeared, using the previous valid
   version of that section;
3. preserves required-heading order.

The normal validator still runs afterwards and remains fail-closed.
"""

import functools
import re

from .runtime import monitor
from .validator import REQUIRED_HEADINGS


_H2_RE = re.compile(r'(?m)^##[ \t]+(.+?)[ \t]*$')


def _heading_key(value):
    value = str(value or '').strip()
    value = re.sub(r'^#{1,6}\s*', '', value)
    value = value.replace('&', ' and ')
    value = value.replace('/', ' ')
    value = re.sub(r'\bor\b', ' ', value, flags=re.I)
    value = re.sub(r'[^a-z0-9]+', ' ', value.lower())
    return ' '.join(value.split())


def _h2_spans(markdown):
    """Return H2 sections as dictionaries with full text spans."""
    text = str(markdown or '')
    matches = list(_H2_RE.finditer(text))
    sections = []

    for index, match in enumerate(matches):
        start = match.start()
        end = (
            matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        )
        heading = '## ' + match.group(1).strip()
        sections.append({
            'heading': heading,
            'key': _heading_key(heading),
            'start': start,
            'end': end,
            'text': text[start:end].rstrip(),
        })

    return sections


def _exact_heading_present(markdown, heading):
    pattern = re.compile(
        r'(?m)^' + re.escape(str(heading).strip()) + r'[ \t]*$'
    )
    return bool(pattern.search(str(markdown or '')))


def _normalize_heading_variant(markdown, required_heading):
    """Rename one unambiguous equivalent H2 to the exact required heading."""
    text = str(markdown or '')
    wanted = _heading_key(required_heading)
    candidates = [
        section for section in _h2_spans(text)
        if section['key'] == wanted
        and section['heading'] != required_heading
    ]

    if len(candidates) != 1:
        return text, False

    section = candidates[0]
    old_heading = section['heading']
    pattern = re.compile(
        r'(?m)^' + re.escape(old_heading) + r'[ \t]*$'
    )
    repaired, count = pattern.subn(required_heading, text, count=1)
    return repaired, count == 1


def _section_from_reference(reference_markdown, required_heading):
    for section in _h2_spans(reference_markdown):
        if section['heading'] == required_heading:
            return section['text'].strip()
    return None


def _insert_before_heading(markdown, heading, section_text):
    text = str(markdown or '')
    pattern = re.compile(
        r'(?m)^' + re.escape(str(heading).strip()) + r'[ \t]*$'
    )
    match = pattern.search(text)
    if not match:
        return text, False

    insert_at = match.start()
    prefix = text[:insert_at].rstrip()
    suffix = text[insert_at:].lstrip()

    repaired = (
        prefix
        + '\n\n'
        + str(section_text).strip()
        + '\n\n'
        + suffix
    )
    return repaired, True


def _insert_after_heading_section(markdown, heading, section_text):
    """Insert after an existing required section, before the following H2."""
    text = str(markdown or '')
    sections = _h2_spans(text)

    for section in sections:
        if section['heading'] != heading:
            continue

        insert_at = section['end']
        prefix = text[:insert_at].rstrip()
        suffix = text[insert_at:].lstrip()

        repaired = (
            prefix
            + '\n\n'
            + str(section_text).strip()
            + ('\n\n' + suffix if suffix else '\n')
        )
        return repaired, True

    return text, False


def _append_before_visual_plan_or_end(markdown, section_text):
    text = str(markdown or '')
    visual_heading = '## Visual Generation Plan'

    if _exact_heading_present(text, visual_heading):
        return _insert_before_heading(
            text,
            visual_heading,
            section_text
        )

    return (
        text.rstrip()
        + '\n\n'
        + str(section_text).strip()
        + '\n'
    ), True


def restore_required_sections(before_markdown, after_markdown):
    """Restore required H2 structure lost by a complete-lesson rewrite.

    Returns:
        (repaired_markdown, restored_headings, normalized_headings)
    """
    before = str(before_markdown or '')
    repaired = str(after_markdown or '')
    restored = []
    normalized = []

    # First correct harmless heading drift so we do not duplicate a section
    # simply because punctuation or "or" changed.
    for heading in REQUIRED_HEADINGS:
        if _exact_heading_present(repaired, heading):
            continue

        repaired, changed = _normalize_heading_variant(
            repaired,
            heading
        )
        if changed:
            normalized.append(heading)

    # Then restore truly missing sections from the previous valid lesson.
    for index, heading in enumerate(REQUIRED_HEADINGS):
        if _exact_heading_present(repaired, heading):
            continue

        reference_section = _section_from_reference(
            before,
            heading
        )
        if not reference_section:
            # The previous version did not contain it either. Do not fabricate
            # educational content; let the existing validator fail closed.
            continue

        inserted = False

        # Preferred location: immediately before the next required heading
        # that still exists.
        for later_heading in REQUIRED_HEADINGS[index + 1:]:
            if _exact_heading_present(repaired, later_heading):
                repaired, inserted = _insert_before_heading(
                    repaired,
                    later_heading,
                    reference_section
                )
                if inserted:
                    break

        # Otherwise place it after the nearest earlier required section.
        if not inserted:
            for earlier_heading in reversed(REQUIRED_HEADINGS[:index]):
                if _exact_heading_present(repaired, earlier_heading):
                    repaired, inserted = _insert_after_heading_section(
                        repaired,
                        earlier_heading,
                        reference_section
                    )
                    if inserted:
                        break

        # Final safe placement: before machine metadata or at document end.
        if not inserted:
            repaired, inserted = _append_before_visual_plan_or_end(
                repaired,
                reference_section
            )

        if inserted and _exact_heading_present(repaired, heading):
            restored.append(heading)

    return repaired, restored, normalized


def preserve_required_sections(before_markdown, after_markdown):
    repaired, _, _ = restore_required_sections(
        before_markdown,
        after_markdown
    )
    return repaired


def _wrap_full_lesson_rewrite(method_name):
    from .lesson_writer import LessonWriter

    original = getattr(LessonWriter, method_name, None)
    if original is None:
        return

    if getattr(
            original,
            '_professor_os_heading_integrity_wrapped',
            False):
        return

    @functools.wraps(original)
    def protected_rewrite(self, lesson_markdown, *args, **kwargs):
        result = original(
            self,
            lesson_markdown,
            *args,
            **kwargs
        )

        repaired, restored, normalized = restore_required_sections(
            lesson_markdown,
            result
        )

        if normalized:
            monitor.event(
                'warning',
                'Editorial rewrite changed required heading text; '
                'Professor OS normalized it deterministically: {0}'.format(
                    ', '.join(normalized)
                )
            )

        if restored:
            monitor.event(
                'warning',
                'Editorial rewrite removed required lesson section(s); '
                'Professor OS restored them deterministically: {0}'.format(
                    ', '.join(restored)
                )
            )

        return repaired

    protected_rewrite._professor_os_heading_integrity_wrapped = True
    setattr(
        LessonWriter,
        method_name,
        protected_rewrite
    )


def install_runtime_hook():
    """Protect required H2 structure across every complete-lesson rewrite."""
    for method_name in (
        'repair_code',
        'repair_technical_quality',
        'polish_post_media_quality',
        'polish_premium_quality',
        'converge_premium_quality',
        'surgical_premium_quality',
    ):
        _wrap_full_lesson_rewrite(method_name)
