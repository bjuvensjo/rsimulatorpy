import logging
import re
from json import dumps, loads
from json.decoder import JSONDecodeError
from typing import Any

from rsimulator_core.data import Error
from rsimulator_core.regex.data import Groups

log = logging.getLogger(__name__)


def __error(
    parents: tuple[str, ...] | None,
    this_str: str | None,
    that_str: str | None,
    message: str,
) -> Error:
    return Error(parents, this_str, that_str, message)


def __match_default(this_value, that_value, parents: tuple[str, ...]) -> Error | Groups:
    if this_value == that_value:
        return Groups()
    return __error(
        parents,
        str(this_value),
        str(that_value),
        f'Values not matching: "{this_value}" != "{that_value}"',
    )


def __match_dict(
    this_dict: dict, that_dict: dict, parents: tuple[str, ...]
) -> Error | Groups:
    if len(this_dict) != len(that_dict):
        return __error(parents, None, None, "Different number of keys")
    groups = tuple()
    for this_child_key, this_child_value in this_dict.items():
        that_child_value = that_dict.get(this_child_key, None)
        if that_child_value is None:
            return __error(
                parents,
                this_child_key,
                None,
                f'Keys not matching: "{this_child_key}"',
            )
        child_match = __match_objects(
            this_child_value, that_child_value, parents + (this_child_key,)
        )
        if isinstance(child_match, Error):
            if child_match.this is None:
                return __error(
                    parents, this_child_key, this_child_key, child_match.message
                )
            else:
                return child_match
        else:
            groups += child_match.groups
    return Groups(groups=groups)


def __match_list(
    this_list: list, that_list: list, parents: tuple[str, ...]
) -> Error | Groups:
    if len(this_list) != len(that_list):
        return __error(
            parents, str(this_list), str(that_list), "Different length of lists"
        )
    groups = tuple()
    for index, children in enumerate(zip(this_list, that_list)):
        this_child, that_child = children
        child_match = __match_objects(this_child, that_child, parents + (index,))
        if isinstance(child_match, Error):
            return child_match
        else:
            groups += child_match.groups
    return Groups(groups=groups)


def __match_str(
    this_str: str, that_str: str, parents: tuple[str, ...]
) -> Error | Groups:
    if this_str == that_str:
        return Groups()
    if m := re.fullmatch(f"(?ms){this_str}", that_str):
        return Groups(groups=tuple(m.groups()))
    return __error(
        parents,
        this_str,
        that_str,
        f'Values not matching: "{this_str}" != "{that_str}"',
    )


def __canonicalize(an_object: Any) -> str:
    if isinstance(an_object, dict):
        return dumps(dict(sorted(an_object.items())))
    if isinstance(an_object, list):
        return dumps(sorted(an_object, key=str))
    return dumps(an_object)


def __match_objects(
    this_object: Any,
    that_object: Any,
    parents: tuple[str, ...],
) -> Error | Groups:
    # Return error if different types
    if type(this_object) != type(that_object):
        return __error(
            parents,
            str(this_object),
            str(that_object),
            f"Objects of different types: {type(this_object)}, {type(that_object)}",
        )

    # Return if as canonicalized strings and are equal or match as regexp
    if type(this_object) in (dict, list, str):
        result = __match_str(
            __canonicalize(this_object), __canonicalize(that_object), parents
        )
        if isinstance(result, Groups):
            return result

    match_function = {
        dict: __match_dict,
        list: __match_list,
        str: __match_str,
    }.get(type(this_object), __match_default)
    return match_function(this_object, that_object, parents)


def match(this: str, that: str) -> Error | Groups:
    """
    Matches this and that.
    The "this" can contain regular expressions.
    Both "this" and "that" must be valid json, if they not as a whole matches with
    re.fullmatch(f"(?ms){r}", s).
    Returns an Error or a Groups object.
    """
    if not (isinstance(this, str) and isinstance(that, str)):
        # Return error if this and that are not strings
        return __error(
            (),
            this,
            that,
            f'Values not strings: "{type(this)}" != "{type(that)}"',
        )

    # Match this and that as strings and return if Match, i.e. no Error
    result = __match_str(this, that, ())
    if isinstance(result, Groups):
        return result

    # Load to Objects
    objects = []
    for name, json in ("this", this), ("that", that):
        try:
            objects.append(loads(json))
        except JSONDecodeError as e:
            return __error((), this, that, f'Cannot load {name} "{json}": {e}')
    this_object, that_object = objects

    # Match Objects
    return __match_objects(this_object, that_object, ())
