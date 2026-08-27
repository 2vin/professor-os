from teacher_agent import pipeline
from teacher_agent.pipeline import RoboticsTeacherAgent
from teacher_agent.quality import combined_quality_report


class FakeWriter(object):
    def __init__(self):
        self.calls = 0

    def surgical_premium_quality(
            self,
            markdown,
            review_json,
            static_report_json,
            visual_context=None):
        self.calls += 1
        return markdown + '\n\nsurgical-{0}\n'.format(self.calls)


def _static():
    return {
        'passed': True,
        'word_count': 2780,
        'code_blocks': 1,
        'errors': [],
        'warnings': [],
    }


def _ai(score, clarity, originality, blockers):
    dimensions = dict((name, 88) for name in [
        'technical_accuracy',
        'pedagogy',
        'clarity',
        'depth',
        'examples',
        'interactivity',
        'code_alignment',
        'visual_teaching_plan',
        'originality',
        'consistency',
        'accessibility',
    ])
    dimensions['clarity'] = clarity
    dimensions['originality'] = originality
    return {
        'overall_score': score,
        'dimensions': dimensions,
        'blocking_issues': blockers,
        'improvement_notes': [],
    }


def _agent():
    agent = object.__new__(RoboticsTeacherAgent)
    agent.writer = FakeWriter()
    return agent


def test_surgical_repair_can_take_near_pass_over_threshold(monkeypatch):
    agent = _agent()

    initial_ai = _ai(
        84,
        79,
        78,
        ['automatic door ambiguity', 'feedback ambiguity']
    )
    passing_ai = _ai(91, 89, 87, [])

    initial_report = combined_quality_report(_static(), initial_ai, 6)

    monkeypatch.setattr(
        agent,
        '_review',
        lambda markdown, lesson, visual_context=None: (_static(), passing_ai)
    )
    monkeypatch.setattr(pipeline, 'validate_lesson', lambda markdown: [])
    monkeypatch.setattr(pipeline.monitor, 'event', lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline.monitor, 'quality', lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline.settings, 'premium_quality_min_score', 88)
    monkeypatch.setattr(pipeline.settings, 'premium_quality_min_dimension', 80)

    markdown, ai, report, rounds = agent._surgical_quality_repair(
        '# lesson',
        {'class_no': 1, 'title': 'What Is a Robot?'},
        initial_report,
        max_rounds=2
    )

    assert rounds == 1
    assert agent.writer.calls == 1
    assert report['passed']
    assert ai['overall_score'] == 91
    assert 'surgical-1' in markdown


def test_surgical_repair_discards_regression(monkeypatch):
    agent = _agent()

    initial_ai = _ai(84, 79, 78, ['one blocker'])
    worse_ai = _ai(70, 70, 70, ['one blocker', 'new blocker'])

    initial_report = combined_quality_report(_static(), initial_ai, 6)

    monkeypatch.setattr(
        agent,
        '_review',
        lambda markdown, lesson, visual_context=None: (_static(), worse_ai)
    )
    monkeypatch.setattr(pipeline, 'validate_lesson', lambda markdown: [])
    monkeypatch.setattr(pipeline.monitor, 'event', lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline.monitor, 'quality', lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline.settings, 'premium_quality_min_score', 88)
    monkeypatch.setattr(pipeline.settings, 'premium_quality_min_dimension', 80)

    markdown, ai, report, rounds = agent._surgical_quality_repair(
        '# best lesson',
        {'class_no': 1, 'title': 'What Is a Robot?'},
        initial_report,
        max_rounds=1
    )

    assert rounds == 1
    assert markdown == '# best lesson'
    assert ai['overall_score'] == 84
    assert report['ai']['overall_score'] == 84
