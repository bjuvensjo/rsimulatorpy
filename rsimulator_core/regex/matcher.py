import logging
from glob import glob
from os.path import dirname, sep

from rsimulator_core import config
from rsimulator_core.data import Error, Match, NoMatch
from rsimulator_core.regex.data import Groups

log = logging.getLogger(__name__)


def find_matches(
    root_path: str, root_relative_path: str, request: str, content_type: str
) -> tuple[tuple[Match, ...], tuple[NoMatch, ...]]:
    no_matches = []
    matches = []
    match = config.get_regex_match_function(content_type)
    for candidate_path in __find(root_path, root_relative_path, content_type):
        candidate = __read(candidate_path)
        result = match(candidate, request)
        log.debug("Match result for %s: %s", candidate_path, result)
        if isinstance(result, Error):
            no_matches.append(NoMatch(request, candidate_path, candidate, result))
        else:
            response_path = __get_response_path(candidate_path)
            response_raw = __read(response_path)
            response = __replace_response(result, response_raw)
            matches.append(
                Match(
                    request,
                    candidate_path,
                    candidate,
                    response_path,
                    response_raw,
                    response,
                )
            )
    log.debug("Matches: %s", matches)
    return tuple(matches), tuple(no_matches)


def __replace_response(result: Groups, response: str) -> str:
    for index, val in enumerate(result.groups, start=1):
        response = response.replace("${" + str(index) + "}", val)
    return response


def __get_response_path(request_path: str) -> str:
    return f'{dirname(request_path)}/{request_path.split(sep)[-1].replace("Request", "Response")}'


def __find(root_path: str, root_relative_path: str, ending: str) -> list[str]:
    return glob(
        f"{root_path}/{root_relative_path}/**/*Request.{ending}", recursive=True
    )


def __read(path: str) -> str:
    with open(path, "rt", encoding="utf-8") as f:
        return f.read()
