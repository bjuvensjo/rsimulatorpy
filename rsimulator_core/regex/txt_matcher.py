import logging
import re

from rsimulator_core.data import Error
from rsimulator_core.regex.data import Groups

log = logging.getLogger(__name__)


def match(this: str, that: str) -> Error | Groups:
    """
    Matches this and that.
    The "this" can contain regular expressions.
    Returns an Error or a Groups object.
    """
    if m := re.fullmatch(rf"(?ms){this.strip()}", that.strip()):
        return Groups(groups=tuple(m.groups()))
    else:
        return Error((), this, that, f"Values not matching: {this} != {that}")
