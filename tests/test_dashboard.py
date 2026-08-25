from teacher_agent.dashboard import _state_payload


def test_dashboard_state_payload_has_course_memory():
    data = _state_payload()
    assert 'course_memory' in data
    assert 'status' in data



def test_dashboard_marks_missing_generated(monkeypatch):
    from teacher_agent import dashboard
    monkeypatch.setattr(dashboard, '_load_curriculum', lambda: [{'class_no': 1, 'title': 'Intro to Robotics'}])
    monkeypatch.setattr(dashboard, 'load_progress', lambda: {'last_generated_class': 1, 'last_published_class': 0})
    monkeypatch.setattr(dashboard, '_lecture_preview', lambda lecture: {
        'slug': '001-intro-to-robotics',
        'preview_dir': 'preview/001-intro-to-robotics',
        'preview_available': False,
        'diagram_available': False,
        'code_count': 0,
        'lesson_url': None,
        'diagram_url': None,
        'code_urls': [],
    })
    monkeypatch.setattr(dashboard.monitor, 'snapshot', lambda: {'status': 'idle'})
    data = dashboard._state_payload()
    assert data['lectures'][0]['status'] == 'missing'
    assert data['integrity']['missing_count'] == 1
