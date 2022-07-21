from importlib import reload
from posixpath import dirname

from rsimulator_core.data import Match

root_dir = f"{dirname(__file__)}/../regex/test/data"


def test_service_no_cache():
    import rsimulator_core.config

    rsimulator_core.config.CACHE = False
    import rsimulator_core.core

    reload(rsimulator_core.decorators)
    reload(rsimulator_core.core)
    from rsimulator_core.core import service

    assert service(root_dir, "json", '{"foo": "Hello World!"}', "json") == Match(
        request='{"foo": "Hello World!"}',
        candidate_path=f"{root_dir}/json/1_Request.json",
        candidate='{\n  "foo": "(.*)"\n}',
        response_path=f"{root_dir}/json/1_Response.json",
        response_raw='{\n  "bar": "${1}"\n} ',
        response='{\n  "bar": "Hello World!"\n} ',
    )
    assert service(root_dir, "json", '{"foo": "Hello World!"}', "json") is not service(
        root_dir, "json", '{"foo": "Hello World!"}', "json"
    )


def test_service_cache():
    import rsimulator_core.config

    rsimulator_core.config.CACHE = True
    import rsimulator_core.core

    reload(rsimulator_core.decorators)
    reload(rsimulator_core.core)
    from rsimulator_core.core import service

    assert service(
        root_dir, "json", '{"foo": "Hello World!"}', "json"
    ) == Match(
        request='{"foo": "Hello World!"}',
        candidate_path=f"{root_dir}/json/1_Request.json",
        candidate='{\n  "foo": "(.*)"\n}',
        response_path=f"{root_dir}/json/1_Response.json",
        response_raw='{\n  "bar": "${1}"\n} ',
        response='{\n  "bar": "Hello World!"\n} ',
    )
    assert service(
        f"{dirname(__file__)}/data", "json", '{"foo": "Hello World!"}', "json"
    ) is service(f"{dirname(__file__)}/data", "json", '{"foo": "Hello World!"}', "json")


def test_service_no_match():
    import rsimulator_core.config

    rsimulator_core.config.CACHE = True
    import rsimulator_core.core

    reload(rsimulator_core.decorators)
    reload(rsimulator_core.core)
    from rsimulator_core.core import service

    assert (
        service(
            f"{dirname(__file__)}/data", "json", '{"dummy": "Hello World!"}', "json"
        )
        is None
    )
    assert service(
        f"{dirname(__file__)}/data", "json", '{"foo": "Hello World!"}', "json"
    ) is service(f"{dirname(__file__)}/data", "json", '{"foo": "Hello World!"}', "json")
