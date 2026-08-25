from teacher_agent.article_renderer import markdown_to_html, render_premium_article


def test_markdown_renderer_handles_code_and_headings():
    rendered = markdown_to_html('# Title\n\n## Lab\n\n```python\nprint(1)\n```')
    assert '<h1>Title</h1>' in rendered
    assert 'print(1)' in rendered
    assert 'code-card' in rendered


def test_render_premium_article(tmp_path):
    target = tmp_path / 'article.html'
    render_premium_article('# Class 1: Intro\n\nA clear lesson.', {'class_no': 1, 'title': 'Intro', 'concepts': 'robot'}, target)
    text = target.read_text(encoding='utf-8')
    assert 'Professor OS' in text
    assert 'Built by Connect.Vin' in text


def test_youtube_marker_renders_responsive_embed(tmp_path):
    from teacher_agent.article_renderer import render_premium_article
    lesson = {'class_no': 1, 'title': 'Robot Video', 'concepts': 'robot, actuator'}
    markdown = '# Class 1: Robot Video\n\n<!-- PROFESSOR_OS_YOUTUBE:M7lc1UVf-VE -->\n\nWatch the real hardware.'
    out = tmp_path / 'article.html'
    render_premium_article(markdown, lesson, out)
    html = out.read_text(encoding='utf-8')
    assert 'https://www.youtube.com/embed/M7lc1UVf-VE' in html
    assert 'video-frame' in html
