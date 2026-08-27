from teacher_agent import dashboard


def _cached_preview(lecture):
    return {
        'slug': '001-intro-to-robotics',
        'preview_dir': 'preview/001-intro-to-robotics',
        'preview_available': True,
        'page_available': True,
        'diagram_available': True,
        'hero_available': True,
        'podcast_available': True,
        'code_count': 1,
        'category': 'Foundations',
        'summary': 'Cached old class.',
        'reading_minutes': 10,
        'lesson_url': '/lessons/001-intro-to-robotics/',
        'diagram_url': '/lessons/001-intro-to-robotics/diagram.png',
        'hero_url': '/lessons/001-intro-to-robotics/hero.png',
        'podcast_url': '/lessons/001-intro-to-robotics/podcast.mp3',
        'code_urls': [{'name': 'lab_01.py', 'url': '/lessons/001-intro-to-robotics/code/lab_01.py'}],
    }


def test_reset_to_zero_hides_cached_lessons(monkeypatch):
    monkeypatch.setattr(
        dashboard,
        '_load_curriculum',
        lambda: [{'class_no': 1, 'title': 'Intro to Robotics', 'concepts': 'robot'}]
    )
    monkeypatch.setattr(
        dashboard,
        'load_progress',
        lambda: {'last_generated_class': 0, 'last_published_class': 0}
    )
    monkeypatch.setattr(dashboard, '_lecture_preview', _cached_preview)
    monkeypatch.setattr(dashboard.monitor, 'snapshot', lambda: {'status': 'idle'})

    data = dashboard._state_payload()
    lecture = data['lectures'][0]
    assert lecture['status'] == 'next'
    assert lecture['lesson_url'] is None
    assert lecture['podcast_url'] is None
    assert lecture['code_urls'] == []
    assert lecture['cached_package_present'] is True
    assert data['integrity']['published_count'] == 0


def test_new_progress_namespace_resets_browser_progress():
    assert dashboard.STUDENT_PROGRESS_KEY == 'professorOSStudentProgressV2'
