from teacher_agent.media_curator import append_generated_teaching_visual, media_review_context


def test_generated_teaching_visual_inserted_once():
    md = "# Class 1\n\n## See It in Your Head\nThink about the robot.\n\n## Real Robot Connection\nA real robot."
    lesson = {'class_no': 1, 'title': 'Robot Basics'}
    updated = append_generated_teaching_visual(md, lesson)
    assert '![Professor OS engineering schematic](diagram.png)' in updated
    assert 'How to read this visual' in updated
    again = append_generated_teaching_visual(updated, lesson)
    assert again.count('![Professor OS engineering schematic](diagram.png)') == 1


def test_media_review_context_describes_generated_assets():
    ctx = media_review_context({'items': [], 'reason': 'Clarify system flow'}, hero_path='hero.png', diagram_path='diagram.png')
    assert 'Generated 16:9' in ctx
    assert 'engineering schematic' in ctx
    assert 'diagram.png' in ctx
