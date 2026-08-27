from pathlib import Path

from teacher_agent.pipeline import RoboticsTeacherAgent


def test_regeneration_starts_from_clean_lesson_directory(tmp_path):
    agent = object.__new__(RoboticsTeacherAgent)
    lesson_dir = tmp_path / 'preview' / '001-what-is-a-robot'
    code_dir = lesson_dir / 'code'
    code_dir.mkdir(parents=True)

    (lesson_dir / 'podcast.mp3').write_bytes(b'old podcast')
    (lesson_dir / 'inline_09.png').write_bytes(b'old image')
    (lesson_dir / 'FAILED_FINAL.md').write_text('old failure', encoding='utf-8')
    (code_dir / 'lab_09.py').write_text('print("stale")\n', encoding='utf-8')

    prepared = agent._prepare_lesson_output_dir(lesson_dir)

    assert prepared == lesson_dir
    assert prepared.exists()
    assert list(prepared.iterdir()) == []


class _FakeGitHub(object):
    def __init__(self):
        self.paths = []

    def put_bytes(self, path, data, message):
        self.paths.append(path)


def test_durable_lesson_mirror_includes_podcast_and_transcript(tmp_path):
    agent = object.__new__(RoboticsTeacherAgent)
    lesson_dir = tmp_path / 'lesson'
    lesson_dir.mkdir()

    (lesson_dir / 'README.md').write_text('# Lesson\n', encoding='utf-8')
    (lesson_dir / 'podcast.mp3').write_bytes(b'ID3' + (b'x' * 100))
    (lesson_dir / 'podcast_transcript.txt').write_text(
        'Professor OS podcast transcript.',
        encoding='utf-8'
    )

    github = _FakeGitHub()
    agent._upload_lesson_package(
        github,
        lesson_dir,
        '001-what-is-a-robot',
        1
    )

    assert 'lessons/001-what-is-a-robot/podcast.mp3' in github.paths
    assert 'lessons/001-what-is-a-robot/podcast_transcript.txt' in github.paths
