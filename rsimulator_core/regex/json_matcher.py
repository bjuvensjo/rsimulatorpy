import logging
import re
from json import loads, dumps
from json.decoder import JSONDecodeError
from typing import Optional, Any

from rsimulator_core.data import Result, Error

log = logging.getLogger(__name__)


def __error(
    parents: Optional[tuple[str, ...]],
    this_str: Optional[str],
    that_str: Optional[str],
    message: str,
) -> Result:
    return Result(error=Error(parents, this_str, that_str, message))


def __match_default(this_value, that_value, parents: tuple[str, ...]) -> Result:
    return (
        Result()
        if this_value == that_value
        else __error(
            parents,
            None,
            None,
            f'Values not matching: "{this_value}" != "{that_value}"',
        )
    )


def __match_dict(this_dict: dict, that_dict: dict, parents: tuple[str, ...]) -> Result:
    if len(this_dict) != len(that_dict):
        return __error(parents, None, None, "Different number of keys")
    groups = tuple()
    this_sorted = dict(sorted(this_dict.items()))
    that_sorted = dict(sorted(that_dict.items()))
    for this_child, that_child in zip(this_sorted.items(), that_sorted.items()):
        this_child_key, this_child_value = this_child
        that_child_key, that_child_value = that_child
        if this_child_key != that_child_key:
            return __error(
                parents,
                this_child_key,
                that_child_key,
                f'Keys not matching: "{this_child_key}" != "{that_child_key}"',
            )
        child_result = __match_objects(
            this_child_value, that_child_value, parents + (this_child_key,)
        )
        if child_result.has_error():
            if child_result.error.this is None:
                return __error(
                    parents, this_child_key, that_child_key, child_result.error.message
                )
            else:
                return child_result
        else:
            groups += child_result.groups
    return Result(groups=groups)


def __match_list(this_list: list, that_list: list, parents: tuple[str, ...]) -> Result:
    if len(this_list) != len(that_list):
        return __error(parents, None, None, "Different length of lists")
    groups = tuple()
    this_sorted = sorted(this_list, key=str)
    that_sorted = sorted(that_list, key=str)
    for this_child, that_child in zip(this_sorted, that_sorted):
        child_result = __match_objects(this_child, that_child, parents)
        if child_result.has_error():
            return child_result
        else:
            groups += child_result.groups
    return Result(groups=groups)


def __match_str(this_str: str, that_str: str, parents: tuple[str, ...]) -> Result:
    if this_str == that_str:
        return Result()
    m = re.fullmatch(f"(?ms){this_str}", that_str)
    if m:
        return Result(groups=tuple(m.groups()))
    return __error(
        parents, None, None, f'Values not matching: "{this_str}" != "{that_str}"'
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
) -> Result:
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
        if not result.has_error():
            return result

    return {dict: __match_dict, list: __match_list, str: __match_str}.get(
        type(this_object), __match_default
    )(this_object, that_object, parents)


def match(this: str, that: str) -> Result:
    """
    Matches this and that.
    The "this" can contain regular expressions.
    Both "this" and "that" must be valid json, if they not as a whole matches with
    re.fullmatch(f"(?ms){r}", s).
    Returns a Result object with possible groups and/or errors
    """
    if not (isinstance(this, str) and isinstance(that, str)):
        # Return error if this and that are not strings
        return __error(
            (),
            this,
            that,
            f'Values not strings: "{type(this)}" != "{type(that)}"',
        )

    # Match this and that as strings and return if result is a match, i.e. has no error
    result = __match_str(this, that, ())
    if not result.has_error():
        return result

    # Load to Objects
    objects = []
    for name, json in ("this", this), ("that", that):
        try:
            objects.append(loads(json))
        except JSONDecodeError as e:
            return __error(None, None, None, f'Cannot load {name} "{json}": {e}')
    this_object, that_object = objects

    # Match Objects
    return __match_objects(this_object, that_object, ())
