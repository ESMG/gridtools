import pytest

xfail = pytest.mark.xfail

# content of test_class.py
class TestClass:
    def test_one(self):
        x = "this"
        assert "h" in x

    @xfail
    def test_two(self):
        x = "hello"
        assert hasattr(x, "check")
