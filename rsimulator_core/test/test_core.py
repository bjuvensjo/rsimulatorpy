from importlib import reload
from posixpath import dirname

root_dir = f"{dirname(__file__)}/../regex/test/data"


def test_service_no_cache():
    import rsimulator_core.config

    rsimulator_core.config.CACHE = False
    from rsimulator_core import Match, core

    reload(rsimulator_core.decorators)
    reload(rsimulator_core.core)

    assert core.service(root_dir, "json", '{"foo": "Hello World!"}', "json") == Match(
        request='{"foo": "Hello World!"}',
        candidate_path=f"{root_dir}/json/1_Request.json",
        candidate='{\n  "foo": "(.*)"\n}',
        response_path=f"{root_dir}/json/1_Response.json",
        response_raw='{\n  "bar": "${1}"\n} ',
        response='{\n  "bar": "Hello World!"\n} ',
    )

    assert core.service(
        root_dir, "json", '{"foo": "Hello World!"}', "json"
    ) is not core.service(root_dir, "json", '{"foo": "Hello World!"}', "json")


def test_service_cache():
    import rsimulator_core.config

    rsimulator_core.config.CACHE = True
    from rsimulator_core import Match, core

    reload(rsimulator_core.decorators)
    reload(rsimulator_core.core)

    assert core.service(root_dir, "json", '{"foo": "Hello World!"}', "json") == Match(
        request='{"foo": "Hello World!"}',
        candidate_path=f"{root_dir}/json/1_Request.json",
        candidate='{\n  "foo": "(.*)"\n}',
        response_path=f"{root_dir}/json/1_Response.json",
        response_raw='{\n  "bar": "${1}"\n} ',
        response='{\n  "bar": "Hello World!"\n} ',
    )
    assert core.service(
        root_dir, "json", '{"foo": "Hello World!"}', "json"
    ) is core.service(root_dir, "json", '{"foo": "Hello World!"}', "json")


def test_service_no_match():
    import rsimulator_core.config

    rsimulator_core.config.CACHE = True
    from rsimulator_core import core

    reload(rsimulator_core.decorators)
    reload(rsimulator_core.core)

    assert core.service(root_dir, "json", '{"dummy": "Hello World!"}', "json") is None
    assert core.service(
        root_dir, "json", '{"foo": "Hello World!"}', "json"
    ) is core.service(root_dir, "json", '{"foo": "Hello World!"}', "json")
