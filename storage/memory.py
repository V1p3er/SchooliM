import sqlite3
from pathlib import Path
from typing import Iterator

from domain.entitiy.enrollment import Enrollment
from domain.entitiy.subject import Subject
from domain.entitiy.user import Role, User


class _UsersTable:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def __contains__(self, username: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM users WHERE username = ? LIMIT 1", (username,))
        return cur.fetchone() is not None

    def get(self, username: str) -> User | None:
        cur = self.conn.execute(
            "SELECT username, password_hash, role FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
        if not row:
            return None
        return User(username=row[0], password_hash=row[1], role=Role(row[2]))

    def __getitem__(self, username: str) -> User:
        user = self.get(username)
        if user is None:
            raise KeyError(username)
        return user

    def __setitem__(self, username: str, user: User) -> None:
        self.conn.execute(
            """
            INSERT INTO users(username, password_hash, role)
            VALUES(?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password_hash = excluded.password_hash,
                role = excluded.role
            """,
            (username, user.password_hash, user.role.value),
        )
        self.conn.commit()

    def __delitem__(self, username: str) -> None:
        self.conn.execute("DELETE FROM users WHERE username = ?", (username,))
        self.conn.commit()

    def values(self) -> list[User]:
        cur = self.conn.execute("SELECT username, password_hash, role FROM users ORDER BY username")
        return [User(username=r[0], password_hash=r[1], role=Role(r[2])) for r in cur.fetchall()]


class _SubjectsTable:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def __contains__(self, code: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM subjects WHERE code = ? LIMIT 1", (code,))
        return cur.fetchone() is not None

    def __getitem__(self, code: str) -> Subject:
        cur = self.conn.execute("SELECT code, name FROM subjects WHERE code = ?", (code,))
        row = cur.fetchone()
        if not row:
            raise KeyError(code)
        return Subject(code=row[0], name=row[1])

    def __setitem__(self, code: str, subject: Subject) -> None:
        self.conn.execute(
            """
            INSERT INTO subjects(code, name)
            VALUES(?, ?)
            ON CONFLICT(code) DO UPDATE SET
                name = excluded.name
            """,
            (code, subject.name),
        )
        self.conn.commit()

    def __delitem__(self, code: str) -> None:
        self.conn.execute("DELETE FROM subjects WHERE code = ?", (code,))
        self.conn.commit()

    def values(self) -> list[Subject]:
        cur = self.conn.execute("SELECT code, name FROM subjects ORDER BY code")
        return [Subject(code=r[0], name=r[1]) for r in cur.fetchall()]


class _EnrollmentsTable:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def __contains__(self, key: tuple[str, str, str]) -> bool:
        student_username, subject_code, semester = key
        cur = self.conn.execute(
            """
            SELECT 1 FROM enrollments
            WHERE student_username = ? AND subject_code = ? AND semester = ?
            LIMIT 1
            """,
            (student_username, subject_code, semester),
        )
        return cur.fetchone() is not None

    def __getitem__(self, key: tuple[str, str, str]) -> Enrollment:
        student_username, subject_code, semester = key
        cur = self.conn.execute(
            """
            SELECT student_username, subject_code, semester, score
            FROM enrollments
            WHERE student_username = ? AND subject_code = ? AND semester = ?
            """,
            (student_username, subject_code, semester),
        )
        row = cur.fetchone()
        if not row:
            raise KeyError(key)
        return Enrollment(student_username=row[0], subject_code=row[1], semester=row[2], score=row[3])

    def __setitem__(self, key: tuple[str, str, str], enr: Enrollment) -> None:
        student_username, subject_code, semester = key
        self.conn.execute(
            """
            INSERT INTO enrollments(student_username, subject_code, semester, score)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(student_username, subject_code, semester) DO UPDATE SET
                score = excluded.score
            """,
            (student_username, subject_code, semester, enr.score),
        )
        self.conn.commit()

    def __delitem__(self, key: tuple[str, str, str]) -> None:
        student_username, subject_code, semester = key
        self.conn.execute(
            """
            DELETE FROM enrollments
            WHERE student_username = ? AND subject_code = ? AND semester = ?
            """,
            (student_username, subject_code, semester),
        )
        self.conn.commit()

    def __iter__(self) -> Iterator[tuple[str, str, str]]:
        cur = self.conn.execute(
            "SELECT student_username, subject_code, semester FROM enrollments ORDER BY student_username, subject_code, semester"
        )
        for row in cur.fetchall():
            yield (row[0], row[1], row[2])

    def values(self) -> list[Enrollment]:
        cur = self.conn.execute(
            "SELECT student_username, subject_code, semester, score FROM enrollments ORDER BY student_username, subject_code, semester"
        )
        return [Enrollment(student_username=r[0], subject_code=r[1], semester=r[2], score=r[3]) for r in cur.fetchall()]


class InMemorySchoolStore:
    def __init__(self, db_path: str = "schoolim.db") -> None:
        path = Path(db_path)
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self._init_schema()
        self.users = _UsersTable(self.conn)
        self.subjects = _SubjectsTable(self.conn)
        self.enrollments = _EnrollmentsTable(self.conn)

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users(
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS subjects(
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS enrollments(
                student_username TEXT NOT NULL,
                subject_code TEXT NOT NULL,
                semester TEXT NOT NULL,
                score REAL NULL,
                PRIMARY KEY(student_username, subject_code, semester),
                FOREIGN KEY(student_username) REFERENCES users(username) ON DELETE CASCADE,
                FOREIGN KEY(subject_code) REFERENCES subjects(code) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

