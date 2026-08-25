import json
import re
import struct
from pathlib import Path


PLACEHOLDER_RE = re.compile(r'\b(TODO|TBD)\b|lorem ipsum|example\.com|insert (image|video|link|diagram) here', re.I)


def _png_dimensions(path):
    path = Path(path)
    with path.open('rb') as handle:
        header = handle.read(24)
    if len(header) < 24 or header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not a valid PNG: {0}'.format(path))
    return struct.unpack('>II', header[16:24])


def _check_html(path, lesson_title, hero_filename):
    errors = []
    warnings = []
    path = Path(path)
    if not path.exists():
        return ['Rendered article is missing: {0}'.format(path)], warnings
    text = path.read_text(encoding='utf-8')
    lowered = text.lower()
    if '<meta name="viewport"' not in lowered:
        errors.append('Rendered article is missing a responsive viewport declaration.')
    if '@media' not in text:
        errors.append('Rendered article has no responsive media rule.')
    if 'font-family:' not in lowered:
        errors.append('Rendered article has no explicit typography system.')
    if str(lesson_title) not in text:
        errors.append('Rendered article does not contain the lesson title.')
    if hero_filename not in text:
        errors.append('Rendered article does not reference the validated hero image.')
    if PLACEHOLDER_RE.search(text):
        errors.append('Rendered article contains placeholder drafting language.')
    if '<article' not in lowered:
        errors.append('Rendered page is missing semantic article content.')
    if 'Professor OS' not in text or 'Connect.Vin' not in text:
        errors.append('Rendered article is missing Professor OS / Connect.Vin brand consistency.')
    if len(text) < 5000:
        warnings.append('Rendered article HTML is unexpectedly small; inspect before publishing.')
    return errors, warnings


def _check_media(media_result):
    errors = []
    warnings = []
    media_result = media_result or {}
    items = media_result.get('items') or []
    for item in items:
        source = str(item.get('source_page') or '').strip()
        provider = str(item.get('provider') or '').strip()
        usage_mode = str(item.get('usage_mode') or '').strip()
        if not source.startswith('http'):
            errors.append('External media item is missing a public source page: {0}'.format(item.get('title', 'media')))
        if not provider:
            errors.append('External media item is missing provider provenance: {0}'.format(item.get('title', 'media')))

        if item.get('kind') == 'image':
            license_name = str(item.get('license') or '').strip()
            license_url = str(item.get('license_url') or '').strip()
            attribution = str(item.get('attribution') or '').strip()
            if usage_mode != 'licensed_reuse':
                errors.append('External image is not marked as licensed reuse: {0}'.format(item.get('title', 'media')))
            if not license_name or not license_url:
                errors.append('External image is missing reusable license metadata: {0}'.format(item.get('title', 'media')))
            if ('cc by' in license_name.lower() or 'cc-by' in license_name.lower()) and not attribution:
                errors.append('CC BY media is missing creator attribution: {0}'.format(item.get('title', 'media')))
            if not item.get('real_world_photo'):
                warnings.append('External image is not explicitly classified as a real-world photograph: {0}'.format(item.get('title', 'media')))
            if item.get('local_path'):
                path = Path(item['local_path'])
                if not path.exists() or path.stat().st_size < 10000:
                    errors.append('External teaching image is missing or suspiciously small: {0}'.format(path))

        elif item.get('kind') == 'video':
            if usage_mode != 'embed':
                errors.append('External video must remain hosted by its provider and be embedded, not re-hosted.')
            if provider.lower() == 'youtube':
                embed_url = str(item.get('embed_url') or '')
                video_id = str(item.get('video_id') or '')
                if not embed_url.startswith('https://www.youtube.com/embed/') or not video_id:
                    errors.append('YouTube resource is missing a valid embed URL/video ID.')
            if not item.get('attribution'):
                errors.append('External video is missing creator/channel credit.')

    if media_result.get('used') and not items:
        errors.append('Media manifest says external media was used but contains no media items.')
    if media_result.get('recommended') and not items:
        try:
            from .config import settings
            required = settings.require_recommended_media
        except Exception:
            required = False
        if required:
            errors.append('Editorial review recommended real-world media, but no legally verified image/video passed selection.')
        else:
            warnings.append('Editorial review recommended real-world media, but none passed selection.')
    return errors, warnings


def final_publication_gate(lesson, output_dir, quality_report, linkedin_preflight, media_result, code_paths):
    output_dir = Path(output_dir)
    errors = []
    warnings = []
    checks = {}

    quality_ok = bool((quality_report or {}).get('passed'))
    checks['editorial_quality'] = quality_ok
    if not quality_ok:
        errors.append('Premium editorial quality report did not pass.')

    linkedin_ok = bool((linkedin_preflight or {}).get('passed'))
    checks['linkedin_preflight'] = linkedin_ok
    if not linkedin_ok:
        errors.append('LinkedIn preflight did not pass.')

    required = [
        output_dir / 'README.md',
        output_dir / 'index.html',
        output_dir / 'linkedin_preview.html',
        output_dir / 'hero.png',
        output_dir / 'diagram.png',
        output_dir / 'QUALITY_REPORT.json',
        output_dir / 'LINKEDIN_PREFLIGHT.json',
        output_dir / 'MEDIA_CREDITS.md',
    ]
    missing = [str(path) for path in required if not path.exists()]
    checks['required_artifacts'] = not missing
    for path in missing:
        errors.append('Required publication artifact is missing: {0}'.format(path))

    if not code_paths:
        errors.append('No validated Python lab files were packaged.')
    checks['code_package'] = bool(code_paths) and all(Path(path).exists() for path in code_paths)
    if code_paths and not checks['code_package']:
        errors.append('At least one validated Python lab file disappeared before publication.')

    for filename, minimum in [('hero.png', (1200, 630)), ('diagram.png', (1200, 630))]:
        path = output_dir / filename
        if path.exists():
            try:
                width, height = _png_dimensions(path)
                if width < minimum[0] or height < minimum[1]:
                    errors.append('{0} resolution is too small: {1}x{2}.'.format(filename, width, height))
                ratio = float(width) / float(height)
                if abs(ratio - (16.0 / 9.0)) > 0.12:
                    warnings.append('{0} is not close to a 16:9 presentation ratio.'.format(filename))
            except Exception as exc:
                errors.append(str(exc))
    checks['visual_assets'] = not any('hero.png' in item or 'diagram.png' in item for item in errors)

    article_errors, article_warnings = _check_html(
        output_dir / 'index.html', lesson.get('title', ''), 'hero.png')
    errors.extend(article_errors)
    warnings.extend(article_warnings)
    checks['article_design'] = not article_errors

    preview_path = output_dir / 'linkedin_preview.html'
    preview_errors = []
    preview_warnings = []
    if not preview_path.exists():
        preview_errors.append('LinkedIn preview HTML is missing.')
    else:
        preview_text = preview_path.read_text(encoding='utf-8')
        preview_lower = preview_text.lower()
        if '<meta name="viewport"' not in preview_lower:
            preview_errors.append('LinkedIn preview is missing responsive viewport metadata.')
        if '@media' not in preview_text:
            # The preview has a fixed feed-width design, but should still remain usable on phones.
            preview_warnings.append('LinkedIn preview has no explicit media query; verify narrow-screen flow.')
        if 'font-family:' not in preview_lower:
            preview_errors.append('LinkedIn preview is missing a typography declaration.')
        if 'hero.png' not in preview_text:
            preview_errors.append('LinkedIn preview does not reference the validated hero image.')
        if PLACEHOLDER_RE.search(preview_text):
            preview_errors.append('LinkedIn preview contains placeholder drafting language.')
    errors.extend(preview_errors)
    warnings.extend(preview_warnings)
    checks['linkedin_preview_design'] = not preview_errors

    media_errors, media_warnings = _check_media(media_result)
    errors.extend(media_errors)
    warnings.extend(media_warnings)
    checks['media_licensing'] = not media_errors

    gate = {
        'passed': len(errors) == 0,
        'checks': checks,
        'errors': errors,
        'warnings': warnings,
        'message': ('Publication package passed every final gate.' if not errors
                    else 'Publication blocked by {0} final issue(s).'.format(len(errors))),
    }
    (output_dir / 'PUBLICATION_GATE.json').write_text(json.dumps(gate, indent=2), encoding='utf-8')
    return gate
