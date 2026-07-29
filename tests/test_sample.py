"""
Sample test file for CI pipeline demo.
Real project mein yahan actual pipeline ke functions test honge.
"""


def add(a, b):
    return a + b


def test_add():
    assert add(2, 3) == 5


def test_add_negative():
    assert add(-1, -1) == -2
