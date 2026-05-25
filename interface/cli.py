from domain.entitiy.user import Role, User
from services.school_service import AuthorizationError, SchoolService


def _prompt(text: str) -> str:
    return input(text).strip()


def _print_report(rows: list) -> None:
    if not rows:
        print("No records.")
        return
    for row in rows:
        score = "-" if row.score is None else f"{row.score:.2f}"
        print(f"{row.semester} | {row.subject_code} | score: {score}")


def _user_menu(service: SchoolService, actor: User) -> None:
    while True:
        print("\nUser Menu")
        print("1) Change my password")
        print("2) Logout")
        choice = _prompt("Select: ")
        if choice == "1":
            new_pass = _prompt("New password: ")
            service.update_own_password(actor, new_pass)
            print("Password updated.")
        elif choice == "2":
            return
        else:
            print("Invalid option.")


def _student_menu(service: SchoolService, actor: User) -> None:
    while True:
        print("\nStudent Menu")
        print("1) Enroll subject for semester")
        print("2) Remove subject from semester")
        print("3) View score report")
        print("4) Change my password")
        print("5) Logout")
        choice = _prompt("Select: ")
        try:
            if choice == "1":
                service.enroll_student(actor, actor.username, _prompt("Subject code: "), _prompt("Semester: "))
                print("Enrollment added.")
            elif choice == "2":
                service.unenroll_student(actor, actor.username, _prompt("Subject code: "), _prompt("Semester: "))
                print("Enrollment removed.")
            elif choice == "3":
                _print_report(service.get_score_report(actor))
            elif choice == "4":
                service.update_own_password(actor, _prompt("New password: "))
                print("Password updated.")
            elif choice == "5":
                return
            else:
                print("Invalid option.")
        except (ValueError, AuthorizationError) as exc:
            print(f"Error: {exc}")


def _teacher_menu(service: SchoolService, actor: User) -> None:
    while True:
        print("\nTeacher Menu")
        print("1) Create subject")
        print("2) Update subject")
        print("3) Delete subject")
        print("4) Enroll student")
        print("5) Remove student enrollment")
        print("6) Set student score")
        print("7) View student report")
        print("8) Change my password")
        print("9) Logout")
        choice = _prompt("Select: ")
        try:
            if choice == "1":
                service.create_subject(actor, _prompt("Code: "), _prompt("Name: "))
                print("Subject created.")
            elif choice == "2":
                service.update_subject(actor, _prompt("Code: "), _prompt("New name: "))
                print("Subject updated.")
            elif choice == "3":
                service.delete_subject(actor, _prompt("Code: "))
                print("Subject deleted.")
            elif choice == "4":
                service.enroll_student(actor, _prompt("Student username: "), _prompt("Subject code: "), _prompt("Semester: "))
                print("Enrollment added.")
            elif choice == "5":
                service.unenroll_student(actor, _prompt("Student username: "), _prompt("Subject code: "), _prompt("Semester: "))
                print("Enrollment removed.")
            elif choice == "6":
                service.set_score(actor, _prompt("Student username: "), _prompt("Subject code: "), _prompt("Semester: "), float(_prompt("Score (0-20): ")))
                print("Score saved.")
            elif choice == "7":
                _print_report(service.get_score_report(actor, _prompt("Student username: ")))
            elif choice == "8":
                service.update_own_password(actor, _prompt("New password: "))
                print("Password updated.")
            elif choice == "9":
                return
            else:
                print("Invalid option.")
        except (ValueError, AuthorizationError) as exc:
            print(f"Error: {exc}")


def _manager_menu(service: SchoolService, actor: User) -> None:
    while True:
        print("\nManager/Admin Menu")
        print("1) Create user")
        print("2) Delete user")
        print("3) List users")
        print("4) Teacher actions")
        print("5) Change my password")
        print("6) Logout")
        choice = _prompt("Select: ")
        try:
            if choice == "1":
                role_input = _prompt("Role (manager/teacher/student): ").lower()
                role = Role(role_input)
                if role == Role.ADMIN:
                    raise ValueError("Cannot create admin role from menu")
                service.create_user(actor, _prompt("Username: "), _prompt("Password: "), role)
                print("User created.")
            elif choice == "2":
                service.delete_user(actor, _prompt("Username: "))
                print("User deleted.")
            elif choice == "3":
                users = service.list_users(actor)
                for user in users:
                    print(f"{user.username} ({user.role.value})")
            elif choice == "4":
                _teacher_menu(service, actor)
            elif choice == "5":
                service.update_own_password(actor, _prompt("New password: "))
                print("Password updated.")
            elif choice == "6":
                return
            else:
                print("Invalid option.")
        except (ValueError, AuthorizationError) as exc:
            print(f"Error: {exc}")


def run_cli() -> None:
    service = SchoolService(db_path="schoolim.db")
    print("School Management CLI")
    print("Default admin login -> username: admin | password: admin")

    while True:
        print("\nMain Menu")
        print("1) Login")
        print("2) Exit")
        choice = _prompt("Select: ")
        if choice == "2":
            print("Bye.")
            return
        if choice != "1":
            print("Invalid option.")
            continue

        try:
            actor = service.login(_prompt("Username: "), _prompt("Password: "))
        except ValueError:
            print("Invalid credentials.")
            continue

        print(f"Welcome, {actor.username} ({actor.role.value})")
        if actor.role in {Role.ADMIN, Role.MANAGER}:
            _manager_menu(service, actor)
        elif actor.role == Role.TEACHER:
            _teacher_menu(service, actor)
        elif actor.role == Role.STUDENT:
            _student_menu(service, actor)
        else:
            _user_menu(service, actor)
