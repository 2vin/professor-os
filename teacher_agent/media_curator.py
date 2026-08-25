import json
import math
import re
from pathlib import Path
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .config import settings
from .http_utils import request_with_retry
from .runtime import monitor


COMMONS_API = 'https://commons.wikimedia.org/w/api.php'
GOOGLE_CSE_API = 'https://customsearch.googleapis.com/customsearch/v1'
YOUTUBE_SEARCH_API = 'https://www.googleapis.com/youtube/v3/search'
YOUTUBE_VIDEOS_API = 'https://www.googleapis.com/youtube/v3/videos'

BAD_VISUAL_WORDS = (
    'cartoon', 'clipart', 'clip art', 'illustration', 'drawing', 'icon', 'logo',
    'mascot', 'vector', 'anime', 'comic', 'rendering', 'concept art', 'toy',
)
PHOTO_WORDS = ('photo', 'photograph', 'laboratory', 'industrial', 'prototype', 'robot', 'hardware', 'factory')


def _metadata_value(metadata, key, default=''):
    value = metadata.get(key, default)
    if isinstance(value, dict):
        return value.get('value', default)
    return value or default


def _strip_html(value):
    text = re.sub(r'<[^>]+>', ' ', str(value or ''))
    replacements = {
        '&nbsp;': ' ', '&amp;': '&', '&quot;': '"', '&#39;': "'", '&lt;': '<', '&gt;': '>'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r'\s+', ' ', text).strip()


def _safe_license_url(url):
    value = str(url or '').lower().strip()
    if not value:
        return False
    if 'creativecommons.org/publicdomain/zero/' in value:
        return True
    if 'creativecommons.org/publicdomain/mark/' in value:
        return True
    if 'creativecommons.org/licenses/by/' in value:
        if '/by-sa/' not in value and '/by-nc' not in value and '/by-nd' not in value:
            return True
    return False


def _license_name_from_url(url):
    value = str(url or '').lower()
    if 'publicdomain/zero' in value:
        return 'CC0'
    if 'publicdomain/mark' in value:
        return 'Public Domain Mark'
    if '/licenses/by/' in value:
        version = re.search(r'/licenses/by/([0-9.]+)/?', value)
        return 'CC BY {0}'.format(version.group(1) if version else '')
    return 'Open license'


def license_is_safe_for_public_reuse(metadata):
    non_free = str(_metadata_value(metadata, 'NonFree', '')).lower()
    if non_free in ('true', '1', 'yes'):
        return False
    restrictions = _metadata_value(metadata, 'Restrictions', '')
    if restrictions and str(restrictions).strip() not in ('[]', '{}', 'none', 'None'):
        return False
    copyrighted = str(_metadata_value(metadata, 'Copyrighted', '')).lower()
    license_name = _strip_html(_metadata_value(metadata, 'LicenseShortName', '')).lower()
    if copyrighted == 'false' or 'public domain' in license_name or license_name == 'pd':
        return True
    if 'cc0' in license_name:
        return True
    if ('cc by' in license_name or 'cc-by' in license_name):
        if 'sa' not in license_name and 'nc' not in license_name and 'nd' not in license_name:
            return True
    return False


def _candidate_score(page, info, query_terms):
    width = int(info.get('width') or 0)
    height = int(info.get('height') or 0)
    if not width or not height:
        return -1000
    score = min(35, int(width / 90))
    ratio = float(width) / float(height)
    score += max(0, 24 - int(abs(ratio - (16.0 / 9.0)) * 15))

    title = str(page.get('title') or '').lower()
    metadata = info.get('extmetadata') or {}
    description = _strip_html(_metadata_value(metadata, 'ImageDescription', '')).lower()
    searchable = title + ' ' + description
    for term in query_terms:
        if term and term in searchable:
            score += 6
    for word in BAD_VISUAL_WORDS:
        if word in searchable:
            score -= 40
    for word in PHOTO_WORDS:
        if word in searchable:
            score += 5
    if str(info.get('mime') or '').lower() == 'image/jpeg':
        score += 22
    if str(info.get('mediatype') or '').upper() == 'BITMAP':
        score += 18

    assessments = _strip_html(_metadata_value(metadata, 'Assessments', '')).lower()
    if 'featured' in assessments:
        score += 35
    if 'quality' in assessments:
        score += 25
    if 'valued' in assessments:
        score += 12
    return score


def _search_commons(query, limit=24):
    params = {
        'action': 'query', 'format': 'json', 'formatversion': 2,
        'generator': 'search', 'gsrsearch': query, 'gsrnamespace': 6,
        'gsrlimit': limit, 'prop': 'imageinfo',
        'iiprop': 'url|size|mime|mediatype|extmetadata',
        'iiextmetadatafilter': (
            'LicenseShortName|LicenseUrl|UsageTerms|Artist|Credit|Attribution|'
            'AttributionRequired|NonFree|Restrictions|Assessments|ImageDescription|Copyrighted'),
        'iiextmetadatalanguage': 'en', 'iiurlwidth': 1800, 'origin': '*',
    }
    response = request_with_retry(
        'GET', COMMONS_API, params=params, timeout=30,
        max_attempts=settings.api_max_attempts,
        base_delay=settings.api_retry_base_delay)
    response.raise_for_status()
    return ((response.json().get('query') or {}).get('pages') or [])


def _build_commons_candidate(page):
    infos = page.get('imageinfo') or []
    if not infos:
        return None
    info = infos[0]
    metadata = info.get('extmetadata') or {}
    if not license_is_safe_for_public_reuse(metadata):
        return None
    media_type = str(info.get('mediatype') or '').upper()
    mime = str(info.get('mime') or '').lower()
    # Real-world mode intentionally excludes vector/drawing assets.
    if settings.prefer_real_photos and media_type != 'BITMAP':
        return None
    if media_type not in ('BITMAP', 'DRAWING') or mime not in ('image/jpeg', 'image/png'):
        return None
    if int(info.get('width') or 0) < settings.external_media_min_width:
        return None

    license_name = _strip_html(_metadata_value(metadata, 'LicenseShortName', ''))
    license_url = _strip_html(_metadata_value(metadata, 'LicenseUrl', ''))
    attribution = _strip_html(_metadata_value(metadata, 'Attribution', ''))
    if not attribution:
        attribution = _strip_html(_metadata_value(metadata, 'Artist', ''))
    license_lower = license_name.lower()
    if ('cc by' in license_lower or 'cc-by' in license_lower) and (not attribution or not license_url):
        return None

    description = _strip_html(_metadata_value(metadata, 'ImageDescription', ''))
    source_page = info.get('descriptionurl') or ''
    searchable = (str(page.get('title') or '') + ' ' + description).lower()
    if settings.prefer_real_photos and any(word in searchable for word in BAD_VISUAL_WORDS):
        return None

    return {
        'kind': 'image', 'provider': 'Wikimedia Commons', 'usage_mode': 'licensed_reuse',
        'title': str(page.get('title') or '').replace('File:', ''),
        'source_page': source_page, 'download_url': info.get('thumburl') or info.get('url'),
        'license': license_name, 'license_url': license_url,
        'attribution': attribution or 'See source page for creator attribution',
        'description': description, 'width': int(info.get('width') or 0),
        'height': int(info.get('height') or 0), 'mime': info.get('mime'),
        'mediatype': media_type, 'real_world_photo': media_type == 'BITMAP',
    }



def _build_candidate(page, kind):
    # Backward-compatible helper used by the test suite and older integrations.
    if kind == 'image':
        return _build_commons_candidate(page)
    return None

def _best_commons_photo(query):
    queries = [query + ' photograph', query + ' photo', query]
    best = None
    best_score = -10000
    terms = [x.lower() for x in re.findall(r'[a-zA-Z0-9]+', query) if len(x) > 3]
    for search_query in queries:
        for page in _search_commons(search_query):
            item = _build_commons_candidate(page)
            if not item:
                continue
            info = (page.get('imageinfo') or [{}])[0]
            score = _candidate_score(page, info, terms)
            if score > best_score:
                best = item
                best_score = score
    if best:
        best['_score'] = best_score
    return best


def _extract_page_license(source_html):
    html = str(source_html or '')[:400000]
    # Prefer explicit rel=license metadata.
    patterns = [
        r'<(?:link|a)[^>]+rel=["\'][^"\']*license[^"\']*["\'][^>]+href=["\']([^"\']+)["\']',
        r'<(?:link|a)[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\'][^"\']*license[^"\']*["\']',
    ]
    license_url = ''
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match and _safe_license_url(match.group(1)):
            license_url = match.group(1)
            break
    if not license_url:
        urls = re.findall(r'https?://creativecommons\.org/(?:licenses/by/[^"\'<>\s]+|publicdomain/(?:zero|mark)/[^"\'<>\s]+)', html, re.I)
        for url in urls:
            if _safe_license_url(url):
                license_url = url
                break
    author = ''
    for pattern in [
        r'<meta[^>]+name=["\'](?:author|dc\.creator|citation_author)["\'][^>]+content=["\']([^"\']+)["\']',
        r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\'](?:author|dc\.creator|citation_author)["\']',
    ]:
        match = re.search(pattern, html, re.I)
        if match:
            author = _strip_html(match.group(1))
            break
    return license_url, author


def _google_image_candidates(query):
    if not settings.google_image_search_enabled or not settings.google_cse_api_key or not settings.google_cse_id:
        return []
    found = []
    for rights in ('cc_publicdomain', 'cc_attribute'):
        params = {
            'key': settings.google_cse_api_key, 'cx': settings.google_cse_id, 'q': query,
            'searchType': 'image', 'imgType': 'photo', 'imgSize': 'xlarge',
            'safe': 'active', 'rights': rights, 'num': 10,
        }
        response = request_with_retry(
            'GET', GOOGLE_CSE_API, params=params, timeout=30,
            max_attempts=settings.api_max_attempts,
            base_delay=settings.api_retry_base_delay)
        response.raise_for_status()
        for item in response.json().get('items') or []:
            image = item.get('image') or {}
            width = int(image.get('width') or 0)
            if width < settings.external_media_min_width:
                continue
            source_page = image.get('contextLink') or ''
            image_url = item.get('link') or ''
            if not source_page.startswith('http') or not image_url.startswith('http'):
                continue
            # Google Usage Rights is a discovery filter, not the final legal decision.
            try:
                page = request_with_retry(
                    'GET', source_page, timeout=25,
                    max_attempts=min(3, settings.api_max_attempts),
                    base_delay=settings.api_retry_base_delay,
                    headers={'User-Agent': 'ProfessorOS/10 media-license-check'})
                if page.status_code >= 400:
                    continue
                license_url, author = _extract_page_license(page.text)
            except Exception:
                continue
            if not _safe_license_url(license_url):
                continue
            found.append({
                'kind': 'image', 'provider': 'Google Images discovery',
                'usage_mode': 'licensed_reuse', 'title': _strip_html(item.get('title') or 'Real-world reference'),
                'source_page': source_page, 'download_url': image_url,
                'license': _license_name_from_url(license_url), 'license_url': license_url,
                'attribution': author or (urlparse(source_page).netloc or 'Original source'),
                'description': _strip_html(item.get('snippet') or ''),
                'width': width, 'height': int(image.get('height') or 0),
                'mime': item.get('mime') or 'image/jpeg', 'real_world_photo': True,
                'google_usage_rights_filter': rights,
            })
    return found


def _download_image(item, media_dir, filename='real_world_reference'):
    mime = str(item.get('mime') or '').lower()
    suffix = '.png' if 'png' in mime else '.jpg'
    target = media_dir / (filename + suffix)
    response = request_with_retry(
        'GET', item['download_url'], timeout=45,
        max_attempts=settings.api_max_attempts,
        base_delay=settings.api_retry_base_delay,
        headers={'User-Agent': 'ProfessorOS/10 educational-media'})
    response.raise_for_status()
    content_type = str(response.headers.get('Content-Type') or '').lower()
    if 'image/' not in content_type and len(response.content) < 10000:
        raise RuntimeError('Selected external photo did not return a valid image response.')
    target.write_bytes(response.content)
    item['local_path'] = str(target)
    item['relative_path'] = 'media/' + target.name
    return item


def _iso_duration_seconds(value):
    match = re.match(r'^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$', str(value or ''))
    if not match:
        return 0
    hours, minutes, seconds = [int(x or 0) for x in match.groups()]
    return hours * 3600 + minutes * 60 + seconds


def _youtube_video(query):
    if not settings.youtube_media_enabled or not settings.youtube_api_key:
        return None
    params = {
        'part': 'snippet', 'q': query, 'type': 'video',
        'maxResults': settings.youtube_max_results, 'videoEmbeddable': 'true',
        'safeSearch': 'strict', 'relevanceLanguage': 'en', 'order': 'relevance',
        'key': settings.youtube_api_key,
    }
    response = request_with_retry(
        'GET', YOUTUBE_SEARCH_API, params=params, timeout=30,
        max_attempts=settings.api_max_attempts,
        base_delay=settings.api_retry_base_delay)
    response.raise_for_status()
    search_items = response.json().get('items') or []
    ids = [((item.get('id') or {}).get('videoId')) for item in search_items]
    ids = [x for x in ids if x]
    if not ids:
        return None

    detail = request_with_retry(
        'GET', YOUTUBE_VIDEOS_API,
        params={'part': 'snippet,contentDetails,statistics,status', 'id': ','.join(ids), 'key': settings.youtube_api_key},
        timeout=30, max_attempts=settings.api_max_attempts,
        base_delay=settings.api_retry_base_delay)
    detail.raise_for_status()
    details = {item.get('id'): item for item in detail.json().get('items') or []}
    terms = [x.lower() for x in re.findall(r'[a-zA-Z0-9]+', query) if len(x) > 3]
    ranked = []
    for video_id in ids:
        item = details.get(video_id) or {}
        snippet = item.get('snippet') or {}
        status = item.get('status') or {}
        if status.get('embeddable') is False:
            continue
        title = str(snippet.get('title') or '')
        channel = str(snippet.get('channelTitle') or '')
        searchable = (title + ' ' + str(snippet.get('description') or '')).lower()
        score = sum(7 for term in terms if term in searchable)
        channel_lower = channel.lower()
        if any(trusted in channel_lower or channel_lower in trusted for trusted in settings.youtube_trusted_channels):
            score += 60
        if any(word in searchable for word in ('tutorial', 'lecture', 'explained', 'demo', 'demonstration', 'robot', 'robotics')):
            score += 12
        try:
            views = int((item.get('statistics') or {}).get('viewCount') or 0)
        except (TypeError, ValueError):
            views = 0
        if views > 0:
            score += min(28, int(math.log10(max(10, views)) * 5))
        duration = _iso_duration_seconds((item.get('contentDetails') or {}).get('duration'))
        if 120 <= duration <= 1800:
            score += 20
        elif duration > 3600:
            score -= 10
        ranked.append((score, {
            'kind': 'video', 'provider': 'YouTube', 'usage_mode': 'embed',
            'title': title, 'source_page': 'https://www.youtube.com/watch?v=' + video_id,
            'embed_url': 'https://www.youtube.com/embed/' + video_id,
            'video_id': video_id, 'license': 'YouTube-hosted embed', 'license_url': '',
            'attribution': channel or 'YouTube creator',
            'description': _strip_html(snippet.get('description') or ''),
            'thumbnail_url': (((snippet.get('thumbnails') or {}).get('high') or {}).get('url')),
            'duration_seconds': duration, 'view_count': views,
        }))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return ranked[0][1] if ranked else None


def _choose_real_photo(query):
    # Google Images can discover highly relevant photography, but only strictly verified license pages are usable.
    try:
        google = _google_image_candidates(query)
        if google:
            google.sort(key=lambda x: int(x.get('width') or 0), reverse=True)
            return google[0]
    except Exception as exc:
        monitor.event('warning', 'Google image discovery unavailable: {0}'.format(exc))
    return _best_commons_photo(query)


def curate_open_media(lesson, ai_review, output_dir):
    recommended = bool(ai_review and ai_review.get('media_would_help'))
    media_style = str((ai_review or {}).get('media_style') or 'none').lower()
    result = {
        'used': False, 'recommended': recommended, 'items': [],
        'query': '', 'media_style': media_style,
        'reason': str((ai_review or {}).get('media_reason') or ''),
        'insert_after_heading': str((ai_review or {}).get('media_insert_after_heading') or '## Real Robot Connection'),
        'note': 'Real-world media is selected only when it materially improves learning.',
    }
    if not settings.enable_external_media:
        result['note'] = 'External media enrichment is disabled.'
        return result
    if not recommended:
        result['note'] = 'Editorial review determined that external media is not necessary for this lesson.'
        return result

    base_query = ((ai_review or {}).get('image_query') or (ai_review or {}).get('media_query') or
                  '{0} robotics'.format(lesson.get('title', 'robotics')))
    youtube_query = ((ai_review or {}).get('youtube_query') or
                     '{0} robotics explained'.format(lesson.get('title', 'robotics')))
    result['query'] = base_query
    media_dir = Path(output_dir) / 'media'
    media_dir.mkdir(parents=True, exist_ok=True)

    wants_photo = media_style in ('photo', 'mixed', 'none')
    wants_video = media_style in ('video', 'mixed')
    if media_style == 'none':
        wants_photo = True
        wants_video = True

    if wants_photo and len(result['items']) < settings.external_media_max_items:
        try:
            photo = _choose_real_photo(base_query)
            if photo:
                photo = _download_image(photo, media_dir)
                result['items'].append(photo)
                result['used'] = True
                monitor.event('success', 'Added real-world licensed teaching photo from {0}: {1}'.format(
                    photo.get('provider'), photo.get('title')))
            else:
                monitor.event('warning', 'No real-world photograph passed relevance and license verification.')
        except Exception as exc:
            monitor.event('warning', 'Real-world photo enrichment failed: {0}'.format(exc))

    if wants_video and len(result['items']) < settings.external_media_max_items:
        try:
            video = _youtube_video(youtube_query)
            if video:
                result['items'].append(video)
                result['used'] = True
                monitor.event('success', 'Added embeddable expert YouTube resource: {0} · {1}'.format(
                    video.get('attribution'), video.get('title')))
            elif settings.youtube_media_enabled:
                monitor.event('info', 'No suitable embeddable YouTube video was available for this lesson.')
        except Exception as exc:
            monitor.event('warning', 'YouTube media search unavailable: {0}'.format(exc))

    if recommended and not result['items']:
        result['note'] = 'Media was recommended by the editorial board, but no candidate passed legal/relevance checks.'

    manifest_path = Path(output_dir) / 'media_manifest.json'
    manifest_path.write_text(json.dumps(result, indent=2), encoding='utf-8')
    return result


def media_credits_markdown(media_result):
    items = media_result.get('items') or []
    if not items:
        return '# Media Credits\n\nNo external media was used. Professor OS generated the lesson visuals.\n'
    lines = [
        '# Media Credits', '',
        'External media is included only when it materially improves learning and its usage path can be verified.', ''
    ]
    for index, item in enumerate(items, 1):
        lines.extend([
            '## {0}. {1}'.format(index, item.get('title', 'Media resource')), '',
            '- Provider: {0}'.format(item.get('provider') or 'Original source'),
            '- Usage mode: {0}'.format(item.get('usage_mode') or 'source link'),
            '- Source: {0}'.format(item.get('source_page') or 'See original source'),
            '- Creator/channel: {0}'.format(item.get('attribution') or 'See source page'),
        ])
        if item.get('kind') == 'image':
            lines.extend([
                '- License: {0}'.format(item.get('license') or 'See source page'),
                '- License URL: {0}'.format(item.get('license_url') or 'See source page'),
            ])
        else:
            lines.append('- Video remains hosted by YouTube and is embedded through the YouTube player; Professor OS does not download or re-host it.')
        lines.append('')
    return '\n'.join(lines)


def _insert_media_block(markdown, heading, block):
    heading = heading if heading and heading.startswith('## ') else '## Real Robot Connection'
    position = markdown.find(heading)
    if position < 0:
        heading = '## Real Robot Connection'
        position = markdown.find(heading)
    if position < 0:
        marker = '## Next Class'
        position = markdown.find(marker)
        if position >= 0:
            return markdown[:position].rstrip() + '\n\n' + block + '\n\n' + markdown[position:]
        return markdown.rstrip() + '\n\n' + block + '\n'
    line_end = markdown.find('\n', position)
    if line_end < 0:
        line_end = len(markdown)
    return markdown[:line_end + 1] + '\n' + block + '\n\n' + markdown[line_end + 1:]


def append_media_resources(markdown, media_result):
    items = media_result.get('items') or []
    if not items:
        return markdown
    section = ['### Open Media Resource · Real-World Reference', '']
    reason = str(media_result.get('reason') or '').strip()
    if reason:
        section.extend([reason, ''])
    for item in items:
        if item.get('kind') == 'image' and item.get('relative_path'):
            section.append('![Real-world robotics reference: {0}]({1})'.format(
                item.get('title', 'robotics hardware'), item['relative_path']))
            section.append('')
            section.append('*Photo: {0} — {1}. Source: [{2}]({3}).*'.format(
                item.get('attribution', 'creator listed on source page'),
                item.get('license', 'open license'), item.get('provider', 'source'),
                item.get('source_page', '')))
            section.append('')
        elif item.get('kind') == 'video':
            if item.get('video_id'):
                section.append('<!-- PROFESSOR_OS_YOUTUBE:{0} -->'.format(item['video_id']))
            section.append('**Watch:** [{0}]({1}) — {2}.'.format(
                item.get('title', 'Video resource'), item.get('source_page', ''),
                item.get('attribution', 'source creator')))
            section.append('')
    block = '\n'.join(section).strip()
    return _insert_media_block(markdown, media_result.get('insert_after_heading'), block)


def append_generated_teaching_visual(markdown, lesson):
    marker = '![Professor OS engineering schematic](diagram.png)'
    if marker in markdown:
        return markdown
    block = (
        '### AI-Generated Engineering Visual · Professor OS\n\n'
        + marker + '\n\n'
        + '**How to read this visual:** Trace the signal or idea from left to right. '
          'Match each block to the lesson explanation, then predict what would change if one block produced a wrong value.\n'
    )
    return _insert_media_block(markdown, '## See It in Your Head', block)


def media_review_context(media_result, hero_path=None, diagram_path=None):
    lines = []
    if hero_path:
        lines.append('Generated 16:9 Professor OS cover: {0}'.format(hero_path))
    if diagram_path:
        lines.append('Generated premium engineering schematic visual: {0}; referenced in the lesson as diagram.png.'.format(diagram_path))
    items = (media_result or {}).get('items') or []
    if not items:
        lines.append('No external media was selected; generated visual assets are the teaching visuals.')
    for item in items:
        if item.get('kind') == 'image':
            lines.append('Verified real-world image: {0}; provider={1}; license={2}; credited={3}.'.format(
                item.get('title','image'), item.get('provider','source'), item.get('license',''), item.get('attribution','')))
        elif item.get('kind') == 'video':
            lines.append('Embedded YouTube teaching video: {0}; channel/creator={1}; embed source retained.'.format(
                item.get('title','video'), item.get('attribution','')))
    reason = str((media_result or {}).get('reason') or '').strip()
    if reason:
        lines.append('Pedagogical media purpose: ' + reason)
    return '\n'.join(lines)
