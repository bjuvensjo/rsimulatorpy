import logging
import re
import xml.etree.ElementTree as ET
from glob import glob
from json import loads
from os.path import dirname, sep

log = logging.getLogger(__name__)


def find_matches(root_path, root_relative_path, request, content_type, **kwargs):
    matches = []
    normalized_request = normalize(request, content_type, False)
    for candidate_path in find(root_path, root_relative_path, content_type):
        candidate = read(candidate_path)
        match = get_match(normalize(candidate, content_type), normalized_request)
        if match:
            response_path = get_response_path(candidate_path)
            response_raw = read(response_path)
            response = replace_response(match, response_raw)
            matches.append({
                'request': request,
                'candidate_path': candidate_path,
                'candidate': candidate,
                'response_path': response_path,
                'response_raw': response_raw,
                'response': response
            })
    log.debug('Matches: %s', matches)
    return matches


def get_match(p, s):
    return re.fullmatch(rf'(?ms){p}', s)


def normalize(s, content_type, do_escape=True):
    if content_type == 'txt' or not s.strip():
        return s.strip()
    if content_type == 'json':
        return escape(loads(s), do_escape)
    if content_type == 'xml':
        root = ET.fromstring(''.join([l.strip() for l in s.split('\n')]))
        return ET.tostring(root, method='xml').decode('utf-8')
    return s


def escape(value, do_escape=True):
    elements = []
    if isinstance(value, dict):
        elements.append('\{' if do_escape else '{')
        elements.append(','.join(sorted([f'"{k}":{escape(v)}' for (k, v) in value.items()])))
        elements.append('\}' if do_escape else '}')
    if isinstance(value, list):
        elements.append('\[') if do_escape else '['
        elements.append(','.join(sorted([escape(v) for v in value])))
        elements.append('\]' if do_escape else ']')
    if isinstance(value, str):
        elements.append(f'"{value}"')
    if isinstance(value, int) or isinstance(value, float):
        elements.append(str(value))

    return ''.join(elements)


def replace_response(match, response):
    for index, val in enumerate(match.groups(), start=1):
        response = response.replace('${' + str(index) + '}', val)
    return response


def get_response_path(request_path):
    d = dirname(request_path)
    f = request_path.split(sep)[-1].replace('Request', 'Response')
    return f'{d}/{f}'


def find(root_path, root_relative_path, ending):
    return glob(f'{root_path}/{root_relative_path}/**/*Request.{ending}', recursive=True)


def read(path):
    with open(path, 'rt', encoding='utf-8') as f:
        return f.read()
