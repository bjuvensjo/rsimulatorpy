from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Error:
    path: tuple[Any, ...] | None
    this: Any | None
    that: Any | None
    message: str


@dataclass(frozen=True)
class Match:
    request: str
    candidate_path: str
    candidate: str
    response_path: str
    response_raw: str
    response: str


@dataclass(frozen=True)
class NoMatch:
    request: str
    candidate_path: str
    candidate: str
    error: Error
