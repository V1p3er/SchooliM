# SchooliM (Backend CLI School Management System)

Pure Python terminal backend for school management with role-based access control.

## Run

```bash
pip install -r requirements.txt
```

```bash
python main.py
```

Default login:
- `admin / admin`

## Roles

- `admin` and `manager`: full CRUD over users, subjects, enrollments, score reports.
- `teacher`: can create/update/delete subjects, assign/remove student subjects per semester, set student scores, view student reports.
- `student`: can assign/remove own subjects per semester and view own score report.

## Security

- Passwords are stored as `pbkdf2_hmac(sha256)` hashes with random salts.
- Password comparison uses constant-time `hmac.compare_digest`.
- Role authorization is enforced in service layer.

## Tests

```bash
pytest -q
```

Includes:
- unit tests
- integration tests
- end-to-end CLI test
