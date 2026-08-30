"""Deterministic protection for generated inline teaching visuals.

AI editorial/technical rewrites return the complete lesson Markdown. Even when
the prompt says to preserve media, a rewrite can occasionally omit an existing
`inline_XX.png` reference. This module treats those generated-media blocks as
protected publication artifacts and restores any one that disappears during a
rewrite.

The publication gate remains fail-closed: if a protected visual cannot be
restored to its original lesson section, the existing deterministic visual
validator will still block publication.
"""

import functools
import re

from .runtime import monitor


_INLINE_IMAGE_RE = re.compile(
    r'^!\[[^\]]*\]\((inline_\d+\.png)\)\s*$'
)


def _heading_key(value):
    value = str(value or '').strip()
    value = re.sub(r'^#{1,6}\s*', '', value)
    value = re.sub(r'[^a-z0-9]+', ' ', value.lower())
    return ' '.join(value.split())


def _extract_protected_visuals(markdown):
    """Return generated inline image blocks and their nearest H2 section."""
    lines = str(markdown or '').splitlines()
    protected = []
    current_heading = None
    index = 0

    while index < len(lines):
        line = lines[index]

        if line.startswith('## '):
            current_heading = line.strip()

        match = _INLINE_IMAGE_RE.match(line.strip())
        if not match:
            index += 1
            continue

        filename = match.group(1)
        block = [line]
        cursor = index + 1

        # Preserve the normal blank line between image and educational caption.
        if cursor < len(lines) and not lines[cursor].strip():
            block.append(lines[cursor])
            cursor += 1

        if (
            cursor < len(lines)
            and lines[cursor].strip().startswith('**Figure:**')
        ):
            block.append(lines[cursor])
            cursor += 1

        protected.append({
            'filename': filename,
            'heading': current_heading,
            'block': '\n'.join(block).strip(),
        })

        index = cursor

    return protected


def _find_heading(markdown, original_heading):
    if not original_heading:
        return None

    lines = str(markdown or '').splitlines()
    original_heading = original_heading.strip()

    # Strongest match: the required Professor OS section heading is unchanged.
    for line in lines:
        if line.strip() == original_heading:
            return line.strip()

    # Small wording/punctuation drift should not destroy a generated visual.
    wanted = _heading_key(original_heading)
    if not wanted:
        return None

    candidates = []
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith('## '):
            continue
        key = _heading_key(stripped)
        if key == wanted:
            return stripped
        if key and (key in wanted or wanted in key):
            candidates.append(stripped)

    if len(candidates) == 1:
        return candidates[0]

    return None


def _remove_orphan_caption(markdown, block):
    """Avoid duplicating a caption if an AI rewrite deleted only the image."""
    block_lines = str(block or '').splitlines()
    caption = None
    for line in block_lines:
        if line.strip().startswith('**Figure:**'):
            caption = line.strip()
            break

    if not caption:
        return markdown

    lines = str(markdown or '').splitlines()
    removed = False
    kept = []
    for line in lines:
        if not removed and line.strip() == caption:
            removed = True
            continue
        kept.append(line)

    return '\n'.join(kept)


def _insert_after_heading(markdown, heading, block):
    pattern = re.compile(
        r'(?m)^' + re.escape(str(heading).strip()) + r'\s*$'
    )
    match = pattern.search(markdown)
    if not match:
        return markdown, False

    insert_at = match.end()
    repaired = (
        markdown[:insert_at]
        + '\n\n'
        + str(block).strip()
        + '\n'
        + markdown[insert_at:]
    )
    return repaired, True


def restore_generated_visuals(before_markdown, after_markdown):
    """Restore generated inline image blocks lost by a full-lesson rewrite.

    Returns:
        (repaired_markdown, restored_filenames)
    """
    before = str(before_markdown or '')
    repaired = str(after_markdown or '')
    restored = []

    for item in _extract_protected_visuals(before):
        filename = item['filename']

        if ']({0})'.format(filename) in repaired:
            continue

        heading = _find_heading(
            repaired,
            item.get('heading')
        )
        if not heading:
            # Deliberately do not guess a random placement. The existing
            # validate_inserted_visuals() check will fail closed.
            continue

        repaired = _remove_orphan_caption(
            repaired,
            item.get('block')
        )

        repaired, inserted = _insert_after_heading(
            repaired,
            heading,
            item.get('block')
        )

        if inserted and ']({0})'.format(filename) in repaired:
            restored.append(filename)

    return repaired, restored


def preserve_generated_visuals(before_markdown, after_markdown):
    repaired, _ = restore_generated_visuals(
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
            '_professor_os_visual_integrity_wrapped',
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

        repaired, restored = restore_generated_visuals(
            lesson_markdown,
            result
        )

        if restored:
            monitor.event(
                'warning',
                'Editorial rewrite removed generated teaching visual(s); '
                'Professor OS restored them deterministically: {0}'.format(
                    ', '.join(restored)
                )
            )

        return repaired

    protected_rewrite._professor_os_visual_integrity_wrapped = True
    setattr(
        LessonWriter,
        method_name,
        protected_rewrite
    )


def install_runtime_hook():
    """Protect media across every method that rewrites a complete lesson."""
    for method_name in (
        'repair_code',
        'repair_technical_quality',
        'polish_post_media_quality',
        'polish_premium_quality',
        'converge_premium_quality',
        'surgical_premium_quality',
    ):
        _wrap_full_lesson_rewrite(method_name)
