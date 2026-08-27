from teacher_agent.pipeline import RoboticsTeacherAgent


def _report(overall, blockers, technical, code_alignment, consistency, weak_other=90):
    dims = {
        'technical_accuracy': technical,
        'pedagogy': weak_other,
        'clarity': weak_other,
        'depth': weak_other,
        'examples': weak_other,
        'interactivity': weak_other,
        'code_alignment': code_alignment,
        'visual_teaching_plan': weak_other,
        'originality': weak_other,
        'consistency': consistency,
        'accessibility': weak_other,
    }
    return {
        'static': {'passed': True, 'warnings': []},
        'ai': {
            'overall_score': overall,
            'blocking_issues': list(blockers),
            'dimensions': dims,
        },
    }


def test_quality_rank_rejects_catastrophic_rewrite(monkeypatch):
    agent = object.__new__(RoboticsTeacherAgent)
    monkeypatch.setattr(
        'teacher_agent.pipeline.settings.premium_quality_min_dimension',
        80
    )

    good = _report(82, ['visual provenance mismatch'], 86, 84, 82)
    bad = _report(
        57,
        ['route wrong', 'map wrong', 'barrier wrong', 'provenance wrong'],
        48,
        53,
        58,
        weak_other=72,
    )

    assert agent._quality_rank(good) > agent._quality_rank(bad)
    assert not agent._better_quality(bad, good)
