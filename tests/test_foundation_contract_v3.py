from teacher_agent.prompts import (
    FOUNDATION_CONTRACT,
    lesson_prompt,
    premium_review_prompt,
    surgical_quality_repair_prompt,
)


def test_class1_contract_separates_robot_identity_decision_authority_and_feedback():
    assert 'Robot identity is separate from decision authority' in FOUNDATION_CONTRACT
    assert 'human operator, a preprogrammed controller, or autonomous software' in FOUNDATION_CONTRACT
    assert "do not use 'fixed automation' as a mutually exclusive control category" in FOUNDATION_CONTRACT.lower()
    assert 'predetermined feedback rule' in FOUNDATION_CONTRACT
    assert 'sustained feedback regulation' in FOUNDATION_CONTRACT


def test_class1_generation_prompt_forbids_mutually_exclusive_fixed_automation_column():
    prompt = lesson_prompt(
        {
            'class_no': 1,
            'title': 'What Is a Robot?',
            'concepts': 'robot, autonomy, machine, environment',
        },
        None,
        'Sense -> Think -> Act'
    )

    assert "do not use a yes/no 'Fixed automation' column" in prompt
    assert "'Immediate decision authority'" in prompt
    assert "'Feedback in the described behavior?'" in prompt
    assert 'keep the robot definition IDENTICAL' in prompt
    assert 'sustained feedback regulation' in prompt


def test_class1_reviewer_uses_declared_foundation_contract_instead_of_reinventing_taxonomy():
    prompt = premium_review_prompt(
        '# Class 1: What Is a Robot?',
        1,
        'What Is a Robot?',
        None
    )

    assert 'AUTHORITATIVE FOUNDATION CONTRACT FOR THIS REVIEW' in prompt
    assert 'do not create a blocking issue merely because another textbook uses a different boundary or label' in prompt
    assert "do not require a yes/no 'Fixed automation' category" in prompt
    assert 'threshold-based feedback as feedback' in prompt


def test_surgical_repair_sweeps_all_class1_terminology_locations():
    prompt = surgical_quality_repair_prompt(
        '# Class 1: What Is a Robot?',
        '{"overall_score":81,"blocking_issues":["taxonomy inconsistency"]}',
        '{"passed":true,"word_count":3055}',
        None
    )

    assert 'run a terminology sweep' in prompt
    assert 'robot definition, comparison table, feedback explanation, quiz, answers, and Vocabulary' in prompt
    assert 'A preprogrammed task and feedback can coexist' in prompt
    assert 'including human-directed teleoperation' in prompt
