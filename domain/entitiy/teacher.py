from dataclasses import dataclass


@dataclass(slots=True)
class TeacherProfile:
    username: str
