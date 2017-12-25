import unittest
from importlib import reload

from rsimulator_core.matcher import *


class RSimulatorCore(unittest.TestCase):

    def test_service_no_cache(self):
        import rsimulator_core.config
        rsimulator_core.config.CACHE = False
        import rsimulator_core.rsimulator_core
        reload(rsimulator_core.decorator)
        reload(rsimulator_core.rsimulator_core)
        from rsimulator_core.rsimulator_core import service

        self.assertEqual({'request': '{"foo": "Hello World!"}',
                          'candidate_path': dirname(__file__) + '/data/json/1_Request.json',
                          'candidate': '{\n  "foo": "(.*)"\n}',
                          'response_path': dirname(__file__) + '/data/json/1_Response.json',
                          'response_raw': '{\n  "bar": "${1}"\n} ', 'response': '{\n  "bar": "Hello World!"\n} '},
                         service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))
        self.assertFalse(service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json') is
                         service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))

    def test_service_cache(self):
        import rsimulator_core.config
        rsimulator_core.config.CACHE = True
        import rsimulator_core.rsimulator_core
        reload(rsimulator_core.decorator)
        reload(rsimulator_core.rsimulator_core)
        from rsimulator_core.rsimulator_core import service

        self.assertEqual({'request': '{"foo": "Hello World!"}',
                          'candidate_path': dirname(__file__) + '/data/json/1_Request.json',
                          'candidate': '{\n  "foo": "(.*)"\n}',
                          'response_path': dirname(__file__) + '/data/json/1_Response.json',
                          'response_raw': '{\n  "bar": "${1}"\n} ', 'response': '{\n  "bar": "Hello World!"\n} '},
                         service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))
        self.assertTrue(service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json') is
                        service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))


if __name__ == '__main__':
    unittest.main()
