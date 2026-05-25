from dataclasses import dataclass


@dataclass(slots=True)
class Subject:
    code: str
    name: str
