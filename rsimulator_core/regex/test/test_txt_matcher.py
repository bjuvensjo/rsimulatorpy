import pytest
from rsimulator_core.data import Error
from rsimulator_core.regex.data import Groups
from rsimulator_core.regex.txt_matcher import match


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "We are ([a-zA-z]+) and (.*)",
            "We are Foo and Bar",
            Groups(groups=("Foo", "Bar")),
        ),
    ],
)
def test_match(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "a",
            "b",
            Error(
                path=(),
                this="a",
                that="b",
                message="Values not matching: a != b",
            ),
        ),
    ],
)
def test_error(this, that, expected):
    assert match(this, that) == expected
