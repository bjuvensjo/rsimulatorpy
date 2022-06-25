#!/usr/bin/env python3
import logging
import sys

from flask import Flask, abort
from flask import request

import rsimulator_core.core as core
import rsimulator_http.config as cfg

app = Flask(__name__)


def get_log():
    log_formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    the_log = logging.getLogger()
    the_log.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    the_log.addHandler(console_handler)

    return the_log


log = get_log()


def get_content_type(content_type=''):
    if 'json' in content_type:
        return 'json'
    if 'xml' in content_type:
        return 'xml'
    return 'txt'


def get_content_encoding(content_type=''):
    split = content_type.split(';')
    if len(split) == 2:
        return split[1].split('=')[1]
    return 'utf-8'


@app.route('/', defaults={'root_relative_path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:root_relative_path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def service(root_relative_path):
    core_response = core.service(cfg.ROOT_PATH,
                                 root_relative_path,
                                 request.data.decode(get_content_encoding(request.content_type)),
                                 get_content_type(request.content_type))
    if core_response:
        return core_response['response']
    else:
        abort(404)


if __name__ == '__main__':
    app.run()
