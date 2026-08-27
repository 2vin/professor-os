from teacher_agent.article_renderer import render_premium_article


def _lesson():
    return {
        'class_no': 1,
        'title': 'What Is a Robot?',
        'concepts': 'robot, autonomy, feedback',
    }


def test_every_major_chapter_has_ask_professor_button(tmp_path):
    page = tmp_path / 'index.html'
    render_premium_article(
        '# Class 1: What Is a Robot?\n\n'
        '## The Big Idea\n\nA robot is a physical machine.\n\n'
        '## Python Lab\n\nRun a small simulation.',
        _lesson(),
        page
    )
    text = page.read_text(encoding='utf-8')

    assert text.count('data-professor-chat-section=') == 2
    assert 'Professor OS Tutor' in text
    assert '✦ Ask Professor' in text


def test_tutor_is_on_device_qwen_with_no_chat_api(tmp_path):
    page = tmp_path / 'index.html'
    render_premium_article(
        '# Class 1: What Is a Robot?\n\n'
        '## The Big Idea\n\nA robot is a physical machine.',
        _lesson(),
        page
    )
    text = page.read_text(encoding='utf-8')

    assert 'onnx-community/Qwen3-0.6B-ONNX' in text
    assert '@huggingface/transformers@4.2.0' in text
    assert '/api/lesson-chat' not in text
    assert 'no API key' in text
    assert 'Questions stay on your device during inference' in text


def test_tutor_has_local_scope_and_safety_guards(tmp_path):
    page = tmp_path / 'index.html'
    render_premium_article(
        '# Class 1: Intro\n\n## Core Concept\n\nLearn safe robotics.',
        {'class_no': 1, 'title': 'Intro', 'concepts': 'robot, safety'},
        page
    )
    text = page.read_text(encoding='utf-8')
    assert '[OFF_TOPIC]' in text
    assert '[SAFETY]' in text
    assert 'bypass' in text
    assert 'system prompt' in text
