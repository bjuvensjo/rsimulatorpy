from dataclasses import dataclass


@dataclass(frozen=True)
class Groups:
    groups: tuple[str, ...] = ()
