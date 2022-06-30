import logging

from rsimulator_core.regex import xml_matcher, json_matcher, txt_matcher

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Configure caching on/off
CACHE = False

# Configure match functions.
# Key corresponds to core.service content_type parameter
# Value is to function to handle matching for a specific content_type
__match_functions = {
    "json": json_matcher.match,
    "txt": txt_matcher.match,
    "xml": xml_matcher.match,
}


def get_match_function(content_type: str) -> callable:
    return __match_functions.get(content_type, txt_matcher.match)
