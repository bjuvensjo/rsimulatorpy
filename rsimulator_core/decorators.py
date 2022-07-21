import functools
import logging
import re
from functools import wraps
from os.path import exists

from rsimulator_core.config import CACHE

log = logging.getLogger(__name__)


def cache(f):
    @wraps(f)
    @functools.lru_cache(maxsize=1000, typed=False)
    def cache_decorator(*args, **kwargs):
        return f(*args, **kwargs)

    return cache_decorator if CACHE else f


def __execute(script_path, args, kwargs):
    if exists(script_path):
        log.debug("Before executing script %s: %s, %s", script_path, args, kwargs)
        with open(script_path, "rt", encoding="utf-8") as s:
            c = s.read()
            exec(c, {}, {"args": args, "kwargs": kwargs})
            log.debug("After executing script %s: %s, %s", script_path, args, kwargs)
    else:
        log.debug("Script %s does not exist: %s, %s", script_path, args, kwargs)


def script(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        kws = kwargs if kwargs else {}

        # Global request
        __execute(f"{args[0]}/global_request.py", args, kws)
        if "response" in kws:
            return kws["response"]

        # Call
        response = f(*args, **kwargs)
        kws["response"] = response

        if response:
            # local response
            __execute(
                re.sub(r"Request.[a-z]+", ".py", response.candidate_path), args, kws
            )
            # Global response
            __execute(f"{args[0]}/global_response.py", args, kws)
        return kws["response"]

    return decorator
