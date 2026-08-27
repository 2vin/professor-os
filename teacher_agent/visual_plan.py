import json
import re


VISUAL_PLAN_RE = re.compile(
    r'## Visual Generation Plan\s*'
    r'```json\s*(\{.*?\})\s*```',
    re.S | re.I
)


EXTERNAL_PROVENANCE_TERMS = (
    'independently sourced',
    'licensed photograph',
    'licensed photo',
    'wikimedia',
    'stock photo',
    'third-party',
    'third party',
    'external photograph',
    'external photo',
    'photographer attribution',
)


def _validate_generated_asset(item, label):
    if not isinstance(item, dict):
        raise RuntimeError('{0} must be a JSON object.'.format(label))

    source = str(item.get('source') or '').strip().lower()
    if not source:
        # Backward-compatible normalization: the Visual Generation Plan is a Gemini-only
        # plan. Missing provenance may be normalized, but explicit external provenance is rejected.
        item['source'] = 'gemini'
        source = 'gemini'
    if source != 'gemini':
        raise RuntimeError(
            '{0} must declare source="gemini". External media is handled by the separate media-curation stage.'.format(
                label
            )
        )

    text = ' '.join([
        str(item.get('visual_type') or ''),
        str(item.get('prompt') or ''),
        str(item.get('caption') or ''),
        str(item.get('alt_text') or ''),
    ]).lower()

    for term in EXTERNAL_PROVENANCE_TERMS:
        if term in text:
            raise RuntimeError(
                '{0} incorrectly requests external/licensed provenance inside the Gemini visual plan: {1}'.format(
                    label,
                    term
                )
            )

    if not str(item.get('prompt') or '').strip():
        raise RuntimeError('{0} is missing prompt.'.format(label))
    if not str(item.get('caption') or '').strip():
        raise RuntimeError('{0} is missing caption.'.format(label))
    if not str(item.get('alt_text') or '').strip():
        raise RuntimeError('{0} is missing alt_text.'.format(label))


def extract_visual_plan(markdown):
    match = VISUAL_PLAN_RE.search(markdown)

    if not match:
        raise RuntimeError(
            'Lesson is missing the required Visual Generation Plan.'
        )

    try:
        plan = json.loads(match.group(1))
    except ValueError as exc:
        raise RuntimeError(
            'Visual Generation Plan is invalid JSON: {0}'.format(exc)
        )

    hero = plan.get('hero_image')
    _validate_generated_asset(hero, 'hero_image')

    if not hero.get('needed', True):
        raise RuntimeError('Visual Generation Plan hero_image.needed must be true.')

    inline = plan.get('inline_visuals')

    if not isinstance(inline, list):
        raise RuntimeError(
            'Visual Generation Plan inline_visuals must be an array.'
        )

    if len(inline) < 2:
        raise RuntimeError(
            'Visual Generation Plan requires at least 2 inline visuals.'
        )

    if len(inline) > 4:
        raise RuntimeError(
            'Visual Generation Plan allows at most 4 inline visuals for a focused lesson.'
        )

    for index, item in enumerate(inline, 1):
        _validate_generated_asset(
            item,
            'inline_visuals[{0}]'.format(index - 1)
        )
        if not str(item.get('section_heading') or '').startswith('## '):
            raise RuntimeError(
                'Inline visual {0} must target an exact ## section heading.'.format(index)
            )

    return plan


def remove_visual_plan(markdown):
    """Remove machine instructions from the student-facing article."""
    return VISUAL_PLAN_RE.sub('', markdown).rstrip() + '\n'
