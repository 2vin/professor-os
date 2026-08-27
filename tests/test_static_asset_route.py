from teacher_agent import dashboard


def test_static_asset_helper_is_scoped_to_teacher_static(tmp_path, monkeypatch):
    static_dir = tmp_path / 'teacher_agent' / 'static'
    static_dir.mkdir(parents=True)
    asset = static_dir / 'professor-core-wireframe.png'
    asset.write_bytes(b'png')

    monkeypatch.setattr(dashboard, '_PROJECT_ROOT', tmp_path)

    assert dashboard._safe_static_asset(
        'professor-core-wireframe.png'
    ) == asset.resolve()

    assert dashboard._safe_static_asset(
        '../config.py'
    ) is None
