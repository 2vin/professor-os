from teacher_agent.article_renderer import markdown_to_html, render_premium_article


def test_display_math_is_rendered_as_visible_math_block():
    markdown = (
        '## Math Without Fear\n\n'
        '\\[\n'
        '(1)(0.60\\ \\text{m/s})(2.0\\ \\text{s}) = 1.2\\ \\text{m}\n'
        '\\]\n'
    )
    rendered = markdown_to_html(markdown)
    assert 'class="math-block"' in rendered
    assert '\\text{m/s}' in rendered
    assert '1.2' in rendered


def test_inline_math_survives_for_mathjax():
    rendered = markdown_to_html(
        'The result is \\(d = vt\\) and the distance is \\(4.8\\ \\text{m}\\).'
    )
    assert '\\(d = vt\\)' in rendered
    assert '\\text{m}' in rendered


def test_markdown_table_becomes_real_html_table():
    rendered = markdown_to_html(
        '| Mode | Position |\n'
        '|---|---:|\n'
        '| Teleoperated | \\(1.2\\ \\text{m}\\) |\n'
        '| Autonomous | \\(3.6\\ \\text{m}\\) |\n'
    )
    assert '<table>' in rendered
    assert '<th>Mode</th>' in rendered
    assert 'Teleoperated' in rendered
    assert '\\(3.6\\ \\text{m}\\)' in rendered


def test_article_loads_mathjax_and_uses_fresh_student_progress_key(tmp_path):
    target = tmp_path / 'index.html'
    render_premium_article(
        '# Class 1: Intro\n\n## Math Without Fear\n\n\\[\nd = vt\n\\]',
        {'class_no': 1, 'title': 'Intro', 'concepts': 'robot, motion'},
        target
    )
    page = target.read_text(encoding='utf-8')
    assert 'mathjax@3/es5/tex-svg.js' in page
    assert 'window.MathJax' in page
    assert 'professorOSStudentProgressV2' in page
    assert 'class="math-block"' in page
