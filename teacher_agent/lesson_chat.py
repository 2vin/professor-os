"""Professor OS server-chat compatibility module.

Student tutoring is intentionally performed in the browser with an open,
on-device Qwen model. This module contains only deterministic helpers retained
for backward compatibility. It never calls an external LLM service.
"""

import re


def _normalize_heading(text):
    return re.sub(r'\s+', ' ', str(text or '').strip()).lower()


def extract_chapter(markdown, section_title):
    wanted = _normalize_heading(section_title)
    if not wanted:
        return ''

    lines = str(markdown or '').splitlines()
    start = None
    for index, line in enumerate(lines):
        match = re.match(r'^##\s+(.+?)\s*$', line.strip())
        if match and _normalize_heading(match.group(1)) == wanted:
            start = index
            break

    if start is None:
        return ''

    end = len(lines)
    for index in range(start + 1, len(lines)):
        if re.match(r'^##\s+.+', lines[index].strip()):
            end = index
            break
    return '\n'.join(lines[start:end]).strip()


def sanitize_history(history, max_turns=4, max_chars=800):
    clean = []
    if not isinstance(history, list):
        return clean
    max_items = max(0, int(max_turns)) * 2
    for item in history[-max_items:]:
        if not isinstance(item, dict):
            continue
        role = str(item.get('role') or '').strip().lower()
        if role not in ('user', 'assistant'):
            continue
        text = str(item.get('text') or '').strip()
        if not text:
            continue
        clean.append({
            'role': role,
            'text': text[:max_chars],
        })
    return clean


def allow_chat_request(client_key, now=None):
    # Server inference is intentionally disabled. This helper is retained only
    # so older imports/tests do not become an accidental route to a paid API.
    return False, 0


def reset_chat_rate_limits():
    return None


class LessonChatTutor(object):
    def __init__(self):
        raise RuntimeError(
            'Server-side lesson LLM inference is disabled. '
            'Professor OS Tutor runs Qwen locally in the browser.'
        )
