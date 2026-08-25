import base64

from teacher_agent.gemini_image_client import GeminiImageClient


def test_extracts_rest_interactions_step_content_image():
    client = GeminiImageClient.__new__(GeminiImageClient)
    payload = base64.b64encode(b'pngdata').decode('ascii')
    data = {
        'steps': [
            {'type': 'model_output', 'content': [
                {'type': 'image', 'data': payload, 'mime_type': 'image/png'}
            ]}
        ]
    }
    assert client._extract_base64(data) == payload


def test_extracts_output_image_convenience_shape():
    client = GeminiImageClient.__new__(GeminiImageClient)
    assert client._extract_base64({'output_image': {'data': 'abc'}}) == 'abc'
