import json
import re

from .config import settings
from .validator import REQUIRED_HEADINGS, extract_python, validate_lesson


PLACEHOLDER_PATTERNS = [
    r'\bTODO\b', r'\bTBD\b', r'lorem ipsum', r'example\.com',
    r'insert (image|video|link|diagram) here', r'as an ai language model',
]

QUALITY_DIMENSIONS = [
    'technical_accuracy',
    'pedagogy',
    'clarity',
    'depth',
    'examples',
    'interactivity',
    'code_alignment',
    'visual_teaching_plan',
    'originality',
    'consistency',
    'accessibility',
]


PREMIUM_REVIEW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "overall_score": {"type": "integer", "minimum": 0, "maximum": 100},
        "dimensions": {
            "type": "object",
            "additionalProperties": False,
            "properties": dict((name, {"type": "integer", "minimum": 0, "maximum": 100}) for name in QUALITY_DIMENSIONS),
            "required": QUALITY_DIMENSIONS,
        },
        "blocking_issues": {"type": "array", "items": {"type": "string"}},
        "improvement_notes": {"type": "array", "items": {"type": "string"}},
        "media_would_help": {"type": "boolean"},
        "media_style": {"type": "string", "enum": ["none", "photo", "video", "mixed"]},
        "media_query": {"type": "string"},
        "image_query": {"type": "string"},
        "youtube_query": {"type": "string"},
        "media_insert_after_heading": {"type": "string"},
        "media_reason": {"type": "string"},
        "linkedin": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "title": {"type": "string"},
                "description": {"type": "string"},
                "commentary": {"type": "string"},
                "thumbnail_alt_text": {"type": "string"},
            },
            "required": ["title", "description", "commentary", "thumbnail_alt_text"],
        },
    },
    "required": [
        "overall_score", "dimensions", "blocking_issues", "improvement_notes",
        "media_would_help", "media_style", "media_query", "image_query",
        "youtube_query", "media_insert_after_heading", "media_reason", "linkedin"
    ],
}


def _body_without_code(markdown):
    return re.sub(r'```.*?```', ' ', markdown, flags=re.S)


def _word_count(markdown):
    body = _body_without_code(markdown)
    words = re.findall(r"\b[\w'-]+\b", body, flags=re.UNICODE)
    return len(words)


def _heading_positions(markdown):
    positions = []
    for heading in REQUIRED_HEADINGS:
        positions.append(markdown.find(heading))
    return positions


def deterministic_quality_checks(markdown):
    errors = []
    warnings = []
    words = _word_count(markdown)
    code_blocks = extract_python(markdown)

    structure_errors = validate_lesson(markdown)
    errors.extend(structure_errors)

    if words < 1600:
        errors.append('Premium lesson is too short: {0} words; target at least 1,600.'.format(words))
    elif words > 3800:
        warnings.append('Lesson is long at {0} words; consider tightening for reading flow.'.format(words))

    if not code_blocks:
        errors.append('Premium lesson must contain at least one runnable Python lab.')

    positions = _heading_positions(markdown)
    present_positions = [value for value in positions if value >= 0]
    if present_positions and present_positions != sorted(present_positions):
        errors.append('Required lesson sections are not in the expected teaching order.')

    lower = markdown.lower()
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, lower, flags=re.I):
            errors.append('Placeholder or low-quality drafting language detected: {0}'.format(pattern))

    if markdown.count('## Quick Quiz') != 1 or markdown.count('## Answers') != 1:
        errors.append('Quiz and answer sections must each appear exactly once.')

    if len(re.findall(r'\b(question|quiz)\b', lower)) < 2:
        warnings.append('Quiz language appears sparse; make assessment prompts explicit.')

    if not re.search(r'\d', markdown):
        errors.append('Lesson needs at least one concrete numerical example.')

    # Detect suspiciously repetitive consecutive paragraphs.
    paragraphs = [re.sub(r'\s+', ' ', item.strip()).lower() for item in re.split(r'\n\s*\n', markdown)]
    paragraphs = [item for item in paragraphs if len(item) > 80 and not item.startswith('```')]
    seen = set()
    duplicates = 0
    for paragraph in paragraphs:
        key = paragraph[:180]
        if key in seen:
            duplicates += 1
        seen.add(key)
    if duplicates:
        errors.append('Repeated teaching paragraph(s) detected: {0}.'.format(duplicates))

    return {
        'passed': len(errors) == 0,
        'word_count': words,
        'code_blocks': len(code_blocks),
        'errors': errors,
        'warnings': warnings,
    }


def _balanced_json_object(text):
    start = text.find('{')
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        ch = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif ch == '\\':
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return None


def extract_json_object(text):
    if not text:
        raise ValueError('Empty quality-review response.')
    cleaned = text.strip()
    if cleaned.startswith('```'):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.I)
        cleaned = re.sub(r'\s*```$', '', cleaned)

    candidates = [cleaned]
    balanced = _balanced_json_object(cleaned)
    if balanced and balanced != cleaned:
        candidates.append(balanced)

    last_error = None
    for candidate in candidates:
        try:
            return json.loads(candidate)
        except ValueError as exc:
            last_error = exc
        # Conservative repair for a common model error: trailing commas before ] or }.
        repaired = re.sub(r',\s*([}\]])', r'\1', candidate)
        if repaired != candidate:
            try:
                return json.loads(repaired)
            except ValueError as exc:
                last_error = exc

    if last_error is not None:
        raise ValueError('Malformed quality-review JSON: {0}'.format(last_error))
    raise ValueError('No JSON object found in quality-review response.')


def failed_ai_review(reason):
    return normalize_ai_review({
        'overall_score': 0,
        'dimensions': dict((name, 0) for name in QUALITY_DIMENSIONS),
        'blocking_issues': [reason],
        'improvement_notes': [
            'The editorial review could not be parsed reliably. Regenerate the review before publication.'
        ],
        'media_would_help': False,
        'media_style': 'none',
        'media_query': '',
        'image_query': '',
        'youtube_query': '',
        'media_insert_after_heading': '## Real Robot Connection',
        'media_reason': '',
        'linkedin': {
            'title': '', 'description': '', 'commentary': '', 'thumbnail_alt_text': ''
        },
    })


def normalize_ai_review(review):
    dimensions = review.get('dimensions') or {}
    normalized = {}
    for key in QUALITY_DIMENSIONS:
        try:
            value = int(dimensions.get(key, 0))
        except (TypeError, ValueError):
            value = 0
        normalized[key] = max(0, min(100, value))

    try:
        overall = int(review.get('overall_score', 0))
    except (TypeError, ValueError):
        overall = 0
    overall = max(0, min(100, overall))

    blocking = review.get('blocking_issues') or []
    improvements = review.get('improvement_notes') or []
    if not isinstance(blocking, list):
        blocking = [str(blocking)]
    if not isinstance(improvements, list):
        improvements = [str(improvements)]

    linkedin = review.get('linkedin') or {}
    normalized_review = {
        'overall_score': overall,
        'dimensions': normalized,
        'blocking_issues': [str(x) for x in blocking if str(x).strip()],
        'improvement_notes': [str(x) for x in improvements if str(x).strip()],
        'linkedin': {
            'title': str(linkedin.get('title') or '').strip(),
            'description': str(linkedin.get('description') or '').strip(),
            'commentary': str(linkedin.get('commentary') or '').strip(),
            'thumbnail_alt_text': str(linkedin.get('thumbnail_alt_text') or '').strip(),
        },
        'media_query': str(review.get('media_query') or '').strip(),
        'image_query': str(review.get('image_query') or review.get('media_query') or '').strip(),
        'youtube_query': str(review.get('youtube_query') or '').strip(),
        'media_style': str(review.get('media_style') or 'none').strip().lower(),
        'media_insert_after_heading': str(review.get('media_insert_after_heading') or '## Real Robot Connection').strip(),
        'media_reason': str(review.get('media_reason') or '').strip(),
        'media_would_help': bool(review.get('media_would_help', False)),
    }
    return normalized_review


def premium_review_passes(static_report, ai_review):
    if not static_report.get('passed'):
        return False
    if not ai_review:
        return not settings.require_ai_quality_review
    if ai_review.get('blocking_issues'):
        return False
    if ai_review.get('overall_score', 0) < settings.premium_quality_min_score:
        return False
    dimensions = ai_review.get('dimensions') or {}
    for value in dimensions.values():
        if int(value) < settings.premium_quality_min_dimension:
            return False
    return True



def weak_dimensions(ai_review):
    result = []
    dimensions = (ai_review or {}).get('dimensions') or {}
    for name, score in dimensions.items():
        try:
            numeric = int(score)
        except (TypeError, ValueError):
            numeric = 0
        if numeric < settings.premium_quality_min_dimension:
            result.append({'name': name, 'score': numeric, 'required': settings.premium_quality_min_dimension})
    result.sort(key=lambda item: item['score'])
    return result

def combined_quality_report(static_report, ai_review, rounds_used=0):
    passed = premium_review_passes(static_report, ai_review)
    return {
        'passed': passed,
        'thresholds': {
            'overall': settings.premium_quality_min_score,
            'dimension': settings.premium_quality_min_dimension,
        },
        'rewrite_rounds_used': rounds_used,
        'static': static_report,
        'ai': ai_review,
    }


def quality_failure_summary(report):
    reasons = []
    static = report.get('static') or {}
    reasons.extend(static.get('errors') or [])
    ai = report.get('ai') or {}
    reasons.extend(ai.get('blocking_issues') or [])
    if ai:
        if ai.get('overall_score', 0) < settings.premium_quality_min_score:
            reasons.append('AI quality score {0} is below required {1}.'.format(
                ai.get('overall_score', 0), settings.premium_quality_min_score))
        for name, score in (ai.get('dimensions') or {}).items():
            if int(score) < settings.premium_quality_min_dimension:
                reasons.append('{0} score {1} is below required {2}.'.format(
                    name, score, settings.premium_quality_min_dimension))
    return reasons
