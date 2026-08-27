import json
from pathlib import Path

import teacher_agent.podcast as podcast_module
from teacher_agent.podcast import (
    PODCAST_FILENAME,
    PODCAST_META_FILENAME,
    inject_podcast_ui,
    synthesize_podcast,
    validate_podcast_package,
)


class FakeSpeechResponse(object):
    status_code = 200
    text = ''

    def __init__(self, content):
        self.content = content

    def raise_for_status(self):
        return None


def _fake_mp3():
    return b'ID3' + (b'podcast-audio' * 1000)


def _metadata():
    return {
        'filename': PODCAST_FILENAME,
        'transcript_filename': 'podcast_transcript.txt',
        'class_no': 1,
        'title': 'What Is a Robot?',
        'script_words': 900,
        'estimated_minutes': 6,
        'tts_model': 'gpt-4o-mini-tts',
        'voice': 'alloy',
        'synthetic_narration': True,
    }


def test_speech_generation_requests_mp3_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr(podcast_module.settings, 'openai_api_key', 'test-key')
    monkeypatch.setattr(podcast_module.settings, 'podcast_tts_model', 'gpt-4o-mini-tts')
    monkeypatch.setattr(podcast_module.settings, 'podcast_voice', 'alloy')
    monkeypatch.setattr(podcast_module.settings, 'podcast_timeout', 180)

    captured = {}

    def fake_request(method, url, **kwargs):
        captured['method'] = method
        captured['url'] = url
        captured['json'] = kwargs.get('json')
        return FakeSpeechResponse(_fake_mp3())

    monkeypatch.setattr(podcast_module, 'request_with_retry', fake_request)

    output_path = tmp_path / PODCAST_FILENAME
    synthesize_podcast('Welcome to Professor OS. This is a test narration.', output_path)

    assert output_path.exists()
    assert output_path.read_bytes().startswith(b'ID3')
    assert captured['url'].endswith('/v1/audio/speech')
    assert captured['json']['model'] == 'gpt-4o-mini-tts'
    assert captured['json']['voice'] == 'alloy'
    assert captured['json']['response_format'] == 'mp3'
    assert 'instructions' in captured['json']


def test_podcast_ui_has_player_download_and_disclosure(tmp_path):
    page = tmp_path / 'index.html'
    page.write_text(
        '<html><head><style>body{font-family:Arial}</style></head><body>'
        '<div class="top-actions"><a class="pill" href="/">Home</a></div>'
        '<section class="window">Hero</section><div class="reader">Lesson</div>'
        '</body></html>',
        encoding='utf-8'
    )

    inject_podcast_ui(page, _metadata())
    inject_podcast_ui(page, _metadata())

    html = page.read_text(encoding='utf-8')
    assert html.count('id="professorOSPodcast"') == 1
    assert '<audio controls' in html
    assert 'podcast.mp3' in html
    assert 'download=' in html
    assert 'Download podcast' in html
    assert 'AI-generated narration' in html
    assert 'href="#professorOSPodcast"' in html


def test_complete_podcast_package_validates(tmp_path):
    (tmp_path / PODCAST_FILENAME).write_bytes(_fake_mp3())
    (tmp_path / PODCAST_META_FILENAME).write_text(
        json.dumps(_metadata()),
        encoding='utf-8'
    )
    page = tmp_path / 'index.html'
    page.write_text(
        '<html><head><style></style></head><body>'
        '<div class="top-actions"></div><div class="reader"></div>'
        '</body></html>',
        encoding='utf-8'
    )
    inject_podcast_ui(page, _metadata())

    assert validate_podcast_package(tmp_path) == []


def test_missing_podcast_is_rejected_by_podcast_validator(tmp_path):
    errors = validate_podcast_package(tmp_path)
    assert errors
    assert any('podcast audio is missing' in error.lower() for error in errors)
