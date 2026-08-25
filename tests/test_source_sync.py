from teacher_agent import source_sync


def test_collect_source_files_excludes_secrets(tmp_path):
    (tmp_path / 'teacher_agent').mkdir()
    (tmp_path / 'teacher_agent' / 'a.py').write_text('print(1)', encoding='utf-8')
    (tmp_path / '.env').write_text('SECRET=1', encoding='utf-8')
    (tmp_path / '.env.example').write_text('SECRET=', encoding='utf-8')
    files = source_sync.collect_source_files(tmp_path)
    assert 'teacher_agent/a.py' in files
    assert '.env' not in files
    assert '.env.example' in files


def test_source_hash_changes_when_source_changes():
    a = source_sync.source_hash({'a.py': b'1'})
    b = source_sync.source_hash({'a.py': b'2'})
    assert a != b


def test_quality_gate_stops_on_failed_pytest(monkeypatch, tmp_path):
    class Result(object):
        returncode = 1
        stdout = 'failed test'
    monkeypatch.setattr(source_sync.subprocess, 'run', lambda *a, **k: Result())
    try:
        source_sync.run_quality_gate(tmp_path)
    except RuntimeError as exc:
        assert 'NOT pushed' in str(exc)
    else:
        assert False, 'Expected validation failure'
