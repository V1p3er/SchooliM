from dataclasses import dataclass
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    TEACHER = "teacher"
    STUDENT = "student"


@dataclass(slots=True)
class User:
    username: str
    password_hash: str
    role: Role

