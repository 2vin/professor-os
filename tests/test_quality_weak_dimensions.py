from teacher_agent.quality import weak_dimensions


def test_weak_dimensions_detect_visual_score(monkeypatch):
    from teacher_agent import quality
    monkeypatch.setattr(quality.settings, 'premium_quality_min_dimension', 80)
    result = weak_dimensions({'dimensions': {'technical_accuracy': 94, 'visual_teaching_plan': 74, 'clarity': 90}})
    assert result == [{'name': 'visual_teaching_plan', 'score': 74, 'required': 80}]
