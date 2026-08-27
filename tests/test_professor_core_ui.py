from pathlib import Path


def _home_template():
    return Path(
        'teacher_agent/templates/student_site.html'
    ).read_text(encoding='utf-8')


def test_home_uses_interactive_professor_core():
    text = _home_template()

    assert '3D Professor Core / Live Teaching Render' in text
    assert 'Interactive 3D Professor OS teaching figure' in text
    assert 'id="professorCore"' in text
    assert 'Drag to inspect' in text

    # Professor-specific geometry and interaction, not the older abstract
    # knowledge-orb renderer.
    assert "label('PEDAGOGY'" in text
    assert "label('ROBOTICS'" in text
    assert '/* Glasses – the defining professor cue. */' in text
    assert "c.addEventListener('pointerdown',down)" in text
    assert "c.addEventListener('dblclick'" in text


def test_professor_core_preserves_runtime_state_feedback():
    text = _home_template()

    assert "running?'Teaching mode':'Interactive professor'" in text
    assert "latestState&&latestState.status==='running'" in text
    assert 'prefers-reduced-motion: reduce' in text
    assert "c.setAttribute('tabindex','0')" in text
