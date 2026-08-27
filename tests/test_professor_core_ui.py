from pathlib import Path


def _home_template():
    return Path(
        'teacher_agent/templates/student_site.html'
    ).read_text(encoding='utf-8')


def test_home_uses_accessible_interactive_professor_core():
    text = _home_template()

    assert 'id="professorCore"' in text
    assert '3D Professor Core / Neural Wireframe' in text
    assert 'Interactive monochrome wireframe Professor OS face' in text
    assert 'Move to inspect' in text

    # The current visual deliberately uses an image-led neural mesh rather than
    # the older hand-drawn Canvas professor geometry.
    assert 'professor-wireframe-figure' in text
    assert 'professor-depth-particles' in text
    assert 'professor-axis-tick' in text
    assert 'PROFESSOR.OS' in text
    assert 'LIVE RENDER' in text


def test_professor_core_preserves_runtime_and_motion_accessibility():
    text = _home_template()

    assert "running?'Teaching mode':'Interactive professor'" in text
    assert "latestState&&latestState.status==='running'" in text
    assert "stage.classList.toggle('is-live'" in text
    assert 'prefers-reduced-motion: reduce' in text

    # The current interaction is on the containing render surface instead of
    # keyboard-driving the old raw Canvas mesh.
    assert "wrap.addEventListener('pointermove',move)" in text
    assert "wrap.addEventListener('pointerleave',leave)" in text
