import json

from teacher_agent import pipeline
from teacher_agent.pipeline import RoboticsTeacherAgent
from teacher_agent.prompts import final_convergence_prompt, lesson_prompt
from teacher_agent.quality import combined_quality_report


class FakeWriter(object):
    def __init__(self):
        self.calls = 0
        self.static_reports = []

    def converge_premium_quality(
            self,
            markdown,
            review_json,
            static_report_json,
            visual_context=None):
        self.calls += 1
        self.static_reports.append(json.loads(static_report_json))
        return markdown + '\n\nconvergence-{0}\n'.format(self.calls)


def _static(words=2800, warnings=None):
    return {
        'passed': True,
        'word_count': words,
        'code_blocks': 1,
        'errors': [],
        'warnings': list(warnings or []),
    }


def _ai(score, originality=90, blockers=None):
    dimensions = dict((name, 90) for name in [
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
    dimensions['originality'] = originality

    return {
        'overall_score': score,
        'dimensions': dimensions,
        'blocking_issues': list(blockers or []),
        'improvement_notes': [],
        'linkedin': {
            'title': '',
            'description': '',
            'commentary': '',
            'thumbnail_alt_text': '',
        },
        'media_query': '',
        'image_query': '',
        'youtube_query': '',
        'media_style': 'none',
        'media_insert_after_heading': '## Real Robot Connection',
        'media_reason': '',
        'media_would_help': False,
    }


def _agent():
    agent = object.__new__(RoboticsTeacherAgent)
    agent.writer = FakeWriter()
    return agent


def test_convergence_can_rescue_exhausted_editorial_gate(monkeypatch):
    agent = _agent()

    failing_static = _static(
        words=6009,
        warnings=['Lesson is long at 6009 words; consider tightening for reading flow.']
    )
    failing_ai = _ai(
        86,
        originality=79,
        blockers=['Taxonomy remains ambiguous.']
    )
    passing_static = _static(words=2900)
    passing_ai = _ai(91, originality=88)

    reviews = [
        (passing_static, passing_ai),
    ]

    def fake_review(markdown, lesson, visual_context=None):
        return reviews.pop(0)

    monkeypatch.setattr(agent, '_review', fake_review)
    monkeypatch.setattr(pipeline, 'validate_lesson', lambda markdown: [])
    monkeypatch.setattr(pipeline.monitor, 'event', lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline.monitor, 'quality', lambda *args, **kwargs: None)
    monkeypatch.setattr(pipeline.settings, 'premium_quality_min_score', 88)
    monkeypatch.setattr(pipeline.settings, 'premium_quality_min_dimension', 80)

    last_report = combined_quality_report(
        failing_static,
        failing_ai,
        rounds_used=5
    )

    markdown, ai_review, report, rounds = agent._quality_convergence(
        '# lesson',
        {'class_no': 1, 'title': 'What Is a Robot?'},
        last_report,
        visual_context=None,
        prior_rounds=5,
        context_label='Pre-media editorial',
        max_rounds=2,
    )

    assert rounds == 1
    assert agent.writer.calls == 1
    assert report['passed']
    assert ai_review['overall_score'] == 91
    assert 'convergence-1' in markdown

    # The convergence writer must see deterministic warnings such as excessive length.
    assert agent.writer.static_reports[0]['word_count'] == 6009
    assert agent.writer.static_reports[0]['warnings']


def test_convergence_prompt_demands_root_cause_fix_and_concision():
    prompt = final_convergence_prompt(
        '# lesson',
        '{"overall_score": 86, "blocking_issues": ["ambiguous taxonomy"]}',
        '{"word_count": 6009, "warnings": ["too long"]}',
        None
    )

    assert 'Resolve the underlying cause' in prompt
    assert '2,200-3,200 words' in prompt
    assert 'common robotics/control terminology' not in prompt or 'standard engineering taxonomy' in prompt
    assert 'Do not call a trigger sensor feedback' in prompt
    assert '6009' in prompt


def test_initial_lesson_prompt_prevents_definition_drift():
    prompt = lesson_prompt(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
            'concepts': 'robot, automation, feedback, autonomy',
        },
        None,
        'Robot Parts'
    )

    assert 'common robotics/control terminology' in prompt
    assert 'sensor-triggered sequence closed-loop feedback' in prompt
    assert '2,200-3,000 words' in prompt
    assert 'verify all claimed outputs' in prompt
