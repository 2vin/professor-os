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
        """Upload the class thumbnail as a LinkedIn Image asset."""
        image_path = Path(image_path)
        if not image_path.exists():
            raise RuntimeError(
                'LinkedIn class thumbnail does not exist: {0}'.format(
                    image_path
                )
            )

        initialize = request_with_retry(
            'POST',
            self.images_url,
            headers=self.headers,
            json={
                'initializeUploadRequest': {
                    'owner': settings.linkedin_author_urn
                }
            },
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
            raise RuntimeError(
                'LinkedIn image initialization returned an unexpected response.'
            )

        upload = request_with_retry(
            'PUT',
            upload_url,
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
        """
        Publish a native LinkedIn IMAGE post.

        The class thumbnail is uploaded as the post media. The Connect.Vin link
        lives in commentary instead of creating a LinkedIn article/link card.
        """
        if not hero_path:
            raise RuntimeError(
                'Professor OS LinkedIn image posts require the class thumbnail.'
            )

        image_urn = self.upload_thumbnail(hero_path)

        media = {
            'id': image_urn,
            'altText': package.get('thumbnail_alt_text', ''),
        }

        payload = {
            'author': settings.linkedin_author_urn,
            'commentary': package['commentary'],
            'visibility': 'PUBLIC',
            'distribution': {
                'feedDistribution': 'MAIN_FEED',
                'targetEntities': [],
                'thirdPartyDistributionChannels': [],
            },
            # Native image post. Do NOT use content.article here.
            'content': {
                'media': media
            },
            'lifecycleState': 'PUBLISHED',
            'isReshareDisabledByAuthor': False,
        }

        response = request_with_retry(
            'POST',
            self.posts_url,
            headers=self.headers,
            json=payload,
            timeout=45,
            # Never blindly retry final publication because that can duplicate
            # an already accepted LinkedIn post.
            max_attempts=1,
            base_delay=settings.api_retry_base_delay,
        )
        try:
            response.raise_for_status()
        except Exception:
            body = (
                response.text[-2000:]
                if response.text
                else '(empty response body)'
            )
            raise RuntimeError(
                'LinkedIn image post creation failed HTTP {0}: {1}'.format(
                    response.status_code,
                    body
                )
            )

        post_id = (
            response.headers.get('x-restli-id')
            or response.headers.get('X-RestLi-Id')
        )
        return {
            'status_code': response.status_code,
            'post_id': post_id,
            'image_urn': image_urn,
            # Keep the old result field for compatibility with existing runtime
            # consumers/tests that may still read thumbnail_urn.
            'thumbnail_urn': image_urn,
            'post_type': 'image',
        }
