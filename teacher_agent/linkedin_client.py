from pathlib import Path

from .config import settings
from .http_utils import request_with_retry


class LinkedInPublisher(object):
    def __init__(self):
        if not settings.linkedin_access_token or not settings.linkedin_author_urn:
            raise RuntimeError('LinkedIn publishing credentials are incomplete.')
        self.posts_url = 'https://api.linkedin.com/rest/posts'
        self.images_url = 'https://api.linkedin.com/rest/images?action=initializeUpload'
        self.headers = {
            'Authorization': 'Bearer ' + settings.linkedin_access_token,
            'LinkedIn-Version': settings.linkedin_version,
            'X-Restli-Protocol-Version': '2.0.0',
            'Content-Type': 'application/json',
        }

    def upload_thumbnail(self, image_path):
        image_path = Path(image_path)
        if not image_path.exists():
            raise RuntimeError('LinkedIn thumbnail does not exist: {0}'.format(image_path))

        initialize = request_with_retry(
            'POST', self.images_url,
            headers=self.headers,
            json={'initializeUploadRequest': {'owner': settings.linkedin_author_urn}},
            timeout=45,
            max_attempts=2,
            base_delay=settings.api_retry_base_delay,
        )
        initialize.raise_for_status()
        try:
            value = initialize.json()['value']
            upload_url = value['uploadUrl']
            image_urn = value['image']
        except Exception:
            raise RuntimeError('LinkedIn image initialization returned an unexpected response.')

        upload = request_with_retry(
            'PUT', upload_url,
            headers={'Content-Type': 'application/octet-stream'},
            data=image_path.read_bytes(),
            timeout=90,
            max_attempts=2,
            base_delay=settings.api_retry_base_delay,
        )
        if upload.status_code not in (200, 201, 202):
            upload.raise_for_status()
        return image_urn

    def publish_lesson_post(self, package, hero_path=None):
        thumbnail_urn = None
        if hero_path:
            thumbnail_urn = self.upload_thumbnail(hero_path)
        elif settings.linkedin_require_thumbnail:
            raise RuntimeError('LinkedIn premium publishing requires a validated thumbnail.')

        article = {
            'source': package['source'],
            'title': package['title'],
            'description': package['description'],
        }
        if thumbnail_urn:
            article['thumbnail'] = thumbnail_urn
            article['thumbnailAltText'] = package.get('thumbnail_alt_text', '')

        payload = {
            'author': settings.linkedin_author_urn,
            'commentary': package['commentary'],
            'visibility': 'PUBLIC',
            'distribution': {
                'feedDistribution': 'MAIN_FEED',
                'targetEntities': [],
                'thirdPartyDistributionChannels': [],
            },
            'content': {'article': article},
            'lifecycleState': 'PUBLISHED',
            'isReshareDisabledByAuthor': False,
        }
        response = request_with_retry(
            'POST', self.posts_url,
            headers=self.headers,
            json=payload,
            timeout=45,
            # Do not blindly retry the final publishing POST: if LinkedIn accepted the first
            # request but the client lost the response, retrying could create a duplicate post.
            max_attempts=1,
            base_delay=settings.api_retry_base_delay,
        )
        try:
            response.raise_for_status()
        except Exception:
            body = response.text[-2000:] if response.text else '(empty response body)'
            raise RuntimeError('LinkedIn post creation failed HTTP {0}: {1}'.format(
                response.status_code, body))
        return {
            'status_code': response.status_code,
            'post_id': response.headers.get('x-restli-id') or response.headers.get('X-RestLi-Id'),
            'thumbnail_urn': thumbnail_urn,
        }
