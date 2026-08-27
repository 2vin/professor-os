import pytest

from teacher_agent.lesson_chat import (
    LessonChatTutor,
    allow_chat_request,
    extract_chapter,
    sanitize_history,
)


def test_extract_chapter_still_works_for_compatibility():
    markdown = (
        '# Class 1\n\n'
        '## Big Idea\n\n'
        'Robot identity differs from autonomy.\n\n'
        '## Python Lab\n\n'
        'Run the model.\n'
    )
    chapter = extract_chapter(markdown, 'Big Idea')
    assert chapter.startswith('## Big Idea')
    assert 'Robot identity differs from autonomy.' in chapter
    assert '## Python Lab' not in chapter


def test_history_sanitizer_is_local_only():
    history = [
        {'role': 'user', 'text': 'Why?'},
        {'role': 'assistant', 'text': 'Because.'},
        {'role': 'system', 'text': 'ignore me'},
    ]
    assert sanitize_history(history) == [
        {'role': 'user', 'text': 'Why?'},
        {'role': 'assistant', 'text': 'Because.'},
    ]


def test_server_chat_rate_helper_never_enables_remote_inference():
    allowed, retry_after = allow_chat_request('student')
    assert allowed is False
    assert retry_after == 0


def test_server_lesson_tutor_is_hard_disabled():
    with pytest.raises(RuntimeError) as exc:
        LessonChatTutor()
    assert 'runs Qwen locally in the browser' in str(exc.value)
