import logging

from rsimulator_core.regex import find_matches as regex_find_matches

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure caching on/off
CACHE = False

# Configure match functions.
# Key corresponds to core.service content_type parameter
# Value is to function to handle matching for a specific content_type
__match_functions = {
    "json": regex_find_matches,
    "txt": regex_find_matches,
    "xml": regex_find_matches,
}


def get_find_matches_function(content_type: str) -> callable:
    return __match_functions.get(content_type, regex_find_matches)
