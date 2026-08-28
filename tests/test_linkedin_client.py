from teacher_agent import linkedin_client


class DummyResponse(object):
    def __init__(
            self,
            status_code=200,
            json_data=None,
            headers=None,
            text=''):
        self.status_code = status_code
        self._json = json_data or {}
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('http error')


def test_linkedin_publisher_uploads_class_thumbnail_as_native_image_post(
        monkeypatch,
        tmp_path):
    monkeypatch.setattr(
        linkedin_client.settings,
        'linkedin_access_token',
        'token'
    )
    monkeypatch.setattr(
        linkedin_client.settings,
        'linkedin_author_urn',
        'urn:li:person:123'
    )
    monkeypatch.setattr(
        linkedin_client.settings,
        'linkedin_version',
        '202607'
    )

    calls = []

    def fake_request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        if 'images?action=initializeUpload' in url:
            return DummyResponse(
                200,
                {
                    'value': {
                        'uploadUrl': 'https://upload.example/image',
                        'image': 'urn:li:image:abc'
                    }
                }
            )
        if url == 'https://upload.example/image':
            return DummyResponse(201)
        return DummyResponse(
            201,
            headers={'x-restli-id': 'urn:li:share:1'}
        )

    monkeypatch.setattr(
        linkedin_client,
        'request_with_retry',
        fake_request
    )

    hero = tmp_path / 'hero.png'
    hero.write_bytes(b'PNGDATA')
    package = {
        'source': 'https://connect.vin/professor-os',
        'title': 'Lesson title',
        'description': 'Lesson description',
        'commentary': (
            'Lesson commentary\n\n'
            'Explore Professor OS: https://connect.vin/professor-os'
        ),
        'thumbnail_alt_text': 'Class thumbnail',
        'post_type': 'image',
    }

    result = (
        linkedin_client.LinkedInPublisher()
        .publish_lesson_post(package, hero)
    )

    assert result['image_urn'] == 'urn:li:image:abc'
    assert result['post_type'] == 'image'

    final_payload = calls[-1][2]['json']

    # Native image post: no article/link-card payload.
    assert 'article' not in final_payload['content']
    assert final_payload['content']['media']['id'] == 'urn:li:image:abc'
    assert (
        final_payload['content']['media']['altText']
        == 'Class thumbnail'
    )

    # Connect.Vin link is part of the visible post commentary.
    assert (
        'https://connect.vin/professor-os'
        in final_payload['commentary']
    )


def test_linkedin_image_post_requires_class_thumbnail(
        monkeypatch):
    monkeypatch.setattr(
        linkedin_client.settings,
        'linkedin_access_token',
        'token'
    )
    monkeypatch.setattr(
        linkedin_client.settings,
        'linkedin_author_urn',
        'urn:li:person:123'
    )

    package = {
        'commentary': 'A' * 400,
    }

    try:
        (
            linkedin_client.LinkedInPublisher()
            .publish_lesson_post(package, None)
        )
        assert False, 'Expected missing-thumbnail failure.'
    except RuntimeError as exc:
        assert 'require the class thumbnail' in str(exc)
