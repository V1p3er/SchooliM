from interface.cli import run_cli


def test_cli_login_and_exit(capsys, monkeypatch):
    answers = iter(
        [
            "1",  # main: login
            "admin",
            "admin",
            "6",  # admin menu: logout
            "2",  # main: exit
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    run_cli()
    out = capsys.readouterr().out
    assert "School Management CLI" in out
    assert "Welcome, admin (admin)" in out
    assert "Bye." in out

