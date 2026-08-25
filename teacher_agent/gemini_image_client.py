import base64

from .config import settings
from .http_utils import request_with_retry
from .runtime import monitor


class GeminiImageClient(object):
    def __init__(self):
        if not settings.gemini_api_key:
            raise RuntimeError('GEMINI_API_KEY is missing from .env')
        self.url = 'https://generativelanguage.googleapis.com/v1beta/interactions'

    def _extract_base64(self, data):
        output_image = data.get('output_image') or {}
        image_data = output_image.get('data')
        if image_data:
            return image_data
        for step in data.get('steps', []) or []:
            parts = []
            parts.extend(step.get('content', []) or [])
            parts.extend(step.get('output', []) or [])
            for part in parts:
                if part.get('type') == 'image' and part.get('data'):
                    return part.get('data')
        return None

    def generate_image(self, prompt, output_path):
        payload = {
            'model': settings.gemini_image_model,
            'input': [
                {'type': 'text', 'text': prompt}
            ],
            'response_format': {
                'type': 'image',
                'mime_type': 'image/png',
                'aspect_ratio': '16:9',
            },
        }
        response = request_with_retry(
            'POST', self.url,
            headers={
                'x-goog-api-key': settings.gemini_api_key,
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=settings.gemini_image_timeout,
            max_attempts=settings.api_max_attempts,
            base_delay=settings.api_retry_base_delay,
        )
        try:
            response.raise_for_status()
        except Exception:
            body = response.text[-2000:] if response.text else '(empty response body)'
            raise RuntimeError('Gemini image API returned HTTP {0}: {1}'.format(
                response.status_code, body))

        try:
            data = response.json()
        except ValueError:
            raise RuntimeError('Gemini image API returned a non-JSON response.')

        image_b64 = self._extract_base64(data)
        if not image_b64:
            raise RuntimeError('Gemini image API returned no output_image data.')

        output_path.write_bytes(base64.b64decode(image_b64))
        monitor.event('success', 'Gemini generated image saved to {0}'.format(output_path))
        return output_path
