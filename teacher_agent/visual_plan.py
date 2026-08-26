import json
import re


VISUAL_PLAN_RE = re.compile(
    r'## Visual Generation Plan\s*'
    r'```json\s*(\{.*?\})\s*```',
    re.S | re.I
)


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

    if not isinstance(hero, dict):
        raise RuntimeError(
            'Visual Generation Plan is missing hero_image.'
        )

    inline = plan.get('inline_visuals')

    if not isinstance(inline, list):
        raise RuntimeError(
            'Visual Generation Plan inline_visuals must be an array.'
        )

    if len(inline) < 2:
        raise RuntimeError(
            'Visual Generation Plan requires at least 2 inline visuals.'
        )

    return plan


def remove_visual_plan(markdown):
    """Remove machine instructions from the student-facing article."""
    return VISUAL_PLAN_RE.sub('', markdown).rstrip() + '\n'
