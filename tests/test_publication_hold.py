from teacher_agent.runtime import RuntimeMonitor


def test_publication_hold_is_not_runtime_crash(tmp_path, monkeypatch):
    import teacher_agent.runtime as runtime
    monkeypatch.setattr(runtime, 'STATE_PATH', tmp_path / 'state.json')
    monkeypatch.setattr(runtime, 'LOG_PATH', tmp_path / 'agent.log')
    monitor = RuntimeMonitor()
    monitor.reset_run('abc', 1, 'Control', 10, 'preview', [('editorial', 'Editorial')])
    monitor.hold('Technical review requires correction.', attempts=3)
    state = monitor.snapshot()
    assert state['status'] == 'blocked'
    assert state['last_error'] is None
    assert state['publication_hold']['active'] is True
    assert state['publication_hold']['attempts'] == 3
