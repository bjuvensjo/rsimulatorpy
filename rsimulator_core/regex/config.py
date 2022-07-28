from rsimulator_core.regex import json_matcher, txt_matcher, xml_matcher

# Configure match functions.
# Key corresponds to core.service content_type parameter
# Value is to function to handle matching for a specific content_type
__regex_match_functions = {
    "json": json_matcher.match,
    "txt": txt_matcher.match,
    "xml": xml_matcher.match,
}


def get_regex_match_function(content_type: str) -> callable:
    return __regex_match_functions.get(content_type, txt_matcher.match)
