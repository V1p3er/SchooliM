from dataclasses import dataclass


@dataclass(slots=True)
class ScoreReportRow:
    semester: str
    subject_code: str
    score: float | None
