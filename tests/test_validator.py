from teacher_agent.validator import extract_python, validate_python_blocks

def test_extract_python():
    md = """## Python Lab
```python
print("hello robot")
```
"""
    assert extract_python(md) == ['print("hello robot")']

def test_python_validation_success():
    md = """```python
x = 2 + 2
print(x)
```"""
    assert validate_python_blocks(md) == []

def test_python_validation_failure():
    md = """```python
for
```"""
    assert validate_python_blocks(md)
