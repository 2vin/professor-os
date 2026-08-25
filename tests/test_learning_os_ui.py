from pathlib import Path

from teacher_agent import dashboard
from teacher_agent.article_renderer import render_premium_article


def test_home_is_learning_os_shell():
    path = Path(dashboard.__file__).parent / 'templates' / 'student_site.html'
    text = path.read_text(encoding='utf-8')
    assert 'Learning Operating System' in text
    assert 'class="os-topbar"' in text
    assert 'class="os-dock"' in text
    assert 'id="commandOverlay"' in text
    assert 'id="notificationPanel"' in text
    assert 'id="osCanvas"' in text
    for app in ('home', 'learn', 'library', 'tonight', 'system'):
        assert 'id="app-{0}"'.format(app) in text


def test_lesson_uses_reader_app_shell(tmp_path):
    target = tmp_path / 'index.html'
    render_premium_article(
        '# Class 1: Intro\n\n## Big Idea\n\nLearn robots.',
        {'class_no': 1, 'title': 'Intro', 'concepts': 'robot, autonomy'},
        target,
        navigation={'next': {'class_no': 2, 'title': 'Next', 'url': None}})
    text = target.read_text(encoding='utf-8')
    assert 'Reader application' in text
    assert 'class="dock"' in text
    assert 'id="lessonContent"' in text
    assert 'id="toc"' in text
    assert 'Reading progress' in text


def test_runtime_identifies_v18_1():
    data = dashboard._state_payload()
    assert data['brand']['version'] == '18.1'
    assert dashboard.DashboardHandler.server_version == 'ProfessorOS/18.1'
