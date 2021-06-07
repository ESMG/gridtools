import pytest

xfail = pytest.mark.xfail

# content of test_sample.py
def func(x):
    return x + 1

@xfail
def test_answer():
    assert func(3) == 5
