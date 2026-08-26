import base64
import io

from PIL import Image

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

    def _decode_base64_image(self, image_b64):
        if not image_b64:
            raise RuntimeError('Gemini image payload is empty.')

        if isinstance(image_b64, bytes):
            encoded = image_b64
        else:
            text = str(image_b64).strip()

            # Be tolerant if an API variant returns a data URL.
            if text.startswith('data:') and ',' in text:
                text = text.split(',', 1)[1]

            encoded = text.encode('ascii')

        try:
            return base64.b64decode(encoded)
        except Exception as exc:
            raise RuntimeError(
                'Gemini image API returned invalid base64 image data: {0}'.format(exc)
            )

    def _save_as_png(self, raw_image, output_path):
        """
        Gemini Interactions currently accepts image/jpeg for the image response.
        Professor OS keeps PNG filenames throughout the article/publication pipeline,
        so decode the returned JPEG and convert it to a real PNG before saving.
        """
        try:
            with Image.open(io.BytesIO(raw_image)) as image:
                image.load()

                if image.mode not in ('RGB', 'RGBA'):
                    image = image.convert('RGB')

                image.save(
                    str(output_path),
                    format='PNG',
                    optimize=True
                )
        except Exception as exc:
            raise RuntimeError(
                'Gemini returned image bytes that could not be decoded: {0}'.format(exc)
            )

        if not output_path.exists():
            raise RuntimeError(
                'Gemini image conversion completed without creating {0}'.format(
                    output_path
                )
            )

        try:
            with output_path.open('rb') as handle:
                signature = handle.read(8)
        except Exception as exc:
            raise RuntimeError(
                'Could not verify converted Gemini PNG: {0}'.format(exc)
            )

        if signature != b'\x89PNG\r\n\x1a\n':
            raise RuntimeError(
                'Converted Gemini image is not a valid PNG: {0}'.format(output_path)
            )

    def generate_image(self, prompt, output_path):
        payload = {
            'model': settings.gemini_image_model,
            'input': [
                {'type': 'text', 'text': prompt}
            ],
            'response_format': {
                'type': 'image',

                # The Gemini Interactions endpoint used by Professor OS currently
                # rejects image/png here and accepts image/jpeg.
                # We convert the returned JPEG to PNG locally below so the rest
                # of Professor OS can continue using hero.png / inline_XX.png.
                'mime_type': 'image/jpeg',

                'aspect_ratio': '16:9',
            },
        }

        response = request_with_retry(
            'POST',
            self.url,
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
            raise RuntimeError(
                'Gemini image API returned HTTP {0}: {1}'.format(
                    response.status_code,
                    body
                )
            )

        try:
            data = response.json()
        except ValueError:
            raise RuntimeError('Gemini image API returned a non-JSON response.')

        image_b64 = self._extract_base64(data)

        if not image_b64:
            raise RuntimeError(
                'Gemini image API returned no output_image data.'
            )

        raw_image = self._decode_base64_image(image_b64)
        self._save_as_png(raw_image, output_path)

        monitor.event(
            'success',
            'Gemini generated JPEG converted to Professor OS PNG: {0}'.format(
                output_path
            )
        )

        return output_path
