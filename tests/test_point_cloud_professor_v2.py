from pathlib import Path


def _home():
    return Path(
        'teacher_agent/templates/student_site.html'
    ).read_text(encoding='utf-8')


def test_current_professor_visual_is_neural_wireframe_render():
    text = _home()

    # The older point-cloud implementation was intentionally replaced by the
    # reference-matched monochrome neural-wireframe professor face.
    assert '3D Professor Core / Neural Wireframe' in text
    assert '/static/professor-core-wireframe.png' in text
    assert 'professor-wireframe-figure' in text
    assert 'Professor OS monochrome wireframe face render' in text
    assert 'professor-crosshair' in text
    assert 'professor-reticle' in text
    assert 'professor-scan' in text


def test_current_professor_interaction_has_subtle_parallax_and_live_feedback():
    text = _home()

    assert "wrap.addEventListener('pointermove',move)" in text
    assert "wrap.addEventListener('pointerleave',leave)" in text
    assert "img.style.setProperty('--render-x'" in text
    assert "img.style.setProperty('--render-y'" in text
    assert "img.style.setProperty('--render-ry'" in text
    assert "img.style.setProperty('--render-rx'" in text
    assert "stage.classList.toggle('is-live'" in text
    assert "latestState&&latestState.status==='running'" in text
    assert 'prefers-reduced-motion: reduce' in text
