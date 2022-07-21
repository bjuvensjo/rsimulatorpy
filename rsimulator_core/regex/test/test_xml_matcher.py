import pytest
from rsimulator_core.data import Error
from rsimulator_core.regex.data import Groups
from rsimulator_core.regex.xml_matcher import match



@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Equal as strings
        (
            "<x/>",
            "<x/>",
            Groups(groups=()),
        ),
        # With and without prolog
        (
            '<?xml version="1.0" encoding="UTF-8"?><x/>',
            "<x/>",
            Groups(groups=()),
        ),
        # Insignificant whitespaces
        (
            '<?xml version="1.0" encoding="UTF-8"?><x><y>y</y></x>',
            "<x>\n<y>    y  \n</y></x>\n",
            Groups(groups=()),
        ),
        # Element name. Attribute name, value and order. Regexp of element and attribute values.
        (
            '<x x1=".*" x2="([\\w]+)"><y y="([a-z0-9]{1})">y</y><z z="z">(.*)</z></x>',
            '<x x2="x2" x1="x1"><y y="y">y</y><z z="z">z</z></x>',
            Groups(groups=("x2", "y", "z")),
        ),
        # Regexp of element structure
        ("<x>(.*)</x>", "<x><y><z>z</z></y></x>", Groups(groups=("<y><z>z</z></y>",))),
        (
            "(.*)",
            "<x>\n<y><z>z</z></y></x>",
            Groups(groups=("<x>\n<y><z>z</z></y></x>",)),
        ),
    ],
)
def test_match_not_namespace_aware(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Different namespace order and prefixes
        (
            '<x xmlns:a="z" targetNamespace="y" xmlns="x"><a:a a="(1)" b="2"><a:b/></a:a></x>',
            '<x xmlns="x" targetNamespace="y" xmlns:z="z"><z:a b="2" a="1"><z:b/></z:a></x>',
            Groups(groups=("1",)),
        ),
        # Regexp namespaces and different order and prefixes
        # ('<x xmlns:a=".*" targetNamespace="[\\w]+" xmlns="[a-z0-9]{1}"><a:a/></x>',
        #  '<x xmlns="x" targetNamespace="y" xmlns:z="z"><z:a/></x>', Match(error=None, groups=()))
    ],
)
def test_match_namespace_aware(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        (
            "<x>",
            "<x/>",
            Error(
                path=(),
                this="<x>",
                that="<x/>",
                message=(
                    'Cannot parse "this": "<x>", Premature end of data in tag x line 1, '
                    "line 1, column 4 (<string>, line 1)"
                ),
            ),
        ),
        (
            "<x/>",
            "<x>",
            Error(
                path=(),
                this="<x/>",
                that="<x>",
                message=(
                    'Cannot parse "that": "<x>", Premature end of data in tag x line 1, '
                    "line 1, column 4 (<string>, line 1)"
                ),
            ),
        ),
    ],
)
def test_error_parse(this, that, expected):
    assert match(this, that) == expected


def test_error_different_types():
    assert match("", 1) == Error(
        path=(),
        this="",
        that="1",
        message="Values not strings: \"<class 'str'>\" != \"<class 'int'>\"",
    )


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Element name
        (
            "<x/>",
            "<a/>",
            Error(
                path=(),
                this="<x/>",
                that="<a/>",
                message='Names not matching: "x" != "a"',
            ),
        ),
        (
            "<x><y></y></x>",
            "<x><b></b></x>",
            Error(
                path=("x",),
                this="<y/>",
                that="<b/>",
                message='Names not matching: "y" != "b"',
            ),
        ),
        (
            "<x><y></y><z></z></x>",
            "<x><b></b><z></z></x>",
            Error(
                path=("x",),
                this="<y/>",
                that="<b/>",
                message='Names not matching: "y" != "b"',
            ),
        ),
        (
            "<x><y></y><z></z></x>",
            "<x><y></y><c></c></x>",
            Error(
                path=("x",),
                this="<z/>",
                that="<c/>",
                message='Names not matching: "z" != "c"',
            ),
        ),
        # Element order
        (
            "<x><y></y><z></z></x>",
            "<x><z></z><y></y></x>",
            Error(
                path=("x",),
                this="<y/>",
                that="<z/>",
                message='Names not matching: "y" != "z"',
            ),
        ),
        # Element value
        (
            "<x>x</x>",
            "<x>a</x>",
            Error(
                path=(),
                this="<x>x</x>",
                that="<x>a</x>",
                message='Text not matching: "x" != "a"',
            ),
        ),
        (
            "<x><y>y</y><z></z></x>",
            "<x><y>a</y><z></z></x>",
            Error(
                path=("x",),
                this="<y>y</y>",
                that="<y>a</y>",
                message='Text not matching: "y" != "a"',
            ),
        ),
        (
            "<x><y></y><z>z</z></x>",
            "<x><y></y><z>a</z></x>",
            Error(
                path=("x",),
                this="<z>z</z>",
                that="<z>a</z>",
                message='Text not matching: "z" != "a"',
            ),
        ),
        (
            "<x><y>y</y><z>z</z></x>",
            "<x><y>a</y><z>b</z></x>",
            Error(
                path=("x",),
                this="<y>y</y>",
                that="<y>a</y>",
                message='Text not matching: "y" != "a"',
            ),
        ),
        # Attribute value
        (
            '<x y="1"/>',
            '<x y="2"/>',
            Error(
                path=(),
                this='<x y="1"/>',
                that='<x y="2"/>',
                message='Attribute values not matching for y: "1" != "2"',
            ),
        ),
        # Different number of children
        (
            "<x><x/></x>",
            "<x></x>",
            Error(
                path=(),
                this="<x><x/></x>",
                that="<x/>",
                message="Different number of children",
            ),
        ),
        # Different number of attributes
        (
            '<x y="1"/>',
            "<x/>",
            Error(
                path=(),
                this='<x y="1"/>',
                that="<x/>",
                message="Different number of attributes",
            ),
        ),
    ],
)
def test_error_not_namespace_aware(this, that, expected):
    assert match(this, that) == expected


@pytest.mark.parametrize(
    "this, that, expected",
    [
        # Element name
        (
            '<x xmlns="x"></x>',
            '<x xmlns="a"> </x>',
            Error(
                path=(),
                this='<x xmlns="x"/>',
                that='<x xmlns="a"> </x>',
                message='Names not matching: "{x}x" != "{a}x"',
            ),
        ),
        (
            '<x xmlns="x" xmlns:n="y"><n:y/></x>',
            '<x xmlns="x" xmlns:n="a"><n:y/></x>',
            Error(
                path=("{x}x",),
                this='<n:y xmlns:n="y" xmlns="x"/>',
                that='<n:y xmlns:n="a" xmlns="x"/>',
                message='Names not matching: "{y}y" != "{a}y"',
            ),
        ),
    ],
)
def test_error_namespace_aware(this, that, expected):
    assert match(this, that) == expected


def test_match_soap_example():
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
    assert match(this, that) == Groups(
        groups=("a", "Test3", "Simulator", "<n2:bar><n2:baz>baz</n2:baz></n2:bar>"),
    )
