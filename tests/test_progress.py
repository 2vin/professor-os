import json

from teacher_agent import progress


def test_progress_separates_preview_and_publish(tmp_path, monkeypatch):
    monkeypatch.setattr(progress, 'LOCAL_PROGRESS', tmp_path / 'progress.json')
    progress.save_progress(2, published=False)
    data = progress.load_progress()
    assert data['last_generated_class'] == 2
    assert data['last_published_class'] == 0

    progress.save_progress(1, published=True)
    data = progress.load_progress()
    assert data['last_generated_class'] == 2
    assert data['last_published_class'] == 1


def test_progress_migrates_v1(tmp_path, monkeypatch):
    path = tmp_path / 'progress.json'
    path.write_text(json.dumps({'last_published_class': 4}), encoding='utf-8')
    monkeypatch.setattr(progress, 'LOCAL_PROGRESS', path)
    data = progress.load_progress()
    assert data['last_published_class'] == 4
    assert data['last_generated_class'] == 4
