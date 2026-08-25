import re
import struct
import unicodedata
from pathlib import Path
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .config import settings


def normalize_professional_text(value):
    text = unicodedata.normalize('NFKC', str(value or ''))
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def build_linkedin_package(lesson, ai_review, lesson_url):
    linkedin = (ai_review or {}).get('linkedin') or {}
    title = normalize_professional_text(linkedin.get('title'))
    description = normalize_professional_text(linkedin.get('description'))
    commentary = normalize_professional_text(linkedin.get('commentary'))
    alt_text = normalize_professional_text(linkedin.get('thumbnail_alt_text'))

    if not title:
        title = 'Robotics Class {0}: {1}'.format(lesson['class_no'], lesson['title'])
    if not description:
        description = 'A practical Professor OS lesson with intuition, math, tested Python, a simulation, quiz, and engineering context.'
    if not commentary:
        commentary = (
            'Robotics Class {0}: {1}\n\n'
            'Today we build the idea from intuition to engineering reality, then test it with Python.\n\n'
            '• Understand the core mental model\n'
            '• Work through a numerical example\n'
            '• Run the validated lab and change one assumption\n'
            '• Check your understanding with the quiz\n\n'
            'Try the lab, predict what should happen first, then compare with the result.\n\n'
            '#Robotics #Python #STEM #RobotLearning'
        ).format(lesson['class_no'], lesson['title'])
    if not alt_text:
        alt_text = 'Professor OS cover for Robotics Class {0}: {1}'.format(
            lesson['class_no'], lesson['title'])

    return {
        'title': title,
        'description': description,
        'commentary': commentary,
        'thumbnail_alt_text': alt_text,
        'source': lesson_url,
    }


def _png_dimensions(path):
    path = Path(path)
    with path.open('rb') as handle:
        signature = handle.read(24)
    if len(signature) < 24 or signature[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Thumbnail is not a valid PNG file.')
    width, height = struct.unpack('>II', signature[16:24])
    return width, height


def preflight_linkedin_package(package, hero_path):
    errors = []
    warnings = []
    title = normalize_professional_text(package.get('title'))
    description = normalize_professional_text(package.get('description'))
    commentary = normalize_professional_text(package.get('commentary'))
    alt_text = normalize_professional_text(package.get('thumbnail_alt_text'))
    source = str(package.get('source') or '').strip()

    if not title or len(title) >= 400:
        errors.append('LinkedIn article title must be present and under 400 characters.')
    if not description or len(description) >= 4086:
        errors.append('LinkedIn article description must be present and under 4,086 characters.')
    if not alt_text or len(alt_text) >= 4086:
        errors.append('LinkedIn thumbnail alt text must be present and under 4,086 characters.')
    if len(alt_text) > 120:
        warnings.append('Thumbnail alt text is over the recommended 120 characters.')

    parsed = urlparse(source)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc:
        errors.append('LinkedIn article source must be a valid public http(s) URL.')

    if len(commentary) < 350:
        errors.append('LinkedIn commentary is too thin for a premium lesson post.')
    if len(commentary) > settings.linkedin_commentary_soft_limit:
        errors.append('LinkedIn commentary exceeds the configured premium readability limit of {0} characters.'.format(
            settings.linkedin_commentary_soft_limit))
    if '```' in commentary or re.search(r'^#{1,6}\s', commentary, flags=re.M):
        errors.append('LinkedIn commentary must not contain Markdown code fences or Markdown headings.')
    if re.search(r'\b(TODO|TBD|lorem ipsum)\b', commentary, flags=re.I):
        errors.append('LinkedIn commentary contains placeholder text.')

    hashtags = re.findall(r'(?<!\w)#[A-Za-z0-9_]+', commentary)
    if len(hashtags) > 4:
        errors.append('LinkedIn commentary should use no more than 4 focused hashtags.')
    if not hashtags:
        warnings.append('No hashtags were included; 2-4 focused hashtags usually improve topic signaling.')

    long_lines = [line for line in commentary.splitlines() if len(line) > 180]
    if long_lines:
        warnings.append('Some LinkedIn commentary lines are visually dense; shorter paragraphs would scan better.')

    try:
        width, height = _png_dimensions(hero_path)
        pixels = width * height
        ratio = float(width) / float(height)
        if pixels >= 36152320:
            errors.append('Thumbnail exceeds LinkedIn image pixel-count limit.')
        if width < 1200 or height < 630:
            errors.append('Premium LinkedIn thumbnail must be at least 1200x630 pixels.')
        if abs(ratio - (16.0 / 9.0)) > 0.12:
            warnings.append('Thumbnail aspect ratio differs noticeably from 16:9.')
    except Exception as exc:
        errors.append('Thumbnail validation failed: {0}'.format(exc))
        width, height = 0, 0

    return {
        'passed': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'title_length': len(title),
        'description_length': len(description),
        'commentary_length': len(commentary),
        'hashtags': hashtags,
        'thumbnail_width': width,
        'thumbnail_height': height,
    }
