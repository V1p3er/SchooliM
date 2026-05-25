from dataclasses import dataclass


@dataclass(slots=True)
class Enrollment:
    student_username: str
    subject_code: str
    semester: str
    score: float | None = None

