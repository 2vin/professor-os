import base64
import io

from PIL import Image

import teacher_agent.gemini_image_client as gemini_module
from teacher_agent.gemini_image_client import GeminiImageClient


class FakeResponse(object):
    status_code = 200
    text = ''

    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def _jpeg_base64(width=320, height=180):
    buffer = io.BytesIO()

    image = Image.new('RGB', (width, height), (120, 130, 140))
    image.save(buffer, format='JPEG', quality=90)

    return base64.b64encode(buffer.getvalue()).decode('ascii')


def test_gemini_requests_jpeg_and_converts_to_real_png(tmp_path, monkeypatch):
    monkeypatch.setattr(gemini_module.settings, 'gemini_api_key', 'test-key')
    monkeypatch.setattr(
        gemini_module.settings,
        'gemini_image_model',
        'gemini-3.1-flash-lite-image'
    )

    captured = {}

    def fake_request(method, url, **kwargs):
        captured['method'] = method
        captured['url'] = url
        captured['json'] = kwargs.get('json')

        return FakeResponse({
            'output_image': {
                'data': _jpeg_base64()
            }
        })

    monkeypatch.setattr(
        gemini_module,
        'request_with_retry',
        fake_request
    )

    output_path = tmp_path / 'hero.png'

    client = GeminiImageClient()
    result = client.generate_image(
        'A premium robotics educational illustration.',
        output_path
    )

    assert result == output_path
    assert output_path.exists()

    assert (
        captured['json']['response_format']['mime_type']
        == 'image/jpeg'
    )
    assert (
        captured['json']['response_format']['aspect_ratio']
        == '16:9'
    )

    with output_path.open('rb') as handle:
        assert handle.read(8) == b'\x89PNG\r\n\x1a\n'

    with Image.open(str(output_path)) as image:
        assert image.format == 'PNG'
        assert image.size == (320, 180)


def test_gemini_accepts_data_url_image_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(gemini_module.settings, 'gemini_api_key', 'test-key')

    encoded = _jpeg_base64()

    def fake_request(method, url, **kwargs):
        return FakeResponse({
            'output_image': {
                'data': 'data:image/jpeg;base64,' + encoded
            }
        })

    monkeypatch.setattr(
        gemini_module,
        'request_with_retry',
        fake_request
    )

    output_path = tmp_path / 'inline_01.png'

    GeminiImageClient().generate_image(
        'Robotics teaching diagram.',
        output_path
    )

    with Image.open(str(output_path)) as image:
        assert image.format == 'PNG'
