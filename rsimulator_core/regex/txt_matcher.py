import logging
import re

from rsimulator_core.data import Result, Error

log = logging.getLogger(__name__)


def match(
    this: str,
    that: str,
    parents=(),
) -> Result:
    """
    Matches this and that.
    The "this" can contain regular expressions.
    Returns a Result object with possible groups and/or errors
    """
    m = re.fullmatch(rf"(?ms){this.strip()}", that.strip())
    return (
        Result(groups=tuple(m.groups()))
        if m
        else Result(
            error=Error(None, None, None, f"Values not matching: {this} != {that}")
        )
    )
