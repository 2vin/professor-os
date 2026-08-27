from pathlib import Path


def _home():
    return Path(
        'teacher_agent/templates/student_site.html'
    ).read_text(encoding='utf-8')


def test_point_cloud_professor_replaces_wireframe_figure():
    text = _home()

    assert 'Point Cloud Professor / Live Teaching Render' in text
    assert 'Interactive point-cloud Professor OS teaching figure' in text
    assert 'Volumetric point field · adaptive detail' in text
    assert 'function addEllipsoid' in text
    assert 'function addCylinder' in text
    assert 'rendered.sort(function(a,b){return a.z-b.z})' in text
    assert '/* Glasses: sparse, bright and precise. */' in text


def test_professor_interaction_has_parallax_drag_inertia_and_pulse():
    text = _home()

    assert "c.addEventListener('pointermove',move)" in text
    assert "c.addEventListener('dblclick',function(){burst=1})" in text
    assert 'velYaw' in text
    assert 'targetYaw=-.10+nx*.38' in text
    assert "latestState&&latestState.status==='running'" in text
    assert 'prefers-reduced-motion: reduce' in text
