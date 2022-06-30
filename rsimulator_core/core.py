import logging

from rsimulator_core.data import CoreMatch, CoreNoMatch
from rsimulator_core.decorators import cache, script
from rsimulator_core.matcher import find_matches

log = logging.getLogger(__name__)


@cache
@script
def service(
    root_path: str, root_relative_path: str, request: str, content_type: str, **kwargs
) -> CoreMatch | None:
    """
    Returns first match to request recursively found in <root_path>/<root_relative_path>.
    Returns None if no match is found.
    The content_type parameter is used to
    1. Decide matcher
    2. Find only files with this extension

    All no matches are logged on debug level, including information why they not match.
    All matches are logged on debug level.
    If no match is found, it is logged on warning level.
    If more than one match is found, it is logged on warning level.
    """
    log.debug("Service called with: %s", locals())
    matches, no_matches = find_matches(
        root_path, root_relative_path, request, content_type, **kwargs
    )
    log.debug("No Matches: %s", no_matches)
    log.debug("Matches: %s", matches)
    if len(matches) == 0:
        log.warning("No candidates matches: %s", matches)
        log.debug("Returning None")
        return None
    if len(matches) > 1:
        log.warning("%d candidates matches: %s", len(matches), matches)
    log.debug("Service returning: %s", matches[0])
    return matches[0]
