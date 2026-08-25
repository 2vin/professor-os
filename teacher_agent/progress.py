import json
from pathlib import Path

LOCAL_PROGRESS = Path('.robotics_teacher_progress.json')


def _default_progress():
    return {
        'last_generated_class': 0,
        'last_published_class': 0,
    }


def load_progress():
    if not LOCAL_PROGRESS.exists():
        return _default_progress()
    try:
        data = json.loads(LOCAL_PROGRESS.read_text(encoding='utf-8'))
    except Exception:
        return _default_progress()

    result = _default_progress()
    # Migration from v1, which only had last_published_class.
    old_published = int(data.get('last_published_class', 0) or 0)
    result['last_published_class'] = old_published
    result['last_generated_class'] = int(data.get('last_generated_class', old_published) or 0)
    return result


def save_progress(class_no, published=False):
    data = load_progress()
    if published:
        data['last_published_class'] = max(data['last_published_class'], int(class_no))
    else:
        data['last_generated_class'] = max(data['last_generated_class'], int(class_no))
    LOCAL_PROGRESS.write_text(json.dumps(data, indent=2), encoding='utf-8')
