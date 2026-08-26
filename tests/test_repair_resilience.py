from teacher_agent import pipeline
from teacher_agent.pipeline import RoboticsTeacherAgent


class FakeWriter(object):
    def __init__(self):
        self.calls = 0

    def repair_code(self, markdown, error_report):
        self.calls += 1
        return markdown + '\nrepair-{0}'.format(self.calls)


def _agent():
    agent = object.__new__(RoboticsTeacherAgent)
    agent.writer = FakeWriter()
    return agent


def test_repair_until_valid_retries_until_third_round(monkeypatch):
    agent = _agent()
    outcomes = [
        ['Block 10: AssertionError'],
        ['Block 10: AssertionError'],
        [],
    ]

    def fake_validate(markdown):
        return outcomes.pop(0)

    monkeypatch.setattr(pipeline, 'validate_lesson', fake_validate)
    monkeypatch.setattr(pipeline.monitor, 'event', lambda *args, **kwargs: None)

    markdown, errors, attempts = agent._repair_until_valid(
        '# lesson',
        ['Block 10: AssertionError'],
        'Test-stage',
        max_attempts=3,
    )

    assert errors == []
    assert attempts == 3
    assert agent.writer.calls == 3
    assert 'repair-3' in markdown


def test_repair_until_valid_stops_early_when_fixed(monkeypatch):
    agent = _agent()
    outcomes = [
        [],
    ]

    monkeypatch.setattr(pipeline, 'validate_lesson', lambda markdown: outcomes.pop(0))
    monkeypatch.setattr(pipeline.monitor, 'event', lambda *args, **kwargs: None)

    markdown, errors, attempts = agent._repair_until_valid(
        '# lesson',
        ['runtime error'],
        'Test-stage',
        max_attempts=3,
    )

    assert errors == []
    assert attempts == 1
    assert agent.writer.calls == 1
    assert 'repair-1' in markdown


def test_repair_until_valid_returns_errors_after_limit(monkeypatch):
    agent = _agent()

    monkeypatch.setattr(
        pipeline,
        'validate_lesson',
        lambda markdown: ['Block 10: still failing'],
    )
    monkeypatch.setattr(pipeline.monitor, 'event', lambda *args, **kwargs: None)

    _, errors, attempts = agent._repair_until_valid(
        '# lesson',
        ['Block 10: AssertionError'],
        'Test-stage',
        max_attempts=3,
    )

    assert errors == ['Block 10: still failing']
    assert attempts == 3
    assert agent.writer.calls == 3
