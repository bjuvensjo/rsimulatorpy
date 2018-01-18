import unittest

from rsimulator_core.matcher import *


class Matcher(unittest.TestCase):

    def test_find_matches_json(self):
        self.assertEqual([{'request': '{"foo": "Hello World!"}',
                           'candidate_path': dirname(__file__) + '/data/json/1_Request.json',
                           'candidate': '{\n  "foo": "(.*)"\n}',
                           'response_path': dirname(__file__) + '/data/json/1_Response.json',
                           'response_raw': '{\n  "bar": "${1}"\n} ', 'response': '{\n  "bar": "Hello World!"\n} '}],
                         find_matches(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))
        self.assertEqual([{'candidate': '',
                           'candidate_path': '/Users/ei4577/git/rsimulator-py/rsimulator_core/test/data/json/2_Request.json',
                           'request': '',
                           'response': '{\n  "bar": "foo"\n} ',
                           'response_path': '/Users/ei4577/git/rsimulator-py/rsimulator_core/test/data/json/2_Response.json',
                           'response_raw': '{\n  "bar": "foo"\n} '}],
                         find_matches(f'{dirname(__file__)}/data', 'json', '', 'json'))

    def test_find_matches_txt(self):
        self.assertEqual([{'request': 'This\nis\nthe\nrequest',
                           'candidate_path': dirname(__file__) + '/data/txt/1_Request.txt',
                           'candidate': '(This.*)',
                           'response_path': dirname(__file__) + '/data/txt/1_Response.txt',
                           'response_raw': 'response to ${1}', 'response': 'response to This\nis\nthe\nrequest'}],
                         find_matches(f'{dirname(__file__)}/data', 'txt', 'This\nis\nthe\nrequest', 'txt'))

        self.assertEqual([{'request': 'Harald Ljungstroem says hello!',
                           'candidate_path': dirname(__file__) + '/data/txt/2_Request.txt',
                           'candidate': '([a-zA-Z]{6}) ([^ ]+) says hello!',
                           'response_path': dirname(__file__) + '/data/txt/2_Response.txt',
                           'response_raw': 'Hello ${1} ${2} says rsimulator!',
                           'response': 'Hello Harald Ljungstroem says rsimulator!'}],
                         find_matches(f'{dirname(__file__)}/data', 'txt', 'Harald Ljungstroem says hello!', 'txt'))

    def test_find_matches_xml(self):
        self.assertEqual([{
            'request': '<note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Dont forget me this weekend!</body></note>',
            'candidate_path': dirname(__file__) + '/data/xml/1_Request.xml',
            'candidate': '<note>\n    <to>(Tove)</to>\n    <from>(Jani)</from>\n    <heading>Reminder</heading>\n    <body>(Dont forget me this weekend!)</body>\n</note>',
            'response_path': dirname(__file__) + '/data/xml/1_Response.xml',
            'response_raw': '<note>\n    <to>${2}</to>\n    <from>${1}</from>\n    <heading>Reminder</heading>\n    <body>${3}</body>\n</note>',
            'response': '<note>\n    <to>Jani</to>\n    <from>Tove</from>\n    <heading>Reminder</heading>\n    <body>Dont forget me this weekend!</body>\n</note>'}],
            find_matches(f'{dirname(__file__)}/data', 'xml',
                   '<note><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Dont forget me this weekend!</body></note>',
                   'xml'))

    def test_normalize(self):
        self.assertEqual('foo', normalize('foo', 'txt'))
        self.assertEqual('\{"a":1,"foo":"bar"\}', normalize('{"foo": "bar", "a": 1}', 'json'))
        self.assertEqual('\{"a":1,"baz":\{"a":\["[0-9]{1}",2,3\]\},"foo":"bar"\}',
                         normalize('{"foo": "bar", "a": 1, "baz": { "a": ["[0-9]{1}", 2, 3]}}', 'json'))
        self.assertEqual('<foo><bar>hello</bar></foo>', normalize('<foo>\n  <bar>hello</bar>\n</foo>', 'xml'))

    def test_match(self):
        self.assertTrue(
            get_match('\{"foo":"bar","a":1,"baz":\{"a":\[[0-9],2,3\]\}\}', '{"foo":"bar","a":1,"baz":{"a":[1,2,3]}}'))
        self.assertTrue(
            get_match('\{"(foo)":"bar","a":1,"(.*)":\{"a":\[1,2,3\]\}}', '{"foo":"bar","a":1,"baz":{"a":[1,2,3]}}'))

    def test_escape(self):
        self.assertEqual('{"a":1,"baz":\{"a":\[1,2,3\]\},"foo":"bar"}', escape({"foo":"bar","a":1,"baz":{"a":[1,2,3]}}, False))
        self.assertEqual('\{"a":1,"baz":\{"a":\[1,2,3\]\},"foo":"bar"\}', escape({"foo":"bar","a":1,"baz":{"a":[1,2,3]}}, True))


if __name__ == '__main__':
    unittest.main()
