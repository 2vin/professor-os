from teacher_agent.validator import validate_python_blocks


def test_symbolic_image_indexing_is_syntax_only():
    assert validate_python_blocks(
        "```python\nimage[row][column][channel]\n```"
    ) == []


def test_undefined_assignment_is_still_rejected():
    errors = validate_python_blocks(
        "```python\npixel = image[row][column][channel]\nprint(pixel)\n```"
    )
    assert errors
    assert 'NameError' in errors[0]


def test_function_call_is_still_rejected():
    errors = validate_python_blocks(
        "```python\nshow_pixel(image[row][column][channel])\n```"
    )
    assert errors
    assert 'NameError' in errors[0]


def test_runtime_math_error_is_still_rejected():
    errors = validate_python_blocks(
        "```python\nvalue = 1 / 0\n```"
    )
    assert errors
    assert 'ZeroDivisionError' in errors[0]


def test_symbolic_expression_still_must_be_valid_python():
    errors = validate_python_blocks(
        "```python\nimage[row][column][channel\n```"
    )
    assert errors
    assert 'syntax error' in errors[0].lower()
