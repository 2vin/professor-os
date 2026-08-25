from teacher_agent import source_sync


def test_sync_error_is_returned_without_marking_github_disconnected(monkeypatch, tmp_path):
    monkeypatch.setattr(source_sync.settings, 'auto_sync_source', True)
    monkeypatch.setattr(source_sync.settings, 'github_token', 'token')
    monkeypatch.setattr(source_sync.settings, 'github_owner', 'owner')
    monkeypatch.setattr(source_sync.settings, 'github_repo', 'repo')
    monkeypatch.setattr(source_sync, 'collect_source_files', lambda root=None: {'README.md': b'hello'})
    monkeypatch.setattr(source_sync, 'run_quality_gate', lambda root=None: {'tests': 'passed', 'compile': 'passed'})

    class BadSync(object):
        def sync_files(self, files, digest):
            raise RuntimeError('temporary GitHub failure')

    monkeypatch.setattr(source_sync, 'GitHubSourceSync', BadSync)
    states = []
    integrations = []
    monkeypatch.setattr(source_sync.monitor, 'source_sync', lambda status, message='', last_commit=None: states.append((status, message)))
    monkeypatch.setattr(source_sync.monitor, 'integration', lambda *args, **kwargs: integrations.append((args, kwargs)))
    monkeypatch.setattr(source_sync.monitor, 'event', lambda *args, **kwargs: None)

    result = source_sync.sync_source_once(tmp_path)
    assert result['reason'] == 'sync_error'
    assert states[-1][0] == 'error'
    assert integrations == []
