from teacher_agent.prompts import lesson_prompt


def test_class_one_prompt_blocks_advanced_scope_drift():
    prompt = lesson_prompt(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
            'concepts': 'robot, autonomy, machine, environment',
        },
        None,
        'Sense → Think → Act'
    )

    assert 'do not introduce path planning' in prompt
    assert 'stay within the listed Core concepts' in prompt
    assert 'same code block' in prompt.lower()
    assert 'source": "gemini' in prompt
