import re
from pathlib import Path


def _clean_text(value):
    value = str(value or '').strip()
    value = re.sub(r'\s+', ' ', value)
    return value


def _insert_after_heading(markdown, heading, block):
    pattern = re.compile(
        r'(?m)^' + re.escape(heading.strip()) + r'\s*$'
    )

    match = pattern.search(markdown)

    if not match:
        raise RuntimeError(
            'Cannot insert teaching visual because heading was not found: {0}'.format(
                heading
            )
        )

    insert_at = match.end()

    return (
        markdown[:insert_at]
        + '\n\n'
        + block.strip()
        + '\n'
        + markdown[insert_at:]
    )


def inject_inline_visuals(markdown, inline_assets):
    """
    Insert Gemini-generated inline teaching visuals directly under
    the lesson headings specified by the visual plan.

    Hero image is intentionally NOT inserted here because
    article_renderer.py already displays hero.png in the article header.
    """

    assets_by_heading = {}

    for asset in inline_assets or []:
        heading = _clean_text(asset.get('section_heading'))
        filename = _clean_text(asset.get('filename'))

        if not heading:
            raise RuntimeError(
                'Gemini inline visual is missing section_heading.'
            )

        if not filename:
            path = asset.get('path')
            if path:
                filename = Path(path).name

        if not filename:
            raise RuntimeError(
                'Gemini inline visual is missing filename.'
            )

        # Avoid accidental duplicate insertion.
        if ']({0})'.format(filename) in markdown:
            continue

        assets_by_heading.setdefault(heading, []).append(asset)

    for heading, assets in assets_by_heading.items():
        blocks = []

        for asset in assets:
            filename = asset.get('filename') or Path(asset['path']).name
            alt_text = _clean_text(
                asset.get('alt_text') or 'Professor OS robotics teaching visual'
            )
            caption = _clean_text(asset.get('caption'))

            if not caption:
                caption = 'Professor OS teaching visual for this concept.'

            block = (
                '![{alt}]({filename})\n\n'
                '**Figure:** {caption}'
            ).format(
                alt=alt_text,
                filename=filename,
                caption=caption,
            )

            blocks.append(block)

        markdown = _insert_after_heading(
            markdown,
            heading,
            '\n\n'.join(blocks)
        )

    return markdown


def validate_inserted_visuals(markdown, inline_assets, output_dir):
    """
    Deterministic fail-closed check.
    Every planned Gemini visual must exist and must appear in Markdown.
    """

    errors = []
    output_dir = Path(output_dir)

    inline_assets = inline_assets or []

    if len(inline_assets) < 2:
        errors.append(
            'Premium lesson requires at least 2 Gemini inline visuals.'
        )

    for index, asset in enumerate(inline_assets, 1):
        filename = asset.get('filename')

        if not filename and asset.get('path'):
            filename = Path(asset['path']).name

        if not filename:
            errors.append(
                'Inline visual {0} has no filename.'.format(index)
            )
            continue

        path = output_dir / filename

        if not path.exists():
            errors.append(
                'Generated inline visual does not exist: {0}'.format(filename)
            )
            continue

        if path.stat().st_size < 10000:
            errors.append(
                'Generated inline visual appears invalid: {0}'.format(filename)
            )

        if ']({0})'.format(filename) not in markdown:
            errors.append(
                'Generated inline visual is not inserted into lesson: {0}'.format(
                    filename
                )
            )

        alt_text = _clean_text(asset.get('alt_text'))
        if not alt_text:
            errors.append(
                'Inline visual has no alt text: {0}'.format(filename)
            )

        caption = _clean_text(asset.get('caption'))
        if not caption:
            errors.append(
                'Inline visual has no educational caption: {0}'.format(filename)
            )

    return errors
