from teacher_agent.config import settings
from teacher_agent.publication_gate import _check_media


def test_recommended_external_media_is_optional_by_default(monkeypatch):
    monkeypatch.setattr(settings, 'require_recommended_media', False)

    errors, warnings = _check_media({
        'recommended': True,
        'used': False,
        'items': [],
    })

    assert errors == []
    assert any(
        'recommended real-world media' in warning.lower()
        and 'none passed selection' in warning.lower()
        for warning in warnings
    )


def test_recommended_external_media_can_still_be_made_strict(monkeypatch):
    monkeypatch.setattr(settings, 'require_recommended_media', True)

    errors, warnings = _check_media({
        'recommended': True,
        'used': False,
        'items': [],
    })

    assert warnings == []
    assert any(
        'recommended real-world media' in error.lower()
        and 'no legally verified image/video passed selection' in error.lower()
        for error in errors
    )
