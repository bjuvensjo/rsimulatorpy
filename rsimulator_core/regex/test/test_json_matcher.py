import pytest
from rsimulator_core.data import Error
from rsimulator_core.regex.data import Groups
from rsimulator_core.regex.json_matcher import match


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '{"c":"([a-z_]+)", "a": 1, "d": {"e": "^(e)_(v.+$)", "f": {"g": 1}}, "b":false}',
            '{"a": 1, "b":false, "c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}}',
            Groups(groups=("c_value", "e", "value")),
        ),
    ],
)
def test_match_dicts(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '[1, 2, 3, [false, true, ["(a)", "b"]]]',
            '[1, 2, 3, [false, true, ["a", "b"]]]',
            # '[3, 2, 1, [true, false, ["b", "a"]]]',
            Groups(groups=("a",)),
        ),
    ],
)
def test_match_arrays(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            '"(h)ell(o)"',
            '"hello"',
            Groups(groups=("h", "o")),
        )
    ],
)
def test_match_json_strings(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        ("(hello)", "hello", Groups(groups=("hello",))),
        (
            '\\["(hello)", "(world)"\\]',
            '["hello", "world"]',
            Groups(groups=("hello", "world")),
        ),
        (
            '{"a": (1), "b":(false), (.*)}',
            '{"a": 1, "b":false, "c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}}',
            Groups(
                groups=(
                    "1",
                    "false",
                    '"c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}',
                )
            ),
        ),
        (
            ".+",
            '{"a": 1, "b":false, "c":"c_value", "d": {"e": "e_value", "f": {"g": 1}}}',
            Groups(groups=()),
        ),
    ],
)
# Note that this does not require valid json
def test_match_re_full_matches(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "foo: fooValue",
            '{"foo": "fooValue"}',
            Error(
                path=(),
                this="foo: fooValue",
                that='{"foo": "fooValue"}',
                message='Cannot load this "foo: fooValue": Expecting value: '
                "line 1 column 1 (char 0)",
            ),
        ),
        (
            '{"foo": "fooValue"}',
            "foo: fooValue",
            Error(
                path=(),
                this='{"foo": "fooValue"}',
                that="foo: fooValue",
                message='Cannot load that "foo: fooValue": Expecting value: '
                "line 1 column 1 (char 0)",
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
            Error(
                path=(),
                this="[1]",
                that="{'foo': 'fooValue'}",
                message="Objects of different types: <class 'list'>, <class 'dict'>",
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
            Error(
                path=(),
                this="a",
                that="b",
                message='Values not matching: "a" != "b"',
            ),
        ),
        (
            '["a"]',
            '["b"]',
            Error(
                path=(0,),
                this="a",
                that="b",
                message='Values not matching: "a" != "b"',
            ),
        ),
        (
            '{"p1": {"p2": "a"}}',
            '{"p1": {"p2": "b"}}',
            Error(
                path=("p1", "p2"),
                this="a",
                that="b",
                message='Values not matching: "a" != "b"',
            ),
        ),
        (
            '{"p1": {"p2": 1}}',
            '{"p1": {"p2": 2}}',
            Error(
                path=("p1", "p2"),
                this="1",
                that="2",
                message='Values not matching: "1" != "2"',
            ),
        ),
        (
            '{"p1": {"p2": ["a"]}}',
            '{"p1": {"p2": ["b"]}}',
            Error(
                path=("p1", "p2", 0),
                this="a",
                that="b",
                message='Values not matching: "a" != "b"',
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
            Error(
                path=(),
                this="p1",
                that="p1",
                message="Different number of keys",
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
            Error(
                path=("p1",),
                this="p2",
                that=None,
                message='Keys not matching: "p2"',
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
            Error(
                path=("p1", "p2"),
                this="[1, 2, 3]",
                that="[1, 2]",
                message="Different length of lists",
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
            Error(
                path=("p1", "p2", 2, "p3"),
                this="a",
                that="b",
                message='Values not matching: "a" != "b"',
            ),
        ),
    ],
)
def test_error_within_lists(this, that, expected):
    assert match(this, that) == expected
