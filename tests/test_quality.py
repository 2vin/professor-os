from teacher_agent import quality


def test_normalize_ai_review_and_thresholds(monkeypatch):
    review = quality.normalize_ai_review({
        'overall_score': 92,
        'dimensions': dict((name, 91) for name in quality.QUALITY_DIMENSIONS),
        'blocking_issues': [],
        'improvement_notes': [],
        'linkedin': {'title': 'T', 'description': 'D', 'commentary': 'C', 'thumbnail_alt_text': 'A'},
    })
    static = {'passed': True, 'errors': [], 'warnings': []}
    assert quality.premium_review_passes(static, review)


def test_quality_threshold_blocks_low_dimension():
    dims = dict((name, 92) for name in quality.QUALITY_DIMENSIONS)
    dims['technical_accuracy'] = 50
    review = {'overall_score': 92, 'dimensions': dims, 'blocking_issues': []}
    static = {'passed': True, 'errors': [], 'warnings': []}
    assert not quality.premium_review_passes(static, review)


def test_extract_json_object_from_fence():
    parsed = quality.extract_json_object('```json\n{"overall_score": 90}\n```')
    assert parsed['overall_score'] == 90


def test_extract_json_object_repairs_trailing_comma():
    parsed = quality.extract_json_object('{"overall_score": 90, "blocking_issues": [],}')
    assert parsed['overall_score'] == 90


def test_extract_json_object_uses_balanced_object_with_commentary():
    parsed = quality.extract_json_object('Review follows: {"overall_score": 91} Thank you')
    assert parsed['overall_score'] == 91


def test_failed_ai_review_is_blocking():
    review = quality.failed_ai_review('review parser failed')
    assert review['overall_score'] == 0
    assert review['blocking_issues'] == ['review parser failed']
