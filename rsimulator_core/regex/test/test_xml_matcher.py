import pytest

from rsimulator_core.regex.xml_matcher import *


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Equal as strings
        (
            "<x/>",
            "<x/>",
            Result(error=None, groups=()),
        ),
        # With and without prolog
        (
            '<?xml version="1.0" encoding="UTF-8"?><x/>',
            "<x/>",
            Result(error=None, groups=()),
        ),
        # Insignificant whitespaces
        (
            '<?xml version="1.0" encoding="UTF-8"?><x><y>y</y></x>',
            "<x>\n<y>    y  \n</y></x>\n",
            Result(error=None, groups=()),
        ),
        # Element name. Attribute name, value and order. Regexp of element and attribute values.
        (
            '<x x1=".*" x2="([\\w]+)"><y y="([a-z0-9]{1})">y</y><z z="z">(.*)</z></x>',
            '<x x2="x2" x1="x1"><y y="y">y</y><z z="z">z</z></x>',
            Result(error=None, groups=("x2", "y", "z")),
        ),
        # Regexp of element structure
        ("<x>(.*)</x>", "<x><y><z>z</z></y></x>", Result(groups=("<y><z>z</z></y>",))),
        (
            "(.*)",
            "<x>\n<y><z>z</z></y></x>",
            Result(error=None, groups=("<x>\n<y><z>z</z></y></x>",)),
        ),
    ],
)
def test_success_not_namespace_aware(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Different namespace order and prefixes
        (
            '<x xmlns:a="z" targetNamespace="y" xmlns="x"><a:a a="(1)" b="2"><a:b/></a:a></x>',
            '<x xmlns="x" targetNamespace="y" xmlns:z="z"><z:a b="2" a="1"><z:b/></z:a></x>',
            Result(error=None, groups=("1",)),
        ),
        # Regexp namespaces and different order and prefixes
        # ('<x xmlns:a=".*" targetNamespace="[\\w]+" xmlns="[a-z0-9]{1}"><a:a/></x>',
        #  '<x xmlns="x" targetNamespace="y" xmlns:z="z"><z:a/></x>', Result(error=None, groups=()))
    ],
)
def test_success_namespace_aware(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "<x>",
            "<x/>",
            Result(
                error=Error(
                    parents=None,
                    this=None,
                    that=None,
                    message=(
                        'Cannot parse "this": "<x>", Premature end of data in tag x line 1, '
                        "line 1, column 4 (<string>, line 1)"
                    ),
                ),
                groups=(),
            ),
        ),
        (
            "<x/>",
            "<x>",
            Result(
                error=Error(
                    parents=None,
                    this=None,
                    that=None,
                    message=(
                        'Cannot parse "that": "<x>", Premature end of data in tag x line 1, '
                        "line 1, column 4 (<string>, line 1)"
                    ),
                ),
                groups=(),
            ),
        ),
    ],
)
def test_failure_parse(this, that, expected):
    assert match(this, that) == expected


def test_failure_different_types():
    # noinspection PyTypeChecker
    assert match("", 1) == Result(
        error=Error(
            parents=(),
            this=None,
            that=None,
            message="Values not strings: \"<class 'str'>\" != \"<class 'int'>\"",
        ),
        groups=(),
    )


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Element name
        (
            "<x/>",
            "<a/>",
            Result(
                error=Error(
                    parents=(), this="x", that="a", message="Names not matching"
                ),
                groups=(),
            ),
        ),
        (
            "<x><y></y></x>",
            "<x><b></b></x>",
            Result(
                error=Error(
                    parents=("x",), this="y", that="b", message="Names not matching"
                ),
                groups=(),
            ),
        ),
        (
            "<x><y></y><z></z></x>",
            "<x><b></b><z></z></x>",
            Result(
                error=Error(
                    parents=("x",), this="y", that="b", message="Names not matching"
                ),
                groups=(),
            ),
        ),
        (
            "<x><y></y><z></z></x>",
            "<x><y></y><c></c></x>",
            Result(
                error=Error(
                    parents=("x",), this="z", that="c", message="Names not matching"
                ),
                groups=(),
            ),
        ),
        # Element order
        (
            "<x><y></y><z></z></x>",
            "<x><z></z><y></y></x>",
            Result(
                error=Error(
                    parents=("x",), this="y", that="z", message="Names not matching"
                ),
                groups=(),
            ),
        ),
        # Element value
        (
            "<x>x</x>",
            "<x>a</x>",
            Result(
                error=Error(
                    parents=(),
                    this="x",
                    that="x",
                    message='Text not matching: "x" != "a"',
                ),
                groups=(),
            ),
        ),
        (
            "<x><y>y</y><z></z></x>",
            "<x><y>a</y><z></z></x>",
            Result(
                error=Error(
                    parents=("x",),
                    this="y",
                    that="y",
                    message='Text not matching: "y" != "a"',
                ),
                groups=(),
            ),
        ),
        (
            "<x><y></y><z>z</z></x>",
            "<x><y></y><z>a</z></x>",
            Result(
                error=Error(
                    parents=("x",),
                    this="z",
                    that="z",
                    message='Text not matching: "z" != "a"',
                ),
                groups=(),
            ),
        ),
        (
            "<x><y>y</y><z>z</z></x>",
            "<x><y>a</y><z>b</z></x>",
            Result(
                error=Error(
                    parents=("x",),
                    this="y",
                    that="y",
                    message='Text not matching: "y" != "a"',
                ),
                groups=(),
            ),
        ),
        # Attribute value
        (
            '<x y="1"/>',
            '<x y="2"/>',
            Result(
                error=Error(
                    parents=(),
                    this="x",
                    that="x",
                    message='Attribute values not matching for y: "1" != "2"',
                ),
                groups=(),
            ),
        ),
        # Different number of children
        (
            "<x><x/></x>",
            "<x></x>",
            Result(
                error=Error(
                    parents=(),
                    this="x",
                    that="x",
                    message="Different number of children",
                ),
                groups=(),
            ),
        ),
        # Different number of attributes
        (
            '<x y="1"/>',
            "<x/>",
            Result(
                error=Error(
                    parents=(),
                    this="x",
                    that="x",
                    message="Different number of attributes",
                ),
                groups=(),
            ),
        ),
    ],
)
def test_failure_not_namespace_aware(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Element name
        (
            '<x xmlns="x"></x>',
            '<x xmlns="a"> </x>',
            Result(
                error=Error(
                    parents=(),
                    this="{x}x",
                    that="{a}x",
                    message="Names not matching",
                ),
                groups=(),
            ),
        ),
        (
            '<x xmlns="x" xmlns:n="y"><n:y/></x>',
            '<x xmlns="x" xmlns:n="a"><n:y/></x>',
            Result(
                error=Error(
                    parents=("{x}x",),
                    this="{y}y",
                    that="{a}y",
                    message="Names not matching",
                ),
                groups=(),
            ),
        ),
    ],
)
def test_failure_namespace_aware(this, that, expected):
    assert match(this, that) == expected


def test_success_soap_example():
    this = """<?xml version="1.0" encoding="UTF-8"?>
            <soapenv:Envelope xmlns:hel="http://www.github.com/bjuvensjo/rsimulator/SayHello/" xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
               <soapenv:Header></soapenv:Header>
               <soapenv:Body>
                  <hel:SayHelloRequest>
                     <from b="b" a="([a-z]+)">(.*)</from>
                     <to>([\\w]{5}[ab]tor)</to>
                     <greeting>[^z]*</greeting>
                     <foo>(.*)</foo>
                  </hel:SayHelloRequest>
               </soapenv:Body>
            </soapenv:Envelope>"""
    that = """<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" xmlns:h="http://www.github.com/bjuvensjo/rsimulator/SayHello/">
                   <s:Header/>
                   <s:Body>
                      <h:SayHelloRequest>
                         <from a="a" b="b">Test3</from>
                         <to>Simulator</to>
                         <greeting>hey</greeting>
                         <foo>
                           <bar>
                             <baz>baz</baz>
                           </bar>                           
                         </foo>
                      </h:SayHelloRequest>
                   </s:Body>
                </s:Envelope>"""
    assert match(this, that) == Result(
        error=None,
        groups=("a", "Test3", "Simulator", "<n2:bar><n2:baz>baz</n2:baz></n2:bar>"),
    )
