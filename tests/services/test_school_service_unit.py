import pytest

from domain.entitiy.user import Role
from services.school_service import AuthorizationError, SchoolService


def _setup_manager_and_student(service: SchoolService):
    admin = service.login("admin", "admin")
    service.create_user(admin, "manager1", "ManagerPass123!", Role.MANAGER)
    service.create_user(admin, "student1", "StudentPass123!", Role.STUDENT)
    return service.login("manager1", "ManagerPass123!"), service.login("student1", "StudentPass123!")


def test_default_admin_login_works():
    service = SchoolService()
    actor = service.login("admin", "admin")
    assert actor.username == "admin"
    assert actor.role == Role.ADMIN


def test_student_cannot_create_user():
    service = SchoolService()
    _, student = _setup_manager_and_student(service)
    with pytest.raises(AuthorizationError):
        service.create_user(student, "xuser", "StrongPass123!", Role.STUDENT)


def test_student_can_only_enroll_self():
    service = SchoolService()
    manager, student = _setup_manager_and_student(service)
    service.create_user(manager, "student2", "StudentPass222!", Role.STUDENT)
    service.create_subject(manager, "MATH101", "Math")

    with pytest.raises(AuthorizationError):
        service.enroll_student(student, "student2", "MATH101", "1405-1")


def test_teacher_can_set_score():
    service = SchoolService()
    admin = service.login("admin", "admin")
    service.create_user(admin, "teacher1", "TeacherPass123!", Role.TEACHER)
    service.create_user(admin, "student1", "StudentPass123!", Role.STUDENT)
    teacher = service.login("teacher1", "TeacherPass123!")
    service.create_subject(teacher, "PHY101", "Physics")
    service.enroll_student(teacher, "student1", "PHY101", "1405-1")
    service.set_score(teacher, "student1", "PHY101", "1405-1", 19.5)

    report = service.get_score_report(teacher, "student1")
    assert len(report) == 1
    assert report[0].score == 19.5


def test_update_own_password_changes_login():
    service = SchoolService()
    admin = service.login("admin", "admin")
    service.update_own_password(admin, "NewAdminPass123!")
    with pytest.raises(ValueError):
        service.login("admin", "admin")
    assert service.login("admin", "NewAdminPass123!").username == "admin"

