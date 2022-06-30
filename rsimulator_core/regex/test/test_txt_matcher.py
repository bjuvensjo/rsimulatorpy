import pytest

from rsimulator_core.regex.txt_matcher import *


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "We are ([a-zA-z]+) and (.*)",
            "We are Foo and Bar",
            Result(error=None, groups=("Foo", "Bar")),
        ),
    ],
)
def test_success(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "a",
            "b",
            Result(
                error=Error(
                    parents=None,
                    this=None,
                    that=None,
                    message="Values not matching: a != b",
                ),
                groups=(),
            ),
        ),
    ],
)
def test_failure(this, that, expected):
    assert match(this, that) == expected
