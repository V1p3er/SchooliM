from dataclasses import replace

from domain.entitiy.enrollment import Enrollment
from domain.entitiy.subject import Subject
from domain.entitiy.user import Role, User
from domain.vo.password import Password
from domain.vo.score import Score
from domain.vo.username import UserName
from services.security import hash_password, verify_password
from storage.memory import InMemorySchoolStore


class AuthorizationError(PermissionError):
    pass


class SchoolService:
    def __init__(self, store: InMemorySchoolStore | None = None, db_path: str = ":memory:") -> None:
        self.store = store or InMemorySchoolStore(db_path=db_path)
        self._seed_default_admin()

    def _seed_default_admin(self) -> None:
        if "admin" in self.store.users:
            return
        self.store.users["admin"] = User(
            username="admin",
            password_hash=hash_password("admin"),
            role=Role.ADMIN,
        )

    def login(self, username: str, password: str) -> User:
        normalized = UserName(username)._value
        user = self.store.users.get(normalized)
        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return replace(user)

    def _must_be_manager(self, actor: User) -> None:
        if actor.role not in {Role.ADMIN, Role.MANAGER}:
            raise AuthorizationError("Only manager/admin can do this")

    def _must_be_teacher_or_manager(self, actor: User) -> None:
        if actor.role not in {Role.ADMIN, Role.MANAGER, Role.TEACHER}:
            raise AuthorizationError("Only teacher/manager/admin can do this")

    def _actor_can_touch_student(self, actor: User, student_username: str) -> None:
        if actor.role in {Role.ADMIN, Role.MANAGER, Role.TEACHER}:
            return
        if actor.role == Role.STUDENT and actor.username == student_username:
            return
        raise AuthorizationError("You are not allowed for this student")

    def create_user(self, actor: User, username: str, password: str, role: Role) -> User:
        self._must_be_manager(actor)
        normalized = UserName(username)._value
        Password(password)
        if normalized in self.store.users:
            raise ValueError("User already exists")
        user = User(normalized, hash_password(password), role)
        self.store.users[normalized] = user
        return replace(user)

    def delete_user(self, actor: User, username: str) -> None:
        self._must_be_manager(actor)
        normalized = UserName(username)._value
        if normalized == "admin":
            raise ValueError("Default admin cannot be deleted")
        if normalized not in self.store.users:
            raise ValueError("User not found")
        del self.store.users[normalized]
        to_remove = [k for k in self.store.enrollments if k[0] == normalized]
        for key in to_remove:
            del self.store.enrollments[key]

    def update_own_password(self, actor: User, new_password: str) -> None:
        Password(new_password)
        stored = self.store.users[actor.username]
        self.store.users[actor.username] = User(
            username=stored.username,
            password_hash=hash_password(new_password),
            role=stored.role,
        )

    def list_users(self, actor: User) -> list[User]:
        self._must_be_manager(actor)
        return [replace(u) for u in self.store.users.values()]

    def create_subject(self, actor: User, code: str, name: str) -> Subject:
        self._must_be_teacher_or_manager(actor)
        clean_code = code.strip().upper()
        clean_name = name.strip()
        if not clean_code or not clean_name:
            raise ValueError("Invalid subject input")
        if clean_code in self.store.subjects:
            raise ValueError("Subject already exists")
        subject = Subject(clean_code, clean_name)
        self.store.subjects[clean_code] = subject
        return replace(subject)

    def update_subject(self, actor: User, code: str, new_name: str) -> None:
        self._must_be_teacher_or_manager(actor)
        clean_code = code.strip().upper()
        if clean_code not in self.store.subjects:
            raise ValueError("Subject not found")
        self.store.subjects[clean_code] = Subject(clean_code, new_name.strip())

    def delete_subject(self, actor: User, code: str) -> None:
        self._must_be_teacher_or_manager(actor)
        clean_code = code.strip().upper()
        if clean_code not in self.store.subjects:
            raise ValueError("Subject not found")
        del self.store.subjects[clean_code]
        to_remove = [k for k in self.store.enrollments if k[1] == clean_code]
        for key in to_remove:
            del self.store.enrollments[key]

    def list_subjects(self, actor: User) -> list[Subject]:
        if actor.role not in {Role.ADMIN, Role.MANAGER, Role.TEACHER, Role.STUDENT}:
            raise AuthorizationError("Not allowed")
        return [replace(s) for s in self.store.subjects.values()]

    def enroll_student(self, actor: User, student_username: str, subject_code: str, semester: str) -> None:
        normalized_student = UserName(student_username)._value
        self._actor_can_touch_student(actor, normalized_student)
        if normalized_student not in self.store.users:
            raise ValueError("Student not found")
        if self.store.users[normalized_student].role != Role.STUDENT:
            raise ValueError("Target user is not a student")

        code = subject_code.strip().upper()
        sem = semester.strip()
        if code not in self.store.subjects:
            raise ValueError("Subject not found")
        key = (normalized_student, code, sem)
        if key in self.store.enrollments:
            raise ValueError("Enrollment already exists")
        self.store.enrollments[key] = Enrollment(normalized_student, code, sem)

    def unenroll_student(self, actor: User, student_username: str, subject_code: str, semester: str) -> None:
        normalized_student = UserName(student_username)._value
        self._actor_can_touch_student(actor, normalized_student)
        key = (normalized_student, subject_code.strip().upper(), semester.strip())
        if key not in self.store.enrollments:
            raise ValueError("Enrollment not found")
        del self.store.enrollments[key]

    def set_score(self, actor: User, student_username: str, subject_code: str, semester: str, score: float) -> None:
        self._must_be_teacher_or_manager(actor)
        normalized_student = UserName(student_username)._value
        code = subject_code.strip().upper()
        sem = semester.strip()
        key = (normalized_student, code, sem)
        if key not in self.store.enrollments:
            raise ValueError("Enrollment not found")
        clean_score = Score(score)._value
        enr = self.store.enrollments[key]
        enr.score = clean_score
        self.store.enrollments[key] = enr

    def get_score_report(self, actor: User, student_username: str | None = None) -> list[Enrollment]:
        target = UserName(student_username)._value if student_username else actor.username
        self._actor_can_touch_student(actor, target)
        rows = [replace(e) for e in self.store.enrollments.values() if e.student_username == target]
        rows.sort(key=lambda x: (x.semester, x.subject_code))
        return rows
