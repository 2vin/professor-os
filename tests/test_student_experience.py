from pathlib import Path

from teacher_agent import dashboard
from teacher_agent.article_renderer import render_premium_article


def test_category_mapping_covers_course_domains():
    assert dashboard._category_for_class(1) == 'Foundations'
    assert dashboard._category_for_class(25) == 'Computer Vision'
    assert dashboard._category_for_class(36) == 'Localization & Mapping'
    assert dashboard._category_for_class(60) == 'Safety & Capstone'


def test_article_has_learning_progress_and_toc(tmp_path):
    target = tmp_path / 'index.html'
    render_premium_article(
        '# Class 1: Intro\n\n## Big Idea\n\nLearn robots.\n\n## Python Lab\n\n```python\nprint(1)\n```',
        {'class_no': 1, 'title': 'Intro', 'concepts': 'robot, autonomy'},
        target,
        navigation={'next': {'class_no': 2, 'title': 'Next', 'url': None}})
    text = target.read_text(encoding='utf-8')
    assert 'professorOSStudentProgressV1' in text
    assert 'id="toc"' in text
    assert 'Mark class complete' in text
    assert 'Reading progress' in text
    assert 'Coming next' in text


def test_student_home_has_search_filters_progress_and_tonight():
    path = Path(dashboard.__file__).parent / 'templates' / 'student_site.html'
    text = path.read_text(encoding='utf-8')
    assert 'id="searchInput"' in text
    assert 'id="filters"' in text
    assert 'professorOSStudentProgressV1' in text
    assert "Tonight's upcoming lecture" in text
    assert 'mobile-nav' in text
