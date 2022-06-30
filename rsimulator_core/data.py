from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Error:
    parents: Optional[tuple[str, ...]]
    this: Optional[str]
    that: Optional[str]
    message: str


@dataclass(frozen=True)
class Result:
    error: Optional[Error] = None
    groups: tuple[str, ...] = ()

    def has_error(self) -> bool:
        return self.error is not None


@dataclass(frozen=True)
class CoreMatch:
    request: str
    candidate_path: str
    candidate: str
    response_path: str
    response_raw: str
    response: str


@dataclass(frozen=True)
class CoreNoMatch:
    request: str
    candidate_path: str
    candidate: str
    result: Result


@dataclass(frozen=True)
class CoreReturn:
    coreMatch: tuple[CoreMatch] = ()
    coreNoMatch: tuple[CoreNoMatch] = ()
