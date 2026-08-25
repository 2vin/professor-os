import requests

from teacher_agent import http_utils


class DummyResponse(object):
    def __init__(self, status_code=200):
        self.status_code = status_code
        self.headers = {}


def test_connection_failure_is_retried(monkeypatch):
    calls = {'count': 0}

    def fake_request(*args, **kwargs):
        calls['count'] += 1
        if calls['count'] < 3:
            raise requests.ConnectionError('temporary dns failure')
        return DummyResponse(200)

    monkeypatch.setattr(http_utils.requests, 'request', fake_request)
    monkeypatch.setattr(http_utils.time, 'sleep', lambda _: None)
    monkeypatch.setattr(http_utils.monitor, 'retry', lambda *args, **kwargs: None)
    response = http_utils.request_with_retry('GET', 'https://example.test', max_attempts=3, base_delay=0.01)
    assert response.status_code == 200
    assert calls['count'] == 3


def test_retryable_http_status_is_retried(monkeypatch):
    statuses = [503, 200]
    monkeypatch.setattr(http_utils.requests, 'request', lambda *a, **k: DummyResponse(statuses.pop(0)))
    monkeypatch.setattr(http_utils.time, 'sleep', lambda _: None)
    monkeypatch.setattr(http_utils.monitor, 'retry', lambda *args, **kwargs: None)
    response = http_utils.request_with_retry('GET', 'https://example.test', max_attempts=2, base_delay=0.01)
    assert response.status_code == 200
