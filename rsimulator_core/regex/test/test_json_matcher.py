import pytest

from rsimulator_core.regex.json_matcher import *


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '{"c":"([a-z_]+)", "a": 1, "d": {"e": "^(e)_(v.+$)", "f": {"g": 1}}, "b":false}',
            '{"a": 1, "b":false, "c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}}',
            Result(error=None, groups=("c_value", "e", "value")),
        ),
    ],
)
def test_success_dicts(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '[1, 2, 3, [false, true, ["(a)", "b"]]]',
            '[3, 2, 1, [true, false, ["b", "a"]]]',
            Result(
                error=None,
                groups=("a",),
            ),
        ),
    ],
)
def test_success_arrays(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '"(h)ell(o)"',
            '"hello"',
            Result(
                error=None,
                groups=(
                    "h",
                    "o",
                ),
            ),
        )
    ],
)
def test_success_json_strings(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        ("(hello)", "hello", Result(error=None, groups=("hello",))),
        (
            '\\["(hello)", "(world)"\\]',
            '["hello", "world"]',
            Result(error=None, groups=("hello", "world")),
        ),
        (
            '{"a": (1), "b":(false), (.*)}',
            '{"a": 1, "b":false, "c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}}',
            Result(
                error=None,
                groups=(
                    "1",
                    "false",
                    '"c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}',
                ),
            ),
        ),
        (
            ".+",
            '{"a": 1, "b":false, "c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}}',
            Result(
                error=None,
                groups=(),
            ),
        ),
    ],
)
# Note that this does not require valid json
def test_success_re_full_matches(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "foo: fooValue",
            '{"foo": "fooValue"}',
            Result(
                error=Error(
                    parents=None,
                    this=None,
                    that=None,
                    message='Cannot load this "foo: fooValue": Expecting value: '
                    "line 1 column 1 (char 0)",
                ),
                groups=(),
            ),
        ),
        (
            '{"foo": "fooValue"}',
            "foo: fooValue",
            Result(
                error=Error(
                    parents=None,
                    this=None,
                    that=None,
                    message='Cannot load that "foo: fooValue": Expecting value: '
                    "line 1 column 1 (char 0)",
                ),
                groups=(),
            ),
        ),
    ],
)
def test_parse_error(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "[1]",
            '{"foo": "fooValue"}',
            Result(
                error=Error(
                    parents=(),
                    this="[1]",
                    that="{'foo': 'fooValue'}",
                    message="Objects of different types: <class 'list'>, <class "
                    "'dict'>",
                ),
                groups=(),
            ),
        ),
    ],
)
def test_objects_of_different_types_error(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '"a"',
            '"b"',
            Result(
                error=Error(
                    parents=(),
                    this=None,
                    that=None,
                    message='Values not matching: "a" != "b"',
                ),
                groups=(),
            ),
        ),
        (
            '["a"]',
            '["b"]',
            Result(
                error=Error(
                    parents=(),
                    this=None,
                    that=None,
                    message='Values not matching: "a" != "b"',
                ),
                groups=(),
            ),
        ),
        (
            '{"p1": {"p2": "a"}}',
            '{"p1": {"p2": "b"}}',
            Result(
                error=Error(
                    parents=("p1",),
                    this="p2",
                    that="p2",
                    message='Values not matching: "a" != "b"',
                ),
                groups=(),
            ),
        ),
        (
            '{"p1": {"p2": 1}}',
            '{"p1": {"p2": 2}}',
            Result(
                error=Error(
                    parents=("p1",),
                    this="p2",
                    that="p2",
                    message='Values not matching: "1" != "2"',
                ),
                groups=(),
            ),
        ),
        (
            '{"p1": {"p2": ["a"]}}',
            '{"p1": {"p2": ["b"]}}',
            Result(
                error=Error(
                    parents=("p1",),
                    this="p2",
                    that="p2",
                    message='Values not matching: "a" != "b"',
                ),
                groups=(),
            ),
        ),
    ],
)
def test_not_matching_values_error(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '{"p1": {"p2": "a"}}',
            '{"p1": {"p2": "a", "p3": "b"}}',
            Result(
                error=Error(
                    parents=(), this="p1", that="p1", message="Different number of keys"
                ),
                groups=(),
            ),
        ),
    ],
)
def test_different_number_of_keys_error(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '{"p1": {"p2": "a"}}',
            '{"p1": {"p": "a"}}',
            Result(
                error=Error(
                    parents=("p1",),
                    this="p2",
                    that="p",
                    message='Keys not matching: "p2" != "p"',
                ),
                groups=(),
            ),
        ),
    ],
)
def test_not_matching_keys_error(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '{"p1": {"p2": [1, 2, 3]}}',
            '{"p1": {"p2": [1, 2]}}',
            Result(
                error=Error(
                    parents=("p1",),
                    this="p2",
                    that="p2",
                    message="Different length of lists",
                ),
                groups=(),
            ),
        ),
    ],
)
def test_different_length_of_lists(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '{"p1": {"p2": [1, 2, {"p3": "a"}]}}',
            '{"p1": {"p2": [1, 2, {"p3": "b"}]}}',
            Result(
                error=Error(
                    parents=("p1", "p2"),
                    this="p3",
                    that="p3",
                    message='Values not matching: "a" != "b"',
                ),
                groups=(),
            ),
        ),
    ],
)
def test_error_within_lists(this, that, expected):
    assert match(this, that) == expected
