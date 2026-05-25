from dataclasses import dataclass


@dataclass(slots=True)
class StudentProfile:
    username: str
