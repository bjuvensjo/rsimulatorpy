from rsimulator_core.data import Error
from rsimulator_core.matcher import *

root_dir = f"{dirname(__file__)}/data"


def test_find_matches_json():
    assert find_matches(root_dir, "json", '{"foo": "Hello World!"}', "json") == (
        (
            CoreMatch(
                request='{"foo": "Hello World!"}',
                candidate_path=f"{root_dir}/json/1_Request.json",
                candidate='{\n  "foo": "(.*)"\n}',
                response_path=f"{root_dir}/json/1_Response.json",
                response_raw='{\n  "bar": "${1}"\n} ',
                response='{\n  "bar": "Hello World!"\n} ',
            ),
        ),
        (
            CoreNoMatch(
                request='{"foo": "Hello World!"}',
                candidate_path=f"{root_dir}/json/2_Request.json",
                candidate="",
                result=Result(
                    error=Error(
                        parents=None,
                        this=None,
                        that=None,
                        message='Cannot load this "": '
                        "Expecting value: line 1 "
                        "column 1 (char 0)",
                    ),
                    groups=(),
                ),
            ),
        ),
    )
    assert find_matches(root_dir, "json", "", "json") == (
        (
            CoreMatch(
                request="",
                candidate_path=f"{root_dir}/json/2_Request.json",
                candidate="",
                response_path=f"{root_dir}/json/2_Response.json",
                response_raw='{\n  "bar": "foo"\n} ',
                response='{\n  "bar": "foo"\n} ',
            ),
        ),
        (
            CoreNoMatch(
                request="",
                candidate_path=f"{root_dir}/json/1_Request.json",
                candidate='{\n  "foo": "(.*)"\n}',
                result=Result(
                    error=Error(
                        parents=None,
                        this=None,
                        that=None,
                        message='Cannot load that "": '
                        "Expecting value: line 1 "
                        "column 1 (char 0)",
                    ),
                    groups=(),
                ),
            ),
        ),
    )


def test_find_matches_txt():
    assert find_matches(root_dir, "txt", "This\nis\nthe\nrequest", "txt") == (
        (
            CoreMatch(
                request="This\nis\nthe\nrequest",
                candidate_path=f"{root_dir}/txt/1_Request.txt",
                candidate="(This.*)",
                response_path=f"{root_dir}/txt/1_Response.txt",
                response_raw="response to ${1}",
                response="response to This\nis\nthe\nrequest",
            ),
        ),
        (
            CoreNoMatch(
                request="This\nis\nthe\nrequest",
                candidate_path=f"{root_dir}/txt/2_Request.txt",
                candidate="([a-zA-Z]{6}) ([^ ]+) says hello!",
                result=Result(
                    error=Error(
                        parents=None,
                        this=None,
                        that=None,
                        message="Values not matching: "
                        "([a-zA-Z]{6}) ([^ ]+) says "
                        "hello! != This\n"
                        "is\n"
                        "the\n"
                        "request",
                    ),
                    groups=(),
                ),
            ),
        ),
    )
    assert find_matches(root_dir, "txt", "Harald Ljungstroem says hello!", "txt") == (
        (
            CoreMatch(
                request="Harald Ljungstroem says hello!",
                candidate_path=f"{root_dir}/txt/2_Request.txt",
                candidate="([a-zA-Z]{6}) ([^ ]+) says hello!",
                response_path=f"{root_dir}/txt/2_Response.txt",
                response_raw="Hello ${1} ${2} says rsimulator!",
                response="Hello Harald Ljungstroem says rsimulator!",
            ),
        ),
        (
            CoreNoMatch(
                request="Harald Ljungstroem says hello!",
                candidate_path=f"{root_dir}/txt/1_Request.txt",
                candidate="(This.*)",
                result=Result(
                    error=Error(
                        parents=None,
                        this=None,
                        that=None,
                        message="Values not matching: (This.*) "
                        "!= Harald Ljungstroem says "
                        "hello!",
                    ),
                    groups=(),
                ),
            ),
        ),
    )


def test_find_matches_xml():
    assert find_matches(
        root_dir,
        "xml",
        "<note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Dont forget me this weekend!</body></note>",
        "xml",
    ) == (
        (
            CoreMatch(
                request="<note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Dont "
                "forget me this weekend!</body></note>",
                candidate_path=f"{root_dir}/xml/1_Request.xml",
                candidate="<note>\n"
                "    <to>(Tove)</to>\n"
                "    <from>(Jani)</from>\n"
                "    <heading>Reminder</heading>\n"
                "    <body>(Dont forget me this weekend!)</body>\n"
                "</note>",
                response_path=f"{root_dir}/xml/1_Response.xml",
                response_raw="<note>\n"
                "    <to>${2}</to>\n"
                "    <from>${1}</from>\n"
                "    <heading>Reminder</heading>\n"
                "    <body>${3}</body>\n"
                "</note>",
                response="<note>\n"
                "    <to>Jani</to>\n"
                "    <from>Tove</from>\n"
                "    <heading>Reminder</heading>\n"
                "    <body>Dont forget me this weekend!</body>\n"
                "</note>",
            ),
        ),
        (),
    )
