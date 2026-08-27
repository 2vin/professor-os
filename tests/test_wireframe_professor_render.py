from pathlib import Path


def _template():
    return Path(
        'teacher_agent/templates/student_site.html'
    ).read_text(encoding='utf-8')


def test_front_page_uses_wireframe_professor_render():
    text = _template()

    assert '3D Professor Core / Neural Wireframe' in text
    assert '/static/professor-core-wireframe.png' in text
    assert 'professor-wireframe-figure' in text
    assert 'Professor OS monochrome wireframe face render' in text
    assert 'professor-reticle' in text
    assert 'professor-scan' in text


def test_wireframe_render_is_interactive_and_live_state_aware():
    text = _template()

    assert "wrap.addEventListener('pointermove',move)" in text
    assert "img.style.setProperty('--render-ry'" in text
    assert "img.style.setProperty('--render-rx'" in text
    assert "stage.classList.toggle('is-live'" in text
    assert 'prefers-reduced-motion: reduce' in text
