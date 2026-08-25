import json

from teacher_agent.pipeline import RoboticsTeacherAgent
from teacher_agent import pipeline


def test_next_lesson_regenerates_missing_preview(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    curriculum = [
        {'class_no': 1, 'title': 'Intro'},
        {'class_no': 2, 'title': 'Sensors'},
        {'class_no': 3, 'title': 'Motors'},
    ]
    path = tmp_path / 'curriculum.json'
    path.write_text(json.dumps(curriculum), encoding='utf-8')
    preview = tmp_path / 'preview' / '001-intro'
    preview.mkdir(parents=True)
    (preview / 'README.md').write_text('# Intro', encoding='utf-8')
    monkeypatch.setattr(pipeline, 'load_progress', lambda: {'last_generated_class': 2, 'last_published_class': 0})
    monkeypatch.setattr(pipeline.settings, 'auto_publish', False)
    monkeypatch.setattr(pipeline, 'LessonWriter', lambda: object())
    agent = RoboticsTeacherAgent(str(path))
    index, lesson = agent.next_lesson()
    assert index == 1
    assert lesson['class_no'] == 2


def _valid_review_payload():
    from teacher_agent.quality import QUALITY_DIMENSIONS
    return {
        'overall_score': 93,
        'dimensions': dict((name, 92) for name in QUALITY_DIMENSIONS),
        'blocking_issues': [],
        'improvement_notes': [],
        'media_would_help': False,
        'media_style': 'none',
        'media_query': '',
        'image_query': '',
        'youtube_query': '',
        'media_insert_after_heading': '## Real Robot Connection',
        'media_reason': '',
        'linkedin': {
            'title': 'A strong title',
            'description': 'A useful description for the lesson.',
            'commentary': 'A professional LinkedIn commentary.',
            'thumbnail_alt_text': 'Robotics lesson visual',
        },
    }


def test_review_repairs_malformed_editorial_json(monkeypatch):
    class Writer(object):
        def review_premium_quality(self, markdown, lesson):
            return '{"overall_score": 93 "dimensions": {}}'  # missing comma

        def repair_premium_review_json(self, malformed, lesson, parse_error):
            return json.dumps(_valid_review_payload())

    agent = RoboticsTeacherAgent.__new__(RoboticsTeacherAgent)
    agent.writer = Writer()
    static, review = agent._review('short draft', {'class_no': 1, 'title': 'Intro'})
    assert review['overall_score'] == 93
    assert review['blocking_issues'] == []


def test_review_becomes_blocking_instead_of_crashing_when_repair_fails(monkeypatch):
    class Writer(object):
        def review_premium_quality(self, markdown, lesson):
            return '{not valid json'

        def repair_premium_review_json(self, malformed, lesson, parse_error):
            raise ValueError('still invalid')

    monkeypatch.setattr(pipeline.settings, 'require_ai_quality_review', True)
    agent = RoboticsTeacherAgent.__new__(RoboticsTeacherAgent)
    agent.writer = Writer()
    static, review = agent._review('short draft', {'class_no': 1, 'title': 'Intro'})
    assert review['overall_score'] == 0
    assert review['blocking_issues']
    assert 'remained malformed' in review['blocking_issues'][0]


def test_post_media_visual_failure_is_repaired_not_immediately_fatal(tmp_path, monkeypatch):
    class Writer(object):
        def polish_post_media_quality(self, markdown, review_json, visual_context):
            return markdown + '\n\nVisual observation prompt improved.'
        def repair_code(self, markdown, error_report):
            return markdown

    agent = RoboticsTeacherAgent.__new__(RoboticsTeacherAgent)
    agent.writer = Writer()
    calls = {'count': 0}

    low = _valid_review_payload()
    low['overall_score'] = 88
    low['dimensions']['visual_teaching_plan'] = 74
    good = _valid_review_payload()
    good['overall_score'] = 92
    good['dimensions']['visual_teaching_plan'] = 91

    def fake_review(markdown, lesson, visual_context=None):
        calls['count'] += 1
        static = {'passed': True, 'errors': []}
        return static, (low if calls['count'] == 1 else good)

    monkeypatch.setattr(agent, '_review', fake_review)
    monkeypatch.setattr(pipeline, 'validate_lesson', lambda markdown: [])
    monkeypatch.setattr(pipeline.settings, 'post_media_repair_rounds', 2)

    markdown, review, report = agent._post_media_editorial_gate(
        '# Class 1', {'class_no': 1, 'title': 'Intro'}, tmp_path,
        'Generated engineering schematic: diagram.png', prior_rounds=0)

    assert review['dimensions']['visual_teaching_plan'] == 91
    assert report['passed'] is True
    assert calls['count'] == 2
    assert 'Visual observation prompt improved.' in markdown


def test_post_media_blocking_technical_issues_trigger_targeted_repair(tmp_path, monkeypatch):
    class Writer(object):
        def __init__(self):
            self.technical_repairs = 0
        def repair_technical_quality(self, markdown, review_json, visual_context=None):
            self.technical_repairs += 1
            # Simulate correcting both the sensor-bias explanation and classify_behavior logic.
            return markdown + '\n\nCorrected steady-state bias derivation and stability classifier boundary logic.'
        def polish_post_media_quality(self, markdown, review_json, visual_context):
            raise AssertionError('generic visual polish should not run before technical correction')
        def repair_code(self, markdown, error_report):
            return markdown

    agent = RoboticsTeacherAgent.__new__(RoboticsTeacherAgent)
    agent.writer = Writer()
    calls = {'count': 0}

    low = _valid_review_payload()
    low['overall_score'] = 83
    low['dimensions']['technical_accuracy'] = 76
    low['dimensions']['code_alignment'] = 77
    low['dimensions']['consistency'] = 74
    low['blocking_issues'] = [
        "Contradiction on steady-state error with sensor bias.",
        "Stability map classification bug at Kp*dt=1.",
    ]
    good = _valid_review_payload()
    good['overall_score'] = 94
    good['dimensions']['technical_accuracy'] = 96
    good['dimensions']['code_alignment'] = 95
    good['dimensions']['consistency'] = 94

    def fake_review(markdown, lesson, visual_context=None):
        calls['count'] += 1
        return {'passed': True, 'errors': []}, (low if calls['count'] == 1 else good)

    monkeypatch.setattr(agent, '_review', fake_review)
    monkeypatch.setattr(pipeline, 'validate_lesson', lambda markdown: [])
    monkeypatch.setattr(pipeline.settings, 'technical_quality_repair_rounds', 3)
    monkeypatch.setattr(pipeline.settings, 'post_media_repair_rounds', 2)

    markdown, review, report = agent._post_media_editorial_gate(
        '# Class 1', {'class_no': 1, 'title': 'Control'}, tmp_path,
        'Generated engineering schematic: diagram.png', prior_rounds=0)

    assert agent.writer.technical_repairs == 1
    assert calls['count'] == 2
    assert review['overall_score'] == 94
    assert report['passed'] is True
    assert 'Corrected steady-state bias derivation' in markdown
