from importlib import reload

from rsimulator_core.matcher import *

root_dir = f'{dirname(__file__)}/data'


def test_service_no_cache():
    import rsimulator_core.config
    rsimulator_core.config.CACHE = False
    import rsimulator_core.core
    reload(rsimulator_core.decorator)
    reload(rsimulator_core.core)
    from rsimulator_core.core import service

    assert ({'request': '{"foo": "Hello World!"}',
             'candidate_path': f'{root_dir}/json/1_Request.json',
             'candidate': '{\n  "foo": "(.*)"\n}',
             'response_path': f'{root_dir}/json/1_Response.json',
             'response_raw': '{\n  "bar": "${1}"\n} ', 'response': '{\n  "bar": "Hello World!"\n} '} ==
            service(root_dir, 'json', '{"foo": "Hello World!"}', 'json'))
    assert (service(root_dir, 'json', '{"foo": "Hello World!"}', 'json') is not
            service(root_dir, 'json', '{"foo": "Hello World!"}', 'json'))


def test_service_cache():
    import rsimulator_core.config
    rsimulator_core.config.CACHE = True
    import rsimulator_core.core
    reload(rsimulator_core.decorator)
    reload(rsimulator_core.core)
    from rsimulator_core.core import service

    assert ({'request': '{"foo": "Hello World!"}',
             'candidate_path': f'{root_dir}/json/1_Request.json',
             'candidate': '{\n  "foo": "(.*)"\n}',
             'response_path': f'{root_dir}/json/1_Response.json',
             'response_raw': '{\n  "bar": "${1}"\n} ', 'response': '{\n  "bar": "Hello World!"\n} '} ==
            service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))
    assert (service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json') is
            service(f'{dirname(__file__)}/data', 'json', '{"foo": "Hello World!"}', 'json'))
