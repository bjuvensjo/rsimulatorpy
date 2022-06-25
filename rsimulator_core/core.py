import logging

from rsimulator_core.decorator import cache, script
from rsimulator_core.matcher import find_matches

log = logging.getLogger(__name__)


@cache
@script
def service(root_path, root_relative_path, request, content_type, **kwargs):
    log.debug('Service called with: %s', locals())
    matches = find_matches(root_path, root_relative_path, request, content_type, **kwargs)
    if len(matches) == 0:
        log.warning('No candidates matches %s', matches)
        return
    if len(matches) > 1:
        log.warning('%d candidates matches %s', len(matches), matches)
    log.debug('Service returning: %s', matches[0])
    return matches[0]
