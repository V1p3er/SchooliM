from domain.entitiy.user import Role
from services.school_service import SchoolService


def test_multi_role_school_flow():
    service = SchoolService()
    admin = service.login("admin", "admin")

    service.create_user(admin, "manager1", "ManagerPass123!", Role.MANAGER)
    service.create_user(admin, "teacher1", "TeacherPass123!", Role.TEACHER)
    service.create_user(admin, "student1", "StudentPass123!", Role.STUDENT)

    manager = service.login("manager1", "ManagerPass123!")
    teacher = service.login("teacher1", "TeacherPass123!")
    student = service.login("student1", "StudentPass123!")

    service.create_subject(teacher, "CHEM101", "Chemistry")
    service.enroll_student(student, "student1", "CHEM101", "1405-1")
    service.set_score(teacher, "student1", "CHEM101", "1405-1", 18)

    student_report = service.get_score_report(student)
    manager_report = service.get_score_report(manager, "student1")

    assert len(student_report) == 1
    assert student_report[0].subject_code == "CHEM101"
    assert student_report[0].score == 18.0
    assert manager_report[0].score == 18.0

